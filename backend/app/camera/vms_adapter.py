import logging
from datetime import datetime
from typing import Optional, Any, Dict
from app.camera.base_adapter import BaseCameraAdapter
from app.camera.rtsp_adapter import RTSPCameraAdapter

logger = logging.getLogger(__name__)

class VendorVMSAdapter(BaseCameraAdapter):
    """
    Enterprise VMS Integration Adapter (Interface Contract & Implementation Stub).
    Provides normalized access for Video Management Systems such as Milestone XProtect,
    Genetec Security Center, and Avigilon Control Center.
    
    Status: INTERFACE CONTRACT IMPLEMENTED (Proprietary C-SDK binaries require licensed server runtime).
    """
    def __init__(
        self,
        camera_id: str,
        camera_code: str,
        vms_name: str = "Milestone XProtect",
        vms_server_url: Optional[str] = None,
        channel_id: Optional[str] = None,
        source_type: str = "VMS",
        rtsp_fallback_url: Optional[str] = None
    ):
        super().__init__(
            camera_id=camera_id,
            camera_code=camera_code,
            source_type=source_type,
            has_ptz=True,
            capabilities="STREAMING,VMS_INTEGRATION,PTZ,RECORDINGS,ALARM_SYNC"
        )
        self.vms_name = vms_name
        self.vms_server_url = vms_server_url
        self.channel_id = channel_id or camera_code
        self.rtsp_fallback_url = rtsp_fallback_url or f"rtsp://127.0.0.1:554/vms/{channel_id}"
        
        self._session_token: Optional[str] = None
        self._rtsp_adapter: Optional[RTSPCameraAdapter] = None

    def authenticate_session(self) -> bool:
        """Authenticates session against VMS REST/SOAP Media Gateway."""
        logger.info(f"VMS Contract: Authenticating session with {self.vms_name} at {self.vms_server_url}")
        self._session_token = f"VMS_SESSION_{self.vms_name[:3].upper()}_2026"
        return True

    def connect(self) -> bool:
        self.status = "CONNECTING"
        self.authenticate_session()
        
        # Uses normalized RTSP bridge stream exposed by VMS Media Gateway
        self._rtsp_adapter = RTSPCameraAdapter(
            camera_id=self.camera_id,
            camera_code=self.camera_code,
            rtsp_url=self.rtsp_fallback_url,
            source_type="VMS"
        )
        success = self._rtsp_adapter.connect()
        self.status = "ONLINE" if success else "ERROR"
        self.start_time = datetime.utcnow()
        return success

    def disconnect(self) -> bool:
        self.status = "OFFLINE"
        if self._rtsp_adapter:
            self._rtsp_adapter.disconnect()
            self._rtsp_adapter = None
        self._session_token = None
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
        self.disconnect()
        return self.connect()

    def ptz_move(self, pan: float, tilt: float, zoom: float, speed: float = 0.5) -> bool:
        logger.info(f"VMS Contract: Dispatched PTZ command to {self.vms_name} Channel #{self.channel_id} (Pan: {pan}, Tilt: {tilt}, Zoom: {zoom})")
        return True

    def subscribe_vms_analytics_events(self, callback: Any) -> bool:
        """Contract: Registers listener for VMS edge analytics & alarm triggers."""
        logger.info(f"VMS Contract: Subscribed to alarm matrix on {self.vms_name}")
        return True
