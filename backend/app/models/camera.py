from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database.connection import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    is_active = Column(Boolean, default=True)
    video_url = Column(String, nullable=True) # For demo mode or RTSP later
