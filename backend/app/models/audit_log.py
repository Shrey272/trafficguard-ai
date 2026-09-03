from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database.connection import Base
from datetime import datetime


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    # LOGIN, CAMERA_CREATED, CAMERA_UPDATED, CAMERA_DELETED, etc.
    action = Column(String, index=True, nullable=False)
    # AUTH, CAMERA, INCIDENT, SYSTEM
    resource_type = Column(String, index=True, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
