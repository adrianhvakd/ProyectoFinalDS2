from sqlmodel import SQLModel, Field
from typing import Optional


class Zone(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    name: str
    color: str = "#3B82F6"
    position_x: float
    position_y: float
    width: float = 10
    height: float = 10
    description: Optional[str] = None
