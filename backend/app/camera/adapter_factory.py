import logging
from typing import Dict, Type, Optional
from app.models.camera import Camera
from app.camera.base_adapter import BaseCameraAdapter
from app.camera.rtsp_adapter import RTSPCameraAdapter
from app.camera.onvif_adapter import ONVIFCameraAdapter
from app.camera.file_adapter import VideoFileAdapter
from app.camera.webcam_adapter import WebcamAdapter
from app.camera.vms_adapter import VendorVMSAdapter
from app.camera.vendor_sdk_adapter import VendorSDKAdapter

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    Registry and Factory for normalized camera adapters.
    Enables TrafficGuard AI to seamlessly ingest streams from heterogeneous
    CCTV protocols, ONVIF Profiles, Video files, USB hardware, and
    Enterprise VMS platforms.
    """
    _registry: Dict[str, Type[BaseCameraAdapter]] = {
        "RTSP": RTSPCameraAdapter,
        "ONVIF": ONVIFCameraAdapter,
        "FILE": VideoFileAdapter,
        "WEBCAM": WebcamAdapter,
        "VMS": VendorVMSAdapter,
        "SDK": VendorSDKAdapter,
        "MOCK": RTSPCameraAdapter
    }

    @classmethod
    def register_adapter(
        cls, source_type: str, adapter_cls: Type[BaseCameraAdapter]
    ):
        """Allows runtime plugin registration for custom vendor adapters."""
        cls._registry[source_type.upper()] = adapter_cls
        logger.info(
            f"Registered camera adapter for source type: "
            f"{source_type.upper()}"
        )

    @classmethod
    def get_adapter_class(cls, source_type: str) -> Type[BaseCameraAdapter]:
        st = (source_type or "RTSP").upper()
        return cls._registry.get(st, RTSPCameraAdapter)

    @classmethod
    def create_adapter(
        cls,
        camera: Camera,
        credentials: Optional[Dict[str, str]] = None
    ) -> BaseCameraAdapter:
        """
        Factory method: instantiates normalized camera adapter based on
        Camera model metadata.
        """
        source_type = (camera.source_type or "RTSP").upper()

        creds = credentials or {}
        username = creds.get("username")
        password = creds.get("password")

        if source_type == "ONVIF":
            if camera.rtsp_url:
                default_host = camera.rtsp_url.split("@")[-1].split(":")[0]
            else:
                default_host = "127.0.0.1"
            return ONVIFCameraAdapter(
                camera_id=camera.id,
                camera_code=camera.camera_code,
                onvif_host=camera.onvif_host or default_host,
                onvif_port=camera.onvif_port or 80,
                onvif_profile_token=(
                    camera.onvif_profile_token or "Profile_1_Main"
                ),
                has_ptz=camera.has_ptz,
                username=username,
                password=password,
                source_type="ONVIF"
            )
        elif source_type == "FILE":
            return VideoFileAdapter(
                camera_id=camera.id,
                camera_code=camera.camera_code,
                video_file_path=camera.video_file_path,
                source_type="FILE"
            )
        elif source_type == "WEBCAM":
            return WebcamAdapter(
                camera_id=camera.id,
                camera_code=camera.camera_code,
                device_index=camera.device_index or 0,
                source_type="WEBCAM"
            )
        elif source_type == "VMS":
            return VendorVMSAdapter(
                camera_id=camera.id,
                camera_code=camera.camera_code,
                vms_name=camera.vms_name or "Milestone XProtect",
                channel_id=camera.camera_code,
                source_type="VMS",
                rtsp_fallback_url=camera.rtsp_url
            )
        elif source_type == "SDK":
            return VendorSDKAdapter(
                camera_id=camera.id,
                camera_code=camera.camera_code,
                vendor=camera.vendor or "Hikvision",
                source_type="SDK",
                rtsp_fallback_url=camera.rtsp_url
            )
        else:
            # Default / RTSP / MOCK
            return RTSPCameraAdapter(
                camera_id=camera.id,
                camera_code=camera.camera_code,
                rtsp_url=camera.rtsp_url,
                source_type=source_type
            )


AdapterFactory = AdapterRegistry
