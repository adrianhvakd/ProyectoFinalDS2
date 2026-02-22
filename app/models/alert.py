from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    severity: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_resolved: bool = Field(default=False)
    
    reading_id: int = Field(foreign_key="reading.id")

    reading: Optional["Reading"] = Relationship(back_populates="alert")