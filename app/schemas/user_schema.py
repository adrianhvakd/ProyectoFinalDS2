from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "operator"

class UserCreate(UserBase):
    id: str

class UserRead(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True