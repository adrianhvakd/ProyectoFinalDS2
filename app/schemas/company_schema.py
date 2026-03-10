from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class CompanyCreate(BaseModel):
    name: str
    industry: str = "mining"


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    is_public_enabled: Optional[bool] = None
    service_id: Optional[int] = None
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    is_subscription_active: Optional[bool] = None


class CompanyRead(BaseModel):
    id: int
    name: str
    industry: str
    public_token: str
    is_public_enabled: bool
    created_at: datetime
    created_by: Optional[UUID] = None
    service_id: Optional[int] = None
    subscription_start: Optional[datetime] = None
    subscription_end: Optional[datetime] = None
    is_subscription_active: bool = True

    class Config:
        from_attributes = True
