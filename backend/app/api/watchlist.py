from fastapi import APIRouter, Depends, HTTPException, Query  # type: ignore
from app.core.deps import require_permission, get_current_user
from app.services.audit_service import record_audit
from fastapi import Request
from app.models.user import User
from sqlalchemy.orm import Session  # type: ignore
from typing import List, Optional
from app.database.connection import get_db  # type: ignore
from app.models.watchlist import WatchlistRecord, WatchlistAlert  # type: ignore
from app.schemas.watchlist import WatchlistRecordResponse, WatchlistRecordCreate, WatchlistAlertResponse  # type: ignore

router = APIRouter()

@router.get("/", response_model=List[WatchlistRecordResponse], dependencies=[Depends(require_permission("watchlist.manage"))])
def get_watchlist(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(WatchlistRecord).order_by(WatchlistRecord.created_at.desc()).offset(skip).limit(limit).all()
    return records

@router.post("/", response_model=WatchlistRecordResponse, dependencies=[Depends(require_permission("watchlist.manage"))])
def add_to_watchlist(record: WatchlistRecordCreate, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    formatted_plate = record.plate_text.strip().upper()
    
    existing = db.query(WatchlistRecord).filter(WatchlistRecord.plate_text == formatted_plate).first()
    if existing:
        raise HTTPException(status_code=400, detail="Plate already exists in watchlist")
        
    db_record = WatchlistRecord(
        plate_text=formatted_plate,
        category=record.category,
        notes=record.notes
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    record_audit(
        action="WATCHLIST_ADDED",
        resource_type="WATCHLIST",
        resource_id=str(db_record.id),
        details=f"Added plate {db_record.plate_text} to watchlist (Category: {db_record.category})",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )
    return db_record

@router.delete("/{record_id}", dependencies=[Depends(require_permission("watchlist.manage"))])
def remove_from_watchlist(record_id: int, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(WatchlistRecord).filter(WatchlistRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Watchlist record not found")
        
    db.delete(record)
    db.commit()
    
    record_audit(
        action="WATCHLIST_REMOVED",
        resource_type="WATCHLIST",
        resource_id=str(record_id),
        details=f"Removed plate {record.plate_text} from watchlist",
        user=current_user,
        ip_address=request.client.host if request.client else None,
        db=db
    )
    return {"message": "Record removed from watchlist"}

@router.get("/alerts", response_model=List[WatchlistAlertResponse], dependencies=[Depends(require_permission("anpr.search"))])
def get_alerts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    alerts = db.query(WatchlistAlert).order_by(WatchlistAlert.timestamp.desc()).offset(skip).limit(limit).all()
    return alerts
