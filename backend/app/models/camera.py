from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database.connection import Base
from datetime import datetime


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String, primary_key=True, index=True)
    camera_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    department = Column(String, default="Traffic Police", index=True)
    vendor = Column(String, default="Hikvision")
    model = Column(String, default="Standard IP/PTZ")
    vms_name = Column(String, default="Main VMS")
    # RTSP, ONVIF, FILE, WEBCAM, VMS, SDK, MOCK
    source_type = Column(String, default="RTSP")
    location_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rtsp_url = Column(String, nullable=True)
    # Secure reference / key identifier
    credential_reference = Column(String, nullable=True)
    # ONLINE, OFFLINE, CONNECTING, ERROR, DISABLED
    status = Column(String, default="ONLINE", index=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Phase 2: Gateway, ONVIF, and VMS Extensions
    onvif_host = Column(String, nullable=True)
    onvif_port = Column(Integer, nullable=True, default=80)
    onvif_profile_token = Column(String, nullable=True)
    has_ptz = Column(Boolean, default=False)
    # e.g., "STREAMING,ONVIF_PROFILE_S,PTZ,EVENTS"
    capabilities = Column(String, nullable=True, default="STREAMING")
    video_file_path = Column(String, nullable=True)  # For FILE source_type
    device_index = Column(Integer, nullable=True, default=0)  # For WEBCAM

    # Phase 5: Calibration
    pixels_per_meter = Column(Float, nullable=True)

    # Backward compatibility with existing frontend/simulator fields
    @property
    def is_active(self) -> bool:
        return self.enabled and self.status != "DISABLED"

    @property
    def video_url(self) -> str | None:
        return self.rtsp_url
