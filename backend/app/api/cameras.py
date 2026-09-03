import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.camera import Camera
from app.models.incident import Incident
from app.models.user import User
from app.schemas.camera import CameraResponse, CameraCreate, CameraUpdate, CameraHealthResponse
from app.core.deps import get_current_user, require_permission, get_optional_user
from app.camera.camera_manager import camera_manager
from app.services.audit_service import record_audit

router = APIRouter()

@router.get("", response_model=List[CameraResponse], dependencies=[Depends(require_permission("camera.read"))])
@router.get("/", response_model=List[CameraResponse], dependencies=[Depends(require_permission("camera.read"))])
def get_cameras(
    department: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Camera)
    if department and department != "ALL":
        query = query.filter(Camera.department == department)
    if status_filter and status_filter != "ALL":
        query = query.filter(Camera.status == status_filter)
    if search:
        s = f"%{search}%"
        query = query.filter((Camera.name.ilike(s)) | (Camera.camera_code.ilike(s)) | (Camera.location_name.ilike(s)))

    cameras = query.offset(skip).limit(limit).all()
    
    # Enrich cameras with recent incident counts
    results = []
    for cam in cameras:
        inc_count = db.query(func.count(Incident.id)).filter(
            (Incident.camera_id == cam.id) | (Incident.camera_id == cam.camera_code)
        ).scalar() or 0
        
        cam_resp = CameraResponse.model_validate(cam)
        cam_resp.incident_count = inc_count
        cam_resp.video_url = cam.rtsp_url
        cam_resp.is_active = cam.enabled and cam.status != "DISABLED"
        results.append(cam_resp)

    return results

@router.get("/{id}", response_model=CameraResponse, dependencies=[Depends(require_permission("camera.read"))])
def get_camera(id: str, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail=f"Camera with ID or Code '{id}' not found")
    
    inc_count = db.query(func.count(Incident.id)).filter(
        (Incident.camera_id == camera.id) | (Incident.camera_id == camera.camera_code)
    ).scalar() or 0

    resp = CameraResponse.model_validate(camera)
    resp.incident_count = inc_count
    resp.video_url = camera.rtsp_url
    resp.is_active = camera.enabled and camera.status != "DISABLED"
    return resp

@router.post("", response_model=CameraResponse, dependencies=[Depends(require_permission("camera.write"))])
@router.post("/", response_model=CameraResponse, dependencies=[Depends(require_permission("camera.write"))])
def create_camera(
    camera_in: CameraCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if code already exists
    existing = db.query(Camera).filter(Camera.camera_code == camera_in.camera_code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Camera code '{camera_in.camera_code}' already exists")

    cam_id = camera_in.id or f"CAM-{uuid.uuid4().hex[:6].upper()}"
    new_cam = Camera(
        id=cam_id,
        camera_code=camera_in.camera_code,
        name=camera_in.name,
        description=camera_in.description,
        department=camera_in.department,
        vendor=camera_in.vendor,
        model=camera_in.model,
        vms_name=camera_in.vms_name,
        source_type=camera_in.source_type,
        location_name=camera_in.location_name,
        latitude=camera_in.latitude,
        longitude=camera_in.longitude,
        rtsp_url=camera_in.rtsp_url,
        credential_reference=camera_in.credential_reference,
        status="CONNECTING" if camera_in.enabled else "DISABLED",
        enabled=camera_in.enabled,
        last_seen=datetime.utcnow(),
        onvif_host=camera_in.onvif_host,
        onvif_port=camera_in.onvif_port,
        onvif_profile_token=camera_in.onvif_profile_token,
        has_ptz=camera_in.has_ptz,
        capabilities=camera_in.capabilities or "STREAMING",
        video_file_path=camera_in.video_file_path,
        device_index=camera_in.device_index or 0
    )
    db.add(new_cam)
    db.commit()
    db.refresh(new_cam)

    if new_cam.enabled:
        creds = {}
        if camera_in.onvif_username or camera_in.onvif_password:
            creds = {"username": camera_in.onvif_username, "password": camera_in.onvif_password}
        camera_manager.start_camera(new_cam.id, credentials=creds, db=db)

    record_audit(
        action="CAMERA_CREATED",
        resource_type="CAMERA",
        resource_id=new_cam.id,
        details=f"Registered camera {new_cam.camera_code} ({new_cam.name}) at {new_cam.location_name}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )

    resp = CameraResponse.model_validate(new_cam)
    resp.incident_count = 0
    return resp

@router.put("/{id}", response_model=CameraResponse, dependencies=[Depends(require_permission("camera.write"))])
def update_camera(
    id: str,
    update_in: CameraUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    update_data = update_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)

    camera.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(camera)

    if "rtsp_url" in update_data or "enabled" in update_data or "status" in update_data:
        if camera.enabled and camera.status != "DISABLED":
            camera_manager.restart_camera(camera.id, db=db)
        else:
            camera_manager.stop_camera(camera.id, db=db)

    record_audit(
        action="CAMERA_UPDATED",
        resource_type="CAMERA",
        resource_id=camera.id,
        details=f"Updated camera {camera.camera_code}: fields {list(update_data.keys())}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )

    resp = CameraResponse.model_validate(camera)
    return resp

@router.delete("/{id}", dependencies=[Depends(require_permission("camera.write"))])
def delete_camera(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    cam_id = camera.id
    cam_code = camera.camera_code
    camera_manager.remove_camera(cam_id)

    db.delete(camera)
    db.commit()

    record_audit(
        action="CAMERA_DELETED",
        resource_type="CAMERA",
        resource_id=cam_id,
        details=f"Deleted camera {cam_code} ({cam_id})",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )
    return {"status": "success", "message": f"Camera {cam_code} deleted successfully"}

@router.post("/{id}/connect", dependencies=[Depends(require_permission("camera.write"))])
def connect_camera(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    camera.enabled = True
    camera.status = "CONNECTING"
    db.commit()

    success = camera_manager.start_camera(camera.id, db=db)

    record_audit(
        action="CAMERA_CONNECTED",
        resource_type="CAMERA",
        resource_id=camera.id,
        details=f"Connected camera stream {camera.camera_code}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )
    return {"status": "success", "camera_id": camera.id, "camera_status": camera.status}

@router.post("/{id}/disconnect", dependencies=[Depends(require_permission("camera.write"))])
def disconnect_camera(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    camera.status = "OFFLINE"
    db.commit()

    camera_manager.stop_camera(camera.id, db=db)

    record_audit(
        action="CAMERA_DISCONNECTED",
        resource_type="CAMERA",
        resource_id=camera.id,
        details=f"Disconnected camera stream {camera.camera_code}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )
    return {"status": "success", "camera_id": camera.id, "camera_status": "OFFLINE"}

@router.post("/{id}/restart", dependencies=[Depends(require_permission("camera.write"))])
def restart_camera(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    camera.status = "CONNECTING"
    db.commit()

    camera_manager.restart_camera(camera.id, db=db)

    record_audit(
        action="CAMERA_RESTARTED",
        resource_type="CAMERA",
        resource_id=camera.id,
        details=f"Restarted camera stream {camera.camera_code}",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )
    return {"status": "success", "camera_id": camera.id, "camera_status": camera.status}

@router.get("/{id}/health", response_model=CameraHealthResponse, dependencies=[Depends(require_permission("camera.read"))])
def get_camera_health(id: str, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter((Camera.id == id) | (Camera.camera_code == id)).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    health = camera_manager.get_camera_health(camera.id)
    if health:
        return CameraHealthResponse(
            camera_id=camera.id,
            camera_code=camera.camera_code,
            name=camera.name,
            status=health["status"],
            is_connected=health["is_connected"],
            fps=health["fps"],
            uptime_seconds=health["uptime_seconds"],
            error_message=health["error_message"],
            latency_ms=health["latency_ms"],
            last_frame_time=health["last_frame_time"],
            reconnect_attempts=health["reconnect_attempts"],
            source_type=camera.source_type,
            has_ptz=health.get("has_ptz", camera.has_ptz),
            capabilities=health.get("capabilities", camera.capabilities)
        )
    
    # Return default health from DB if adapter not active
    return CameraHealthResponse(
        camera_id=camera.id,
        camera_code=camera.camera_code,
        name=camera.name,
        status=camera.status,
        is_connected=camera.status == "ONLINE",
        fps=0.0,
        uptime_seconds=0.0,
        error_message="Camera adapter not active" if camera.status != "ONLINE" else None,
        latency_ms=0.0,
        last_frame_time=camera.last_seen,
        reconnect_attempts=0,
        source_type=camera.source_type,
        has_ptz=camera.has_ptz,
        capabilities=camera.capabilities
    )
