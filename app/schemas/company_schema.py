from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    industry: str = "mining"


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    is_public_enabled: Optional[bool] = None
    onboarding_completed: Optional[bool] = None


class CompanyRead(BaseModel):
    id: int
    name: str
    industry: str
    public_token: str
    is_public_enabled: bool
    onboarding_completed: bool
    created_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True
