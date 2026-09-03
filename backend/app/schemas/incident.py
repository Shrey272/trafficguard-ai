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
    
    # Phase 5: Evidence
    track_ids: Optional[str] = None
    snapshot_reference: Optional[str] = None
    video_clip_reference: Optional[str] = None
    signals_used: Optional[str] = None

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

class IncidentLogBase(BaseModel):
    incident_id: int
    status: str
    notes: Optional[str] = None
    
class IncidentLogResponse(IncidentLogBase):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
