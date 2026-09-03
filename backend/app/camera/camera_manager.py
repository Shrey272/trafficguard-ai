import logging
import threading
import time
from typing import Dict, Optional, Any, Callable, List
from sqlalchemy.orm import Session
from app.models.camera import Camera
from app.camera.base_adapter import BaseCameraAdapter
from app.camera.adapter_factory import AdapterFactory
from app.database.connection import SessionLocal

logger = logging.getLogger(__name__)

class CameraManager:
    """
    Central Camera Stream Manager for TrafficGuard AI.
    Normalizes camera stream management across ONVIF, RTSP, Video files, USB hardware, and VMS gateways.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CameraManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.adapters: Dict[str, BaseCameraAdapter] = {}
        self.ai_sinks: List[Callable[[str, Any], None]] = []
        self._dispatch_running = False
        self._dispatch_thread: Optional[threading.Thread] = None

    def register_ai_sink(self, callback: Callable[[str, Any], None]):
        """Registers a frame sink function (e.g., YOLO/ByteTrack AI pipeline)."""
        if callback not in self.ai_sinks:
            self.ai_sinks.append(callback)
            logger.info("Registered AI frame sink.")

    def start_camera(self, camera_id: str, credentials: Optional[Dict[str, str]] = None, db: Optional[Session] = None) -> bool:
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            cam = db.query(Camera).filter(Camera.id == camera_id).first()
            if not cam:
                logger.warning(f"Camera {camera_id} not found in DB")
                return False

            if not cam.enabled or cam.status == "DISABLED":
                logger.info(f"Camera {camera_id} is disabled; enabling it")
                cam.enabled = True
                cam.status = "CONNECTING"
                db.commit()

            adapter = self.adapters.get(camera_id)
            if adapter is None:
                adapter = AdapterFactory.create_adapter(cam, credentials=credentials)
                self.adapters[camera_id] = adapter

            adapter.connect()
            cam.status = adapter.status
            db.commit()
            return True
        finally:
            if should_close:
                db.close()

    def stop_camera(self, camera_id: str, db: Optional[Session] = None) -> bool:
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            adapter = self.adapters.get(camera_id)
            if adapter:
                adapter.disconnect()

            cam = db.query(Camera).filter(Camera.id == camera_id).first()
            if cam:
                cam.status = "OFFLINE"
                db.commit()
            return True
        finally:
            if should_close:
                db.close()

    def restart_camera(self, camera_id: str, credentials: Optional[Dict[str, str]] = None, db: Optional[Session] = None) -> bool:
        self.stop_camera(camera_id, db=db)
        time.sleep(0.5)
        return self.start_camera(camera_id, credentials=credentials, db=db)

    def remove_camera(self, camera_id: str):
        adapter = self.adapters.pop(camera_id, None)
        if adapter:
            adapter.disconnect()

    def get_adapter(self, camera_id: str) -> Optional[BaseCameraAdapter]:
        return self.adapters.get(camera_id)

    def get_camera_health(self, camera_id: str) -> Optional[Dict[str, Any]]:
        adapter = self.adapters.get(camera_id)
        if adapter:
            return adapter.get_health()
        return None

    def get_all_health(self) -> Dict[str, Dict[str, Any]]:
        return {cam_id: adapter.get_health() for cam_id, adapter in self.adapters.items()}

    def execute_ptz(self, camera_id: str, pan: float, tilt: float, zoom: float, speed: float = 0.5) -> bool:
        adapter = self.adapters.get(camera_id)
        if adapter and adapter.has_ptz:
            return adapter.ptz_move(pan, tilt, zoom, speed)
        return False

    def initialize_all(self, db: Optional[Session] = None):
        """Initializes all enabled cameras from DB into active normalized adapters."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            cameras = db.query(Camera).filter(Camera.enabled == True).all()
            for cam in cameras:
                if cam.status != "DISABLED":
                    adapter = AdapterFactory.create_adapter(cam)
                    self.adapters[cam.id] = adapter
                    adapter.connect()
                    cam.status = adapter.status
            db.commit()
            logger.info(f"Initialized {len(self.adapters)} normalized camera adapters via AdapterFactory.")
            self._start_frame_dispatcher()
        finally:
            if should_close:
                db.close()

    def _start_frame_dispatcher(self):
        if self._dispatch_running:
            return
        self._dispatch_running = True
        self._dispatch_thread = threading.Thread(
            target=self._dispatch_loop,
            name="CameraManager-AIDispatcher",
            daemon=True
        )
        self._dispatch_thread.start()

    def _dispatch_loop(self):
        """Dispatches latest decoded frames to registered AI frame sinks (YOLO/ByteTrack)."""
        while self._dispatch_running:
            try:
                if not self.ai_sinks:
                    time.sleep(0.5)
                    continue

                for cam_id, adapter in list(self.adapters.items()):
                    if adapter.is_connected():
                        frame = adapter.read_frame()
                        if frame is not None:
                            for sink in self.ai_sinks:
                                try:
                                    sink(cam_id, frame)
                                except Exception as e:
                                    logger.error(f"Error in AI frame sink for camera {cam_id}: {e}")
                time.sleep(1.0 / 10.0)  # Rate limit AI sampling ~10 FPS
            except Exception as ex:
                logger.error(f"Error in frame dispatch loop: {ex}")
                time.sleep(1.0)

    def shutdown(self):
        self._dispatch_running = False
        for cam_id, adapter in list(self.adapters.items()):
            try:
                adapter.disconnect()
            except Exception:
                pass
        self.adapters.clear()

camera_manager = CameraManager()
