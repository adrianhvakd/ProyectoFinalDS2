from pydantic import BaseModel
from datetime import datetime

class ReadingCreate(BaseModel):
    sensor_id: int
    value: float

class ReadingRead(ReadingCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True