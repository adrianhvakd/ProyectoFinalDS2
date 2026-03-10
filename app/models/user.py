from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: uuid.UUID = Field(primary_key=True, nullable=False)
    
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")