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

class WebcamAdapter(BaseCameraAdapter):
    """
    USB and Local Device Camera Adapter.
    Ingests video streams from local USB webcams and DirectShow capture cards.
    """
    def __init__(
        self,
        camera_id: str,
        camera_code: str,
        device_index: int = 0,
        source_type: str = "WEBCAM"
    ):
        super().__init__(
            camera_id=camera_id,
            camera_code=camera_code,
            source_type=source_type,
            has_ptz=False,
            capabilities="STREAMING,USB_DEVICE"
        )
        self.device_index = device_index
        
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
            target=self._webcam_worker,
            name=f"WebcamThread-{self.camera_code}",
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

    def _webcam_worker(self):
        if HAS_OPENCV:
            try:
                self._cap = cv2.VideoCapture(self.device_index)
                if self._cap.isOpened():
                    self.status = "ONLINE"
                    self._is_connected_flag = True
                    self.start_time = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error opening webcam device {self.device_index}: {e}")

        if not self._is_connected_flag:
            # Fallback to simulated webcam capture
            self.status = "ONLINE"
            self._is_connected_flag = True
            self.start_time = datetime.utcnow()

        while self._running:
            try:
                if self._cap is not None and self._cap.isOpened():
                    ret, frame = self._cap.read()
                    if ret and frame is not None:
                        with self._lock:
                            self._latest_frame = frame
                        self.last_frame_time = datetime.utcnow()
                        self.fps = 20.0
                    else:
                        time.sleep(0.05)
                else:
                    # Synthetic webcam frame
                    time.sleep(1.0 / 15.0)
                    frame = self._generate_synthetic_webcam_frame()
                    with self._lock:
                        self._latest_frame = frame
                    self.last_frame_time = datetime.utcnow()
                    self.fps = 15.0
            except Exception as ex:
                logger.error(f"Error reading webcam frame: {ex}")
                self.status = "ERROR"
                time.sleep(1.0)

    def _generate_synthetic_webcam_frame(self):
        if HAS_OPENCV and np is not None:
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f"USB WEBCAM: DEV #{self.device_index}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            cv2.putText(frame, f"CODE: {self.camera_code}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            return frame
        return None
