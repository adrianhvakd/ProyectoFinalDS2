from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Reading(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    sensor_id: int = Field(foreign_key="sensor.id")
    
    sensor: Optional["Sensor"] = Relationship(back_populates="readings")
    alert: Optional["Alert"] = Relationship(back_populates="reading")