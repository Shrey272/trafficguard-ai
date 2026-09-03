import threading
import time
import random
import logging
from datetime import datetime
from typing import Optional, Any, Dict
from app.camera.base_adapter import BaseCameraAdapter

logger = logging.getLogger(__name__)

# Optional OpenCV import with fallback
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    cv2 = None
    np = None

class RTSPCameraAdapter(BaseCameraAdapter):
    """
    Production-grade RTSP Camera Adapter.
    Uses OpenCV VideoCapture in a background worker thread with automatic backoff reconnection,
    frame timeout detection, and complete fault isolation.
    """
    def __init__(
        self,
        camera_id: str,
        camera_code: str,
        rtsp_url: Optional[str] = None,
        source_type: str = "RTSP",
        timeout_seconds: float = 6.0,
        max_reconnect_delay: float = 30.0
    ):
        super().__init__(camera_id=camera_id, camera_code=camera_code, source_type=source_type)
        self.rtsp_url = rtsp_url or ""
        self.timeout_seconds = timeout_seconds
        self.max_reconnect_delay = max_reconnect_delay
        
        self._cap = None
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._latest_frame: Optional[Any] = None
        self._frame_count = 0
        self._fps_timer = time.time()
        self._consecutive_failures = 0
        self._is_connected_flag = False

    def connect(self) -> bool:
        if self._running:
            return True
            
        self.status = "CONNECTING"
        self.error_message = None
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._stream_worker,
            name=f"CameraThread-{self.camera_code}",
            daemon=True
        )
        self._worker_thread.start()
        return True

    def disconnect(self) -> bool:
        self._running = False
        self.status = "OFFLINE"
        self._is_connected_flag = False
        self._release_resources()
        if self._worker_thread and self._worker_thread.is_alive():
            try:
                self._worker_thread.join(timeout=1.0)
            except Exception:
                pass
        self._worker_thread = None
        self.fps = 0.0
        return True

    def reconnect(self) -> bool:
        self._release_resources()
        self.status = "CONNECTING"
        self.reconnect_attempts += 1
        return self._open_stream()

    def is_connected(self) -> bool:
        return self._is_connected_flag and self.status == "ONLINE"

    def read_frame(self) -> Optional[Any]:
        with self._lock:
            return self._latest_frame

    def _open_stream(self) -> bool:
        # Check for MOCK or empty RTSP URL
        if self.source_type == "MOCK" or not self.rtsp_url or self.rtsp_url.startswith("mock://") or "dummy" in self.rtsp_url:
            self.status = "ONLINE"
            self._is_connected_flag = True
            self.start_time = datetime.utcnow()
            self.error_message = None
            return True

        if not HAS_OPENCV:
            self.status = "ERROR"
            self.error_message = "OpenCV is not available in backend environment"
            self._is_connected_flag = False
            return False

        # Validate URL format
        if not (self.rtsp_url.startswith("rtsp://") or self.rtsp_url.startswith("rtsps://") or self.rtsp_url.startswith("http://") or self.rtsp_url.startswith("https://")):
            self.status = "ERROR"
            self.error_message = f"Invalid RTSP URL format: {self.rtsp_url[:15]}..."
            self._is_connected_flag = False
            return False

        try:
            start_t = time.time()
            # Initialize VideoCapture
            self._cap = cv2.VideoCapture(self.rtsp_url)
            # Set buffer size to 1 frame to reduce latency
            self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not self._cap.isOpened():
                self.status = "ERROR"
                self.error_message = "Failed to open RTSP stream (Auth failure or host unreachable)"
                self._is_connected_flag = False
                return False

            self.latency_ms = (time.time() - start_t) * 1000
            self.status = "ONLINE"
            self._is_connected_flag = True
            self.start_time = datetime.utcnow()
            self.error_message = None
            self._consecutive_failures = 0
            return True
        except Exception as e:
            self.status = "ERROR"
            self.error_message = f"RTSP Connection Exception: {str(e)}"
            self._is_connected_flag = False
            self._release_resources()
            return False

    def _release_resources(self):
        try:
            if self._cap is not None:
                self._cap.release()
        except Exception as e:
            logger.debug(f"Error releasing VideoCapture for {self.camera_code}: {e}")
        finally:
            self._cap = None

    def _generate_mock_frame(self):
        """Generates a synthetic test frame for mock/offline fallback."""
        if HAS_OPENCV and np is not None:
            # Create a 640x360 frame
            frame = np.zeros((360, 640, 3), dtype=np.uint8)
            # Add timestamp and camera metadata
            ts_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            cv2.putText(frame, f"CAM: {self.camera_code}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 200), 2)
            cv2.putText(frame, ts_str, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"STATUS: {self.status} | FPS: {self.fps:.1f}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            # Draw synthetic vehicles / bounding boxes
            t = time.time()
            x = int(100 + (t * 50) % 400)
            cv2.rectangle(frame, (x, 180), (x + 80, 240), (0, 200, 255), 2)
            cv2.putText(frame, "VEHICLE", (x, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
            return frame
        return None

    def _stream_worker(self):
        """Continuous background frame ingestion loop with fault isolation."""
        self._open_stream()
        
        while self._running:
            try:
                if not self._is_connected_flag or self.status != "ONLINE":
                    # Backoff calculation
                    delay = min(2.0 * (1.5 ** min(self._consecutive_failures, 6)), self.max_reconnect_delay)
                    delay += random.uniform(0.1, 1.0)
                    time.sleep(delay)
                    
                    if not self._running:
                        break
                    
                    self.reconnect()
                    if not self._is_connected_flag:
                        self._consecutive_failures += 1
                        continue

                # Stream is online, read frames
                if self.source_type == "MOCK" or self._cap is None:
                    # Synthetic streaming
                    time.sleep(1.0 / 15.0)  # ~15 FPS
                    frame = self._generate_mock_frame()
                    with self._lock:
                        self._latest_frame = frame
                    self.last_frame_time = datetime.utcnow()
                    self._update_fps()
                else:
                    # Real RTSP stream read
                    ret, frame = self._cap.read()
                    if ret and frame is not None:
                        with self._lock:
                            self._latest_frame = frame
                        self.last_frame_time = datetime.utcnow()
                        self._consecutive_failures = 0
                        self._update_fps()
                    else:
                        # Failed to read frame
                        self._consecutive_failures += 1
                        if self._consecutive_failures > 5:
                            logger.warning(f"Frame timeout for camera {self.camera_code}. Triggering reconnect...")
                            self.status = "ERROR"
                            self.error_message = "Stream interrupted / frame timeout"
                            self._is_connected_flag = False
                        time.sleep(0.05)

            except Exception as ex:
                logger.error(f"Isolated exception in camera worker {self.camera_code}: {ex}", exc_info=False)
                self.status = "ERROR"
                self.error_message = f"Stream Worker Error: {str(ex)}"
                self._is_connected_flag = False
                self._consecutive_failures += 1
                time.sleep(1.0)

        self._release_resources()

    def _update_fps(self):
        self._frame_count += 1
        now = time.time()
        elapsed = now - self._fps_timer
        if elapsed >= 1.0:
            self.fps = self._frame_count / elapsed
            self._frame_count = 0
            self._fps_timer = now
