from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    id: UUID
    company_id: Optional[int] = None

class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    company_id: Optional[int] = None

    @field_validator('id', mode='before')
    @classmethod
    def parse_id(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True