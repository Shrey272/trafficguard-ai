import os
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Any, Dict
from app.camera.base_adapter import BaseCameraAdapter

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    cv2 = None
    np = None

class VideoFileAdapter(BaseCameraAdapter):
    """
    Video File Adapter for testing, benchmarking, and offline simulation.
    Loops MP4/AVI/MKV video files continuously with accurate frame rate pacing.
    """
    def __init__(
        self,
        camera_id: str,
        camera_code: str,
        video_file_path: Optional[str] = None,
        source_type: str = "FILE",
        target_fps: float = 25.0
    ):
        super().__init__(
            camera_id=camera_id,
            camera_code=camera_code,
            source_type=source_type,
            has_ptz=False,
            capabilities="STREAMING,FILE_PLAYBACK,LOOP"
        )
        self.video_file_path = video_file_path or ""
        self.target_fps = target_fps
        
        self._cap = None
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._latest_frame: Optional[Any] = None
        self._is_connected_flag = False

    def connect(self) -> bool:
        if self._running:
            return True
        self.status = "ONLINE"
        self._is_connected_flag = True
        self.start_time = datetime.now()
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._file_worker,
            name=f"FileThread-{self.camera_code}",
            daemon=True
        )
        self._worker_thread.start()
        return True

    def disconnect(self) -> bool:
        self._running = False
        self.status = "OFFLINE"
        self._is_connected_flag = False
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        if self._worker_thread and self._worker_thread.is_alive():
            try:
                self._worker_thread.join(timeout=1.0)
            except Exception:
                pass
        self._worker_thread = None
        self.fps = 0.0
        return True

    def is_connected(self) -> bool:
        return self._is_connected_flag and self.status == "ONLINE"

    def read_frame(self) -> Optional[Any]:
        with self._lock:
            return self._latest_frame

    def reconnect(self) -> bool:
        self.disconnect()
        return self.connect()

    def _file_worker(self):
        file_exists = self.video_file_path and os.path.exists(self.video_file_path)
        
        if file_exists and HAS_OPENCV:
            try:
                self._cap = cv2.VideoCapture(self.video_file_path)
                if self._cap.isOpened():
                    self.status = "ONLINE"
                    self._is_connected_flag = True
                    self.start_time = datetime.utcnow()
                    fps_val = self._cap.get(cv2.CAP_PROP_FPS)
                    if fps_val > 0:
                        self.target_fps = fps_val
            except Exception as e:
                logger.error(f"Error opening video file {self.video_file_path}: {e}")
                self.status = "ERROR"
                self.error_message = str(e)

        if not self._is_connected_flag:
            # Fallback to synthetic loop if file not on disk
            self.status = "ONLINE"
            self._is_connected_flag = True
            self.start_time = datetime.utcnow()

        frame_interval = 1.0 / max(self.target_fps, 1.0)
        
        while self._running:
            start_t = time.time()
            try:
                if self._cap is not None and self._cap.isOpened():
                    ret, frame = self._cap.read()
                    if not ret or frame is None:
                        # End of file reached -> Loop back to start
                        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = self._cap.read()

                    if ret and frame is not None:
                        with self._lock:
                            self._latest_frame = frame
                        self.last_frame_time = datetime.utcnow()
                        self.fps = self.target_fps
                else:
                    # Generate synthetic benchmark frame
                    frame = self._generate_synthetic_file_frame()
                    with self._lock:
                        self._latest_frame = frame
                    self.last_frame_time = datetime.utcnow()
                    self.fps = self.target_fps

            except Exception as ex:
                logger.error(f"Error in VideoFileAdapter {self.camera_code}: {ex}")
                self.status = "ERROR"
                self.error_message = str(ex)

            elapsed = time.time() - start_t
            sleep_time = max(0.0, frame_interval - elapsed)
            time.sleep(sleep_time)

    def _generate_synthetic_file_frame(self):
        if HAS_OPENCV and np is not None:
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f"FILE LOOP: {self.camera_code}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 180, 0), 2)
            cv2.putText(frame, f"PATH: {os.path.basename(self.video_file_path or 'synthetic.mp4')}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(frame, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            # Simulated vehicle bounding box
            x = int(50 + (time.time() * 60) % 450)
            cv2.rectangle(frame, (x, 180), (x + 100, 260), (0, 255, 128), 2)
            cv2.putText(frame, "TRACKED_VEHICLE #104", (x, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 128), 1)
            return frame
        return None
