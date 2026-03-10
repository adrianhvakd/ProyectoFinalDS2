from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Service(SQLModel, table=True):
    __tablename__ = "service"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    duration_days: int = Field(default=30)
    plan_level: int = Field(default=1)
    has_ai: bool = Field(default=False)
    has_advanced_reports: bool = Field(default=False)
    has_priority_notifications: bool = Field(default=False)
