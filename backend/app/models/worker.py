from sqlalchemy import Column, String, Integer, DateTime, Float
from app.database.connection import Base
from datetime import datetime

class EdgeWorker(Base):
    __tablename__ = "edge_workers"

    worker_id = Column(String, primary_key=True, index=True)
    status = Column(String, default="OFFLINE") # ONLINE, OFFLINE, OVERLOADED
    capacity = Column(Integer, default=10)
    assigned_cameras = Column(String, default="[]") # JSON list of camera IDs
    processing_fps = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
