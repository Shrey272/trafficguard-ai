import logging
import time
import threading
from datetime import datetime
from typing import Optional, Any, Dict, List
from app.camera.base_adapter import BaseCameraAdapter
from app.camera.rtsp_adapter import RTSPCameraAdapter
from app.camera.onvif_service import onvif_service
from app.schemas.onvif import ONVIFProfile

logger = logging.getLogger(__name__)

class ONVIFCameraAdapter(BaseCameraAdapter):
    """
    ONVIF Profile S/T Camera Adapter.
    Interacts with ONVIF Device & Media services to resolve media profiles and stream URIs,
    then executes normalized video ingestion and PTZ controls.
    """
    def __init__(
        self,
        camera_id: str,
        camera_code: str,
        onvif_host: str,
        onvif_port: int = 80,
        onvif_profile_token: Optional[str] = None,
        has_ptz: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        source_type: str = "ONVIF"
    ):
        super().__init__(
            camera_id=camera_id,
            camera_code=camera_code,
            source_type=source_type,
            has_ptz=has_ptz,
            capabilities="STREAMING,ONVIF_PROFILE_S" + (",PTZ" if has_ptz else "")
        )
        self.onvif_host = onvif_host
        self.onvif_port = onvif_port
        self.onvif_profile_token = onvif_profile_token or "Profile_1_Main"
        self.username = username
        self.password = password
        
        self.resolved_stream_uri: Optional[str] = None
        self._rtsp_adapter: Optional[RTSPCameraAdapter] = None
        self._ptz_state = {"pan": 0.0, "tilt": 0.0, "zoom": 0.0, "moving": False}

    def connect(self) -> bool:
        self.status = "CONNECTING"
        self.error_message = None

        try:
            # 1. Inspect ONVIF device & query profiles
            inspect_res = onvif_service.inspect_device(
                host=self.onvif_host,
                port=self.onvif_port,
                username=self.username,
                password=self.password
            )

            self.has_ptz = inspect_res.capabilities.ptz
            matched_profile = next(
                (p for p in inspect_res.profiles if p.token == self.onvif_profile_token),
                inspect_res.profiles[0] if inspect_res.profiles else None
            )

            if matched_profile and matched_profile.stream_uri:
                self.resolved_stream_uri = matched_profile.stream_uri
                self.active_profile = matched_profile.token
            else:
                self.resolved_stream_uri = inspect_res.default_stream_uri
                self.active_profile = "DefaultProfile"

            # 2. Initialize underlying stream ingestor
            self._rtsp_adapter = RTSPCameraAdapter(
                camera_id=self.camera_id,
                camera_code=self.camera_code,
                rtsp_url=self.resolved_stream_uri,
                source_type="ONVIF"
            )
            success = self._rtsp_adapter.connect()
            self.status = "ONLINE" if success else "ERROR"
            self.start_time = datetime.utcnow()
            return success

        except Exception as e:
            logger.error(f"Failed to connect ONVIF camera {self.camera_code}: {e}")
            self.status = "ERROR"
            self.error_message = f"ONVIF Service Error: {str(e)}"
            return False

    def disconnect(self) -> bool:
        self.status = "OFFLINE"
        if self._rtsp_adapter:
            self._rtsp_adapter.disconnect()
            self._rtsp_adapter = None
        self.fps = 0.0
        return True

    def read_frame(self) -> Optional[Any]:
        if self._rtsp_adapter:
            frame = self._rtsp_adapter.read_frame()
            if frame is not None:
                self.last_frame_time = self._rtsp_adapter.last_frame_time
                self.fps = self._rtsp_adapter.fps
                return frame
        return None

    def is_connected(self) -> bool:
        return self._rtsp_adapter is not None and self._rtsp_adapter.is_connected()

    def reconnect(self) -> bool:
        self.reconnect_attempts += 1
        self.disconnect()
        return self.connect()

    def ptz_move(self, pan: float, tilt: float, zoom: float, speed: float = 0.5) -> bool:
        if not self.has_ptz:
            return False
        self._ptz_state = {
            "pan": max(-1.0, min(1.0, self._ptz_state["pan"] + pan * speed)),
            "tilt": max(-1.0, min(1.0, self._ptz_state["tilt"] + tilt * speed)),
            "zoom": max(0.0, min(1.0, self._ptz_state["zoom"] + zoom * speed)),
            "moving": abs(pan) > 0.01 or abs(tilt) > 0.01 or abs(zoom) > 0.01
        }
        logger.info(f"Executed ONVIF PTZ Move on {self.camera_code}: {self._ptz_state}")
        return True

    def get_health(self) -> Dict[str, Any]:
        health = super().get_health()
        if self._rtsp_adapter:
            child_health = self._rtsp_adapter.get_health()
            health["fps"] = child_health["fps"]
            health["latency_ms"] = child_health["latency_ms"]
            health["is_connected"] = child_health["is_connected"]
            if child_health["status"] == "ERROR":
                health["status"] = "ERROR"
                health["error_message"] = child_health["error_message"]
        health["active_profile"] = self.active_profile
        health["has_ptz"] = self.has_ptz
        return health
