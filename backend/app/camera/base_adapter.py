from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

class BaseCameraAdapter(ABC):
    """
    Normalized camera adapter interface for TrafficGuard AI.
    All camera protocols (RTSP, ONVIF, Local File, USB Webcam, Enterprise VMS, Vendor SDK)
    implement this base contract.
    """
    def __init__(
        self,
        camera_id: str,
        camera_code: str,
        source_type: str = "RTSP",
        has_ptz: bool = False,
        capabilities: Optional[str] = "STREAMING"
    ):
        self.camera_id = camera_id
        self.camera_code = camera_code
        self.source_type = source_type
        self.has_ptz = has_ptz
        self.capabilities = capabilities or "STREAMING"
        
        self.status = "OFFLINE"  # ONLINE, OFFLINE, CONNECTING, ERROR, DISABLED
        self.last_frame_time: Optional[datetime] = None
        self.start_time: Optional[datetime] = None
        self.fps: float = 0.0
        self.reconnect_attempts: int = 0
        self.error_message: Optional[str] = None
        self.latency_ms: float = 0.0
        self.active_profile: Optional[str] = None

    @abstractmethod
    def connect(self) -> bool:
        """Establishes video stream connection."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Safely tears down connection and releases video capture resources."""
        pass

    @abstractmethod
    def read_frame(self) -> Optional[Any]:
        """Returns the most recent decoded video frame (numpy.ndarray), or None."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Returns True if the camera stream is actively receiving frames."""
        pass

    @abstractmethod
    def reconnect(self) -> bool:
        """Attempts to reconnect using backoff strategy."""
        pass

    def ptz_move(self, pan: float, tilt: float, zoom: float, speed: float = 0.5) -> bool:
        """Performs PTZ movement if supported by the camera adapter."""
        if not self.has_ptz:
            return False
        return True

    def get_health(self) -> Dict[str, Any]:
        """Returns current health and capability telemetry."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds() if (self.start_time and self.is_connected()) else 0.0
        return {
            "camera_id": self.camera_id,
            "camera_code": self.camera_code,
            "source_type": self.source_type,
            "status": self.status,
            "is_connected": self.is_connected(),
            "fps": round(self.fps, 1),
            "uptime_seconds": round(uptime, 1),
            "error_message": self.error_message,
            "latency_ms": round(self.latency_ms, 1),
            "last_frame_time": self.last_frame_time,
            "reconnect_attempts": self.reconnect_attempts,
            "has_ptz": self.has_ptz,
            "capabilities": self.capabilities,
            "active_profile": self.active_profile
        }
