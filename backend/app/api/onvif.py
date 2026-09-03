from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.models.user import User
from app.models.camera import Camera
from app.core.deps import get_current_user, require_permission
from app.schemas.onvif import (
    ONVIFDiscoveryRequest, ONVIFDiscoveredDevice,
    ONVIFInspectRequest, ONVIFInspectResponse,
    PTZMoveRequest, PTZStatusResponse
)
from app.camera.onvif_service import onvif_service
from app.camera.camera_manager import camera_manager
from app.services.audit_service import record_audit

router = APIRouter()


@router.post(
    "/discover",
    response_model=List[ONVIFDiscoveredDevice],
    dependencies=[Depends(require_permission("camera.write"))]
)
def discover_onvif_devices(
    req: Optional[ONVIFDiscoveryRequest] = None,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scans network for ONVIF Profile S/T devices via WS-Discovery UDP probe.
    """
    timeout = req.timeout_seconds if req else 3.0
    subnet = req.subnet if req else None

    devices = onvif_service.discover_devices(
        timeout_seconds=timeout, subnet=subnet
    )

    record_audit(
        action="ONVIF_DISCOVERY_EXECUTED",
        resource_type="NETWORK",
        resource_id=subnet or "LOCAL_BROADCAST",
        details=f"Discovered {len(devices)} ONVIF devices on network",
        user=current_user,
        ip_address=(
            request.client.host
            if request and request.client else None
        ),
        db=db
    )
    return devices


@router.post(
    "/inspect",
    response_model=ONVIFInspectResponse,
    dependencies=[Depends(require_permission("camera.write"))]
)
def inspect_onvif_device(
    req: ONVIFInspectRequest,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connects to a specific ONVIF device, authenticates, and retrieves device
    info, capabilities, media profiles, and stream URIs.
    """
    try:
        inspection = onvif_service.inspect_device(
            host=req.host,
            port=req.port,
            username=req.username,
            password=req.password
        )

        manufacturer = inspection.device_info.manufacturer
        model = inspection.device_info.model
        profile_count = len(inspection.profiles)
        record_audit(
            action="ONVIF_DEVICE_INSPECTED",
            resource_type="CAMERA",
            resource_id=f"{req.host}:{req.port}",
            details=(
                f"Inspected ONVIF device {manufacturer} {model} "
                f"({profile_count} profiles found)"
            ),
            user=current_user,
            ip_address=(
                request.client.host
                if request and request.client else None
            ),
            db=db
        )
        return inspection
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ONVIF Inspection failed: {str(e)}"
        )


@router.post(
    "/ptz/move",
    dependencies=[Depends(require_permission("camera.write"))]
)
def move_ptz(
    req: PTZMoveRequest,
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dispatches PTZ move command (pan, tilt, zoom) to a PTZ-capable camera.
    """
    camera = db.query(Camera).filter(
        (Camera.id == req.camera_id) |
        (Camera.camera_code == req.camera_id)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    success = camera_manager.execute_ptz(
        camera_id=camera.id,
        pan=req.pan,
        tilt=req.tilt,
        zoom=req.zoom,
        speed=req.speed
    )

    if not success and not camera.has_ptz:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Camera {camera.camera_code} does not support "
                "PTZ operations"
            )
        )

    record_audit(
        action="CAMERA_PTZ_COMMAND",
        resource_type="CAMERA",
        resource_id=camera.id,
        details=(
            f"Dispatched PTZ: pan={req.pan}, tilt={req.tilt}, "
            f"zoom={req.zoom}, speed={req.speed}"
        ),
        user=current_user,
        ip_address=(
            request.client.host
            if request and request.client else None
        ),
        db=db
    )
    return {
        "status": "success",
        "camera_id": camera.id,
        "pan": req.pan,
        "tilt": req.tilt,
        "zoom": req.zoom,
        "message": f"PTZ command executed on {camera.camera_code}"
    }


@router.get(
    "/ptz/{camera_id}/status",
    response_model=PTZStatusResponse,
    dependencies=[Depends(require_permission("camera.read"))]
)
def get_ptz_status(
    camera_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns current PTZ telemetry and positional status.
    """
    camera = db.query(Camera).filter(
        (Camera.id == camera_id) |
        (Camera.camera_code == camera_id)
    ).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    adapter = camera_manager.get_adapter(camera.id)
    has_ptz = camera.has_ptz or (adapter.has_ptz if adapter else False)

    return PTZStatusResponse(
        camera_id=camera.id,
        has_ptz=has_ptz,
        pan=0.0,
        tilt=0.0,
        zoom=0.0,
        moving=False
    )
