from pydantic import BaseModel # type: ignore
from typing import Optional
from datetime import datetime
from app.schemas.vehicle import VehicleObservationResponse

class WatchlistRecordBase(BaseModel):
    plate_text: str
    category: str = "SUSPECT"
    notes: Optional[str] = None

class WatchlistRecordCreate(WatchlistRecordBase):
    pass

class WatchlistRecordResponse(WatchlistRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WatchlistAlertBase(BaseModel):
    observation_id: int
    watchlist_id: int
    status: str = "NEW"

class WatchlistAlertCreate(WatchlistAlertBase):
    pass

class WatchlistAlertResponse(WatchlistAlertBase):
    id: int
    timestamp: datetime
    observation: Optional[VehicleObservationResponse] = None
    watchlist_record: Optional[WatchlistRecordResponse] = None

    class Config:
        from_attributes = True
