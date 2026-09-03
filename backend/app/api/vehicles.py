from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from app.core.deps import require_permission
from sqlalchemy.orm import Session, joinedload  # type: ignore
from typing import List, Optional
from app.database.connection import get_db  # type: ignore
from app.models.vehicle_observation import VehicleObservation  # type: ignore
from app.models.vehicle_journey import VehicleJourney  # type: ignore
from app.schemas.vehicle import VehicleObservationResponse, VehicleObservationCreate, VehicleTraceTimeline, VehicleJourneyResponse  # type: ignore

router = APIRouter()

@router.get("/observations", response_model=List[VehicleObservationResponse], dependencies=[Depends(require_permission("anpr.search"))])
def get_observations(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    obs = db.query(VehicleObservation).order_by(VehicleObservation.timestamp.desc()).offset(skip).limit(limit).all()
    return obs

@router.get("/search", response_model=VehicleTraceTimeline, dependencies=[Depends(require_permission("anpr.search"))])
def search_vehicle_history(plate_number: str = Query(..., description="Vehicle registration plate number to trace"), db: Session = Depends(get_db)):
    formatted_query = plate_number.strip().upper()
    
    # 1. Get Observations
    sightings = (
        db.query(VehicleObservation)
        .filter(VehicleObservation.normalized_plate.ilike(f"%{formatted_query}%"))
        .order_by(VehicleObservation.timestamp.asc())
        .all()
    )
    
    if not sightings:
        raise HTTPException(status_code=404, detail=f"No sightings found for vehicle plate '{plate_number}'")
    
    # 2. Get the latest journey for this plate
    latest_journey = (
        db.query(VehicleJourney)
        .options(joinedload(VehicleJourney.points))
        .filter(VehicleJourney.normalized_plate.ilike(f"%{formatted_query}%"))
        .order_by(VehicleJourney.last_seen.desc())
        .first()
    )
    
    journey_response = None
    if latest_journey:
        # Sort points by timestamp
        latest_journey.points.sort(key=lambda x: x.timestamp)
        journey_response = VehicleJourneyResponse.from_orm(latest_journey)

    return VehicleTraceTimeline(
        normalized_plate=sightings[0].normalized_plate,
        total_sightings=len(sightings),
        last_seen=sightings[-1].timestamp,
        sightings=sightings,
        journey=journey_response
    )

@router.post("/observations", response_model=VehicleObservationResponse, dependencies=[Depends(require_permission("system.config"))])
def create_observation(obs: VehicleObservationCreate, db: Session = Depends(get_db)):
    db_obs = VehicleObservation(**obs.dict())
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs
