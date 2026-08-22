from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.traffic import TrafficEvent
from app.schemas.traffic import TrafficEventResponse

router = APIRouter()

@router.get("/", response_model=List[TrafficEventResponse])
def get_traffic_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return events
