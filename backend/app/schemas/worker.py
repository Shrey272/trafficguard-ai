from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EdgeWorkerBase(BaseModel):
    worker_id: str
    status: str
    capacity: int
    assigned_cameras: str
    processing_fps: float
    last_seen: datetime

class EdgeWorkerResponse(EdgeWorkerBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

class HeartbeatRequest(BaseModel):
    status: str
    processing_fps: float
    capacity: Optional[int] = None
