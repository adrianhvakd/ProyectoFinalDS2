from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Sensor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str
    location: str
    description: Optional[str] = None
    min_threshold: float
    max_threshold: float
    is_active: bool = Field(default=True)

    readings: List["Reading"] = Relationship(back_populates="sensor")