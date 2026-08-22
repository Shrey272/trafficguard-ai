from pydantic import BaseModel
from datetime import datetime

class AlertBase(BaseModel):
    incident_id: int
    message: str
    recipient: str
    status: str

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
