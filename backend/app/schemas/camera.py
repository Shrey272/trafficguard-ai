from pydantic import BaseModel
from typing import Optional

class CameraBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    is_active: bool = True
    video_url: Optional[str] = None

class CameraCreate(CameraBase):
    id: str

class CameraResponse(CameraBase):
    id: str

    class Config:
        from_attributes = True
