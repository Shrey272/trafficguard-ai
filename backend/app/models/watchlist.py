from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey  # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime

class WatchlistRecord(Base):
    __tablename__ = "watchlist_records"

    id = Column(Integer, primary_key=True, index=True)
    plate_text = Column(String, index=True, unique=True)
    category = Column(String, default="SUSPECT") # SUSPECT, STOLEN, WANTED
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class WatchlistAlert(Base):
    __tablename__ = "watchlist_alerts"

    id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(Integer, ForeignKey("vehicle_observations.id"))
    watchlist_id = Column(Integer, ForeignKey("watchlist_records.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String, default="NEW") # NEW, ACKNOWLEDGED, RESOLVED

    observation = relationship("VehicleObservation", backref="watchlist_alerts")
    watchlist_record = relationship("WatchlistRecord")
