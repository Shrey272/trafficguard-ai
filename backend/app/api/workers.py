from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import json

from app.database.connection import get_db
from app.models.worker import EdgeWorker
from app.models.camera import Camera
from app.schemas.worker import EdgeWorkerResponse, HeartbeatRequest
from app.core.deps import require_permission

router = APIRouter()
internal_router = APIRouter()

@router.get("/", response_model=List[EdgeWorkerResponse], dependencies=[Depends(require_permission("system.config"))])
def get_workers(db: Session = Depends(get_db)):
    # Clean up stale workers (offline if not seen in 30s)
    now = datetime.utcnow()
    workers = db.query(EdgeWorker).all()
    for w in workers:
        if (now - w.last_seen).total_seconds() > 30 and w.status != "OFFLINE":
            w.status = "OFFLINE"
            # Reassign cameras logic could go here or in heartbeat
            w.assigned_cameras = "[]"
    db.commit()
    
    return db.query(EdgeWorker).all()


@internal_router.post("/{worker_id}/heartbeat")
def worker_heartbeat(worker_id: str, req: HeartbeatRequest, db: Session = Depends(get_db)):
    worker = db.query(EdgeWorker).filter(EdgeWorker.worker_id == worker_id).first()
    now = datetime.utcnow()
    
    if not worker:
        worker = EdgeWorker(
            worker_id=worker_id,
            status=req.status,
            capacity=req.capacity or 10,
            processing_fps=req.processing_fps,
            last_seen=now
        )
        db.add(worker)
    else:
        worker.status = req.status
        worker.processing_fps = req.processing_fps
        if req.capacity is not None:
            worker.capacity = req.capacity
        worker.last_seen = now
        
    db.commit()
    db.refresh(worker)
    
    # Assignment Logic
    assigned = json.loads(worker.assigned_cameras)
    
    # 1. Check if assigned cameras are still enabled
    valid_assigned = []
    for cam_id in assigned:
        cam = db.query(Camera).filter(Camera.id == cam_id).first()
        if cam and cam.enabled and cam.status != "DISABLED":
            valid_assigned.append(cam_id)
            
    assigned = valid_assigned
    
    # 2. If we have capacity, find unassigned cameras
    if len(assigned) < worker.capacity:
        # Get all active workers
        active_workers = db.query(EdgeWorker).filter(EdgeWorker.status != "OFFLINE", EdgeWorker.last_seen > now - timedelta(seconds=30)).all()
        all_assigned = set()
        for w in active_workers:
            if w.worker_id != worker_id: # exclude self
                all_assigned.update(json.loads(w.assigned_cameras))
                
        # Find enabled cameras not in all_assigned and not in self assigned
        unassigned_cameras = db.query(Camera).filter(Camera.enabled == True, Camera.status != "DISABLED").all()
        
        for cam in unassigned_cameras:
            if len(assigned) >= worker.capacity:
                break
            if cam.id not in all_assigned and cam.id not in assigned:
                assigned.append(cam.id)
                
    worker.assigned_cameras = json.dumps(assigned)
    db.commit()
    
    return {"assigned_cameras": assigned}
