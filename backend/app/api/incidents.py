from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.models.incident import Incident
from app.models.incident_log import IncidentLog
from app.models.user import User
from app.schemas.incident import IncidentResponse, IncidentCreate, IncidentUpdate, IncidentLogResponse
from app.core.deps import get_current_user, require_permission, get_optional_user
from app.services.audit_service import record_audit
from app.api.websocket import manager

router = APIRouter()

@router.get("/", response_model=List[IncidentResponse], dependencies=[Depends(require_permission("incident.read"))])
def get_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.timestamp.desc()).offset(skip).limit(limit).all()
    return incidents

@router.get("/{id}", response_model=IncidentResponse, dependencies=[Depends(require_permission("incident.read"))])
def get_incident(id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/{id}/logs", response_model=List[IncidentLogResponse], dependencies=[Depends(require_permission("incident.read"))])
def get_incident_logs(id: int, db: Session = Depends(get_db)):
    logs = db.query(IncidentLog).filter(IncidentLog.incident_id == id).order_by(IncidentLog.timestamp.asc()).all()
    return logs

@router.post("/", response_model=IncidentResponse, dependencies=[Depends(require_permission("system.config"))])
async def create_incident(
    incident: IncidentCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # Create DETECTED log
    log = IncidentLog(
        incident_id=db_incident.id,
        status="DETECTED",
        user_id=None,
        notes="Incident automatically detected by pipeline"
    )
    db.add(log)
    db.commit()

    record_audit(
        action="INCIDENT_CREATED",
        resource_type="INCIDENT",
        resource_id=str(db_incident.id),
        details=f"Created incident {db_incident.incident_type} ({db_incident.severity}) at camera {db_incident.camera_id}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )

    # Broadcast to WebSocket
    await manager.broadcast({
        "type": "NEW_INCIDENT",
        "data": {
            "id": db_incident.id,
            "camera_id": db_incident.camera_id,
            "incident_type": db_incident.incident_type,
            "severity": db_incident.severity,
            "confidence": db_incident.confidence,
            "latitude": db_incident.latitude,
            "longitude": db_incident.longitude,
            "timestamp": db_incident.timestamp.isoformat() if db_incident.timestamp else None,
            "vehicle_count": db_incident.vehicle_count,
            "status": db_incident.status,
            "description": db_incident.description
        }
    })

    return db_incident

@router.patch("/{id}/status", response_model=IncidentResponse, dependencies=[Depends(require_permission("incident.acknowledge"))])
async def update_incident_status(
    id: int,
    status_update: IncidentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    old_status = incident.status
    new_status = status_update.status
    incident.status = new_status
    db.commit()
    db.refresh(incident)

    # Add to IncidentLog
    log = IncidentLog(
        incident_id=incident.id,
        status=new_status,
        user_id=current_user.id if current_user else None,
        notes=f"Status updated from {old_status} to {new_status}"
    )
    db.add(log)
    db.commit()

    action_name = "INCIDENT_ACKNOWLEDGED" if new_status == "ACKNOWLEDGED" else ("INCIDENT_RESOLVED" if new_status == "RESOLVED" else "INCIDENT_UPDATED")
    record_audit(
        action=action_name,
        resource_type="INCIDENT",
        resource_id=str(incident.id),
        details=f"Status changed from {old_status} to {new_status} by {current_user.username}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )

    # Broadcast update to clients
    await manager.broadcast({
        "type": "INCIDENT_STATUS_CHANGED",
        "data": {
            "id": incident.id,
            "status": incident.status,
            "updated_by": current_user.username
        }
    })

    return incident
