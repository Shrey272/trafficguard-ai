from sqlalchemy import Column, Integer, String, Float, DateTime  # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime

class VehicleObservation(Base):
    __tablename__ = "vehicle_observations"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)      
    track_id = Column(Integer, nullable=True, index=True)
    plate_text = Column(String, index=True)  
    normalized_plate = Column(String, index=True)
    ocr_confidence = Column(Float, default=0.0)     
    detection_confidence = Column(Float, default=0.0)
    vehicle_class = Column(String, nullable=True) # Added for Phase 4
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    snapshot_reference = Column(String, nullable=True)
