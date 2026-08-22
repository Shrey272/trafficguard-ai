from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IncidentBase(BaseModel):
    camera_id: str
    incident_type: str
    severity: str
    confidence: float
    latitude: float
    longitude: float
    vehicle_count: int
    description: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: str

class IncidentResponse(IncidentBase):
    id: int
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True
