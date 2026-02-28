from pydantic import BaseModel
from datetime import datetime
from typing import List

class ReadingCreate(BaseModel):
    sensor_id: int
    value: float

class ReadingRead(ReadingCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class TrendPoint(BaseModel):
    hora: str
    valor: float

class TrendResponse(BaseModel):
    sensor_type: str
    data: List[TrendPoint]

    class Config:
        from_attributes = True