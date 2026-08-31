from sqlalchemy import Column, Integer, String, Float, DateTime  # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime

class VehiclePlate(Base):
    __tablename__ = "vehicle_plates"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True)  # e.g., "GJ-05-AB-1234"
    camera_id = Column(String, index=True)      # e.g., "CAM-001"
    camera_name = Column(String)                # e.g., "Ring Road Majura Gate"
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    vehicle_type = Column(String, default="Car") # Car, SUV, Truck, Motorcycle, Bus
    confidence = Column(Float, default=95.0)     # 0-100%
    status = Column(String, default="NORMAL", index=True) # NORMAL, FLAGGED, SUSPICIOUS
