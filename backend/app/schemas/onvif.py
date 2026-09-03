from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ONVIFDiscoveryRequest(BaseModel):
    timeout_seconds: float = 3.0
    subnet: Optional[str] = None  # e.g., "192.168.1.0/24" or None for local probe

class ONVIFDiscoveredDevice(BaseModel):
    endpoint_reference: str
    ip_address: str
    port: int = 80
    hardware_id: Optional[str] = None
    vendor: Optional[str] = "Generic ONVIF"
    model: Optional[str] = "IP Camera"
    firmware_version: Optional[str] = None
    serial_number: Optional[str] = None
    xaddrs: List[str] = []
    scopes: List[str] = []
    has_ptz: bool = False

class ONVIFInspectRequest(BaseModel):
    host: str
    port: int = 80
    username: Optional[str] = None
    password: Optional[str] = None

class ONVIFProfile(BaseModel):
    token: str
    name: str
    encoding: str = "H264"  # H264, H265, JPEG
    resolution_width: int = 1920
    resolution_height: int = 1080
    framerate: float = 30.0
    bitrate_kbps: Optional[int] = 4096
    stream_uri: Optional[str] = None
    is_ptz_compatible: bool = False

class ONVIFDeviceInfo(BaseModel):
    manufacturer: str
    model: str
    firmware_version: str
    serial_number: str
    hardware_id: str

class ONVIFCapabilities(BaseModel):
    streaming: bool = True
    ptz: bool = False
    events: bool = False
    imaging: bool = False
    device_io: bool = False
    analytics: bool = False

class ONVIFInspectResponse(BaseModel):
    host: str
    port: int
    device_info: ONVIFDeviceInfo
    capabilities: ONVIFCapabilities
    profiles: List[ONVIFProfile]
    default_stream_uri: Optional[str] = None

class PTZMoveRequest(BaseModel):
    camera_id: str
    pan: float = Field(0.0, ge=-1.0, le=1.0)
    tilt: float = Field(0.0, ge=-1.0, le=1.0)
    zoom: float = Field(0.0, ge=-1.0, le=1.0)
    speed: float = Field(0.5, ge=0.0, le=1.0)

class PTZStatusResponse(BaseModel):
    camera_id: str
    has_ptz: bool
    pan: float = 0.0
    tilt: float = 0.0
    zoom: float = 0.0
    moving: bool = False
