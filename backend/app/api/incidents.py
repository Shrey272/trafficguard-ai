from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentResponse, IncidentCreate, IncidentUpdate

router = APIRouter()

@router.get("/", response_model=List[IncidentResponse])
def get_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.timestamp.desc()).offset(skip).limit(limit).all()
    return incidents

@router.get("/{id}", response_model=IncidentResponse)
def get_incident(id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/", response_model=IncidentResponse)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    # Ideally, trigger a websocket event here
    return db_incident

@router.patch("/{id}/status", response_model=IncidentResponse)
def update_incident_status(id: int, status_update: IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident.status = status_update.status
    db.commit()
    db.refresh(incident)
    return incident
