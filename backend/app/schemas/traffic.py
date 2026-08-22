from pydantic import BaseModel
from datetime import datetime

class TrafficEventBase(BaseModel):
    camera_id: str
    total_vehicles: int
    congestion_status: str

class TrafficEventCreate(TrafficEventBase):
    pass

class TrafficEventResponse(TrafficEventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
