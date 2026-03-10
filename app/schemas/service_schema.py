from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    name: str
    description: str
    price: float

class ServiceCreate(ServiceBase):
    duration_days: int = 30
    plan_level: int = 1
    has_ai: bool = False
    has_advanced_reports: bool = False
    has_priority_notifications: bool = False

class ServiceRead(ServiceBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    duration_days: int
    plan_level: int
    has_ai: bool
    has_advanced_reports: bool
    has_priority_notifications: bool

    class Config:
        from_attributes = True
