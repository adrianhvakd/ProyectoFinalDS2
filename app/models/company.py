from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Company(SQLModel, table=True):
    __tablename__ = "company"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    industry: str = "mining"
    public_token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)
    is_public_enabled: bool = Field(default=False)
    service_id: Optional[int] = Field(default=None, foreign_key="service.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, foreign_key="user.id")
    
    subscription_start: Optional[datetime] = Field(default=None)
    subscription_end: Optional[datetime] = Field(default=None)
    is_subscription_active: bool = Field(default=True)
