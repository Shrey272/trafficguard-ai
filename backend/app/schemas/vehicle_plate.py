from pydantic import BaseModel  # type: ignore
from typing import Optional, List
from datetime import datetime

class VehiclePlateBase(BaseModel):
    plate_number: str
    camera_id: str
    camera_name: str
    latitude: float
    longitude: float
    vehicle_type: str = "Car"
    confidence: float = 95.0
    status: str = "NORMAL"

class VehiclePlateCreate(VehiclePlateBase):
    pass

class VehiclePlateResponse(VehiclePlateBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class VehicleTraceTimeline(BaseModel):
    plate_number: str
    total_sightings: int
    last_seen: datetime
    sightings: List[VehiclePlateResponse]
