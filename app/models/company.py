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
    onboarding_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, foreign_key="user.id")
