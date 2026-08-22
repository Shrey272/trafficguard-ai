from sqlalchemy import Column, Integer, String, DateTime
from app.database.connection import Base
from datetime import datetime

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, index=True)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    recipient = Column(String) # e.g., "POLICE", "HOSPITAL"
    status = Column(String) # "SENT", "FAILED"
