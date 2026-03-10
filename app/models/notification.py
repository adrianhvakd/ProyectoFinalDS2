from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Notification(SQLModel, table=True):
    __tablename__ = "notification"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    type: str
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
