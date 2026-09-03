from sqlalchemy import Column, Integer, String, DateTime, ForeignKey  # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime


class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), index=True)
    # DETECTED, VERIFIED, ALERTED, ACKNOWLEDGED, DISPATCHED,
    # RESOLVED, FALSE_POSITIVE
    status = Column(String)
    # User who changed the status, if any
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
