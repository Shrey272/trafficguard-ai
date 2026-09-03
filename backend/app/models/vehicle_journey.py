from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey  # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from app.database.connection import Base  # type: ignore
from datetime import datetime

class VehicleJourney(Base):
    __tablename__ = "vehicle_journeys"

    id = Column(Integer, primary_key=True, index=True)
    normalized_plate = Column(String, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ACTIVE") # e.g. ACTIVE, COMPLETED

    points = relationship("JourneyPoint", back_populates="journey", cascade="all, delete-orphan")

class JourneyPoint(Base):
    __tablename__ = "journey_points"

    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("vehicle_journeys.id"), index=True)
    camera_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    confidence = Column(Float, default=0.0)

    journey = relationship("VehicleJourney", back_populates="points")
