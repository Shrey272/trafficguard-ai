from sqlalchemy import Column, Integer, String, DateTime  # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime

class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    total_vehicles = Column(Integer)
    congestion_status = Column(String, index=True) # "LOW", "MEDIUM", "HIGH"

