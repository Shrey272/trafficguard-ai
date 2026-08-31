from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import List, Optional
from app.database.connection import get_db  # type: ignore
from app.models.vehicle_plate import VehiclePlate  # type: ignore
from app.schemas.vehicle_plate import VehiclePlateResponse, VehiclePlateCreate, VehicleTraceTimeline  # type: ignore

router = APIRouter()

@router.get("/", response_model=List[VehiclePlateResponse])
def get_plates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    plates = db.query(VehiclePlate).order_by(VehiclePlate.timestamp.desc()).offset(skip).limit(limit).all()
    return plates

@router.get("/search", response_model=VehicleTraceTimeline)
def search_plate_history(plate_number: str = Query(..., description="Vehicle registration plate number to trace"), db: Session = Depends(get_db)):
    formatted_query = plate_number.strip().upper()
    sightings = (
        db.query(VehiclePlate)
        .filter(VehiclePlate.plate_number.ilike(f"%{formatted_query}%"))
        .order_by(VehiclePlate.timestamp.asc())
        .all()
    )
    
    if not sightings:
        raise HTTPException(status_code=404, detail=f"No sightings found for vehicle plate '{plate_number}'")
    
    return VehicleTraceTimeline(
        plate_number=sightings[0].plate_number,
        total_sightings=len(sightings),
        last_seen=sightings[-1].timestamp,
        sightings=sightings
    )

@router.post("/", response_model=VehiclePlateResponse)
def create_plate_detection(plate: VehiclePlateCreate, db: Session = Depends(get_db)):
    db_plate = VehiclePlate(**plate.dict())
    db.add(db_plate)
    db.commit()
    db.refresh(db_plate)
    return db_plate
