from pydantic import BaseModel
from datetime import datetime
from .reading_schema import ReadingRead
from typing import Optional

class AlertCreate(BaseModel):
    description: str
    severity: str
    reading_id: int

class AlertRead(AlertCreate):
    id: int
    timestamp: datetime
    is_resolved: bool
    reading: Optional[ReadingRead] = None

    class Config:
        from_attributes = True