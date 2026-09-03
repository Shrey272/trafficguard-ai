from sqlalchemy import Column, Integer, String, Float, DateTime  # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)
    incident_type = Column(String)  # e.g., "ACCIDENT"
    severity = Column(String)  # "Minor", "Moderate", "Major"
    confidence = Column(Float)  # 0-100
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    vehicle_count = Column(Integer)
    status = Column(String, default="NEW", index=True)  # NEW, ACKNOWLEDGED, RESOLVED
    description = Column(String, nullable=True)

    # Phase 5: Evidence
    track_ids = Column(String, nullable=True)
    snapshot_reference = Column(String, nullable=True)
    video_clip_reference = Column(String, nullable=True)
    signals_used = Column(String, nullable=True)
