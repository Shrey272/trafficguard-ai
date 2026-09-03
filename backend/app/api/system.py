from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db
from app.models.camera import Camera
from app.models.incident import Incident
from app.models.worker import EdgeWorker
from app.api.websocket import manager
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/health")
def get_system_health(db: Session = Depends(get_db)):
    # Database status
    db_status = "UP"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "DOWN"

    # Cameras
    total_cameras = db.query(Camera).count()
    online_cameras = db.query(Camera).filter(Camera.status == 'ONLINE').count()
    offline_cameras = db.query(Camera).filter(Camera.status == 'OFFLINE').count()
    error_cameras = db.query(Camera).filter(Camera.status == 'ERROR').count()

    # Active Incidents (not resolved or false positive)
    active_incidents = db.query(Incident).filter(Incident.status.notin_(['RESOLVED', 'FALSE_POSITIVE'])).count()

    # Edge Workers
    one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
    active_workers = db.query(EdgeWorker).filter(EdgeWorker.last_seen >= one_minute_ago).count()
    offline_workers = db.query(EdgeWorker).filter(EdgeWorker.last_seen < one_minute_ago).count()

    # WebSockets
    ws_connections = len(manager.active_connections)

    return {
        "status": "UP" if db_status == "UP" else "DEGRADED",
        "database": db_status,
        "cameras": {
            "total": total_cameras,
            "online": online_cameras,
            "offline": offline_cameras,
            "error": error_cameras
        },
        "incidents": {
            "active": active_incidents
        },
        "edge_workers": {
            "active": active_workers,
            "offline": offline_workers
        },
        "websockets": {
            "active_connections": ws_connections
        },
        "timestamp": datetime.utcnow().isoformat()
    }
