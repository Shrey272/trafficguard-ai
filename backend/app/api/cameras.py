from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraResponse, CameraCreate

router = APIRouter()

@router.get("/", response_model=List[CameraResponse])
def get_cameras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cameras = db.query(Camera).offset(skip).limit(limit).all()
    return cameras
