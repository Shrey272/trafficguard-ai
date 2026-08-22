from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    return alerts
