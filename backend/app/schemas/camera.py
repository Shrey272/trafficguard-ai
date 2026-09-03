import re
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

def mask_rtsp_url(url: Optional[str]) -> Optional[str]:
    if not url:
        return url
    # Mask rtsp://username:password@ip:port/path -> rtsp://***:***@ip:port/path
    masked = re.sub(r'(rtsp://|rtsps://)([^:@/]+):([^@/]+)@', r'\1***:***@', url)
    return masked

class CameraBase(BaseModel):
    camera_code: str
    name: str
    description: Optional[str] = None
    department: str = "Traffic Police"
    vendor: str = "Hikvision"
    model: str = "Standard IP/PTZ"
    vms_name: str = "Main VMS"
    source_type: str = "RTSP"  # RTSP, ONVIF, FILE, WEBCAM, VMS, SDK, MOCK
    location_name: str
    latitude: float
    longitude: float
    rtsp_url: Optional[str] = None
    credential_reference: Optional[str] = None
    status: str = "ONLINE"  # ONLINE, OFFLINE, CONNECTING, ERROR, DISABLED
    enabled: bool = True

    # Phase 2 Fields
    onvif_host: Optional[str] = None
    onvif_port: Optional[int] = 80
    onvif_profile_token: Optional[str] = None
    has_ptz: bool = False
    capabilities: Optional[str] = "STREAMING"
    video_file_path: Optional[str] = None
    device_index: Optional[int] = 0
    
    # Phase 5 Fields
    pixels_per_meter: Optional[float] = None

class CameraCreate(CameraBase):
    id: Optional[str] = None
    # Raw password accepted on creation/registration only, never stored in plaintext in response
    onvif_password: Optional[str] = None
    onvif_username: Optional[str] = None

class CameraUpdate(BaseModel):
    camera_code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    vms_name: Optional[str] = None
    source_type: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rtsp_url: Optional[str] = None
    credential_reference: Optional[str] = None
    status: Optional[str] = None
    enabled: Optional[bool] = None
    onvif_host: Optional[str] = None
    onvif_port: Optional[int] = None
    onvif_profile_token: Optional[str] = None
    has_ptz: Optional[bool] = None
    capabilities: Optional[str] = None
    video_file_path: Optional[str] = None
    device_index: Optional[int] = None
    onvif_password: Optional[str] = None
    onvif_username: Optional[str] = None
    pixels_per_meter: Optional[float] = None

class CameraResponse(CameraBase):
    id: str
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Backward compatibility with existing frontend
    is_active: bool = True
    video_url: Optional[str] = None
    incident_count: Optional[int] = 0

    @field_validator('rtsp_url', mode='after')
    @classmethod
    def sanitize_rtsp(cls, v: Optional[str]) -> Optional[str]:
        return mask_rtsp_url(v)

    @field_validator('video_url', mode='after')
    @classmethod
    def sanitize_video(cls, v: Optional[str]) -> Optional[str]:
        return mask_rtsp_url(v)

    @field_validator('credential_reference', mode='after')
    @classmethod
    def sanitize_credential_reference(cls, v: Optional[str]) -> Optional[str]:
        return "***" if v else None

    class Config:
        from_attributes = True

class CameraHealthResponse(BaseModel):
    camera_id: str
    camera_code: str
    name: str
    status: str
    is_connected: bool
    fps: float
    uptime_seconds: float
    error_message: Optional[str] = None
    latency_ms: float
    last_frame_time: Optional[datetime] = None
    reconnect_attempts: int
    source_type: str
    has_ptz: bool = False
    capabilities: Optional[str] = "STREAMING"
