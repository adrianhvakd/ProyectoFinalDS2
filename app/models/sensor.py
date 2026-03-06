from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Sensor(SQLModel, table=True):
    __tablename__ = "sensor"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str
    location: str
    description: Optional[str] = None
    min_threshold: float
    max_threshold: float
    is_active: bool = Field(default=True)
    
    position_x: float = Field(default=0)
    position_y: float = Field(default=0)
    
    company_id: int = Field(foreign_key="company.id")

    readings: List["Reading"] = Relationship(back_populates="sensor")