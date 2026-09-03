from pydantic import BaseModel  # type: ignore
from typing import Optional, List
from datetime import datetime

class VehicleObservationBase(BaseModel):
    camera_id: str
    track_id: Optional[int] = None
    plate_text: str
    normalized_plate: str
    ocr_confidence: float = 0.0
    detection_confidence: float = 0.0
    vehicle_class: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    snapshot_reference: Optional[str] = None

class VehicleObservationCreate(VehicleObservationBase):
    pass

class VehicleObservationResponse(VehicleObservationBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class JourneyPointResponse(BaseModel):
    id: int
    camera_id: str
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence: float

    class Config:
        from_attributes = True

class VehicleJourneyResponse(BaseModel):
    id: int
    normalized_plate: str
    first_seen: datetime
    last_seen: datetime
    status: str
    points: List[JourneyPointResponse]

    class Config:
        from_attributes = True

class VehicleTraceTimeline(BaseModel):
    normalized_plate: str
    total_sightings: int
    last_seen: datetime
    sightings: List[VehicleObservationResponse]
    journey: Optional[VehicleJourneyResponse] = None
