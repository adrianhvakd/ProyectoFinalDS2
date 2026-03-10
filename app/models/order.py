from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Order(SQLModel, table=True):
    __tablename__ = "order"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    service_id: int = Field(foreign_key="service.id")
    company_name: str
    company_address: str
    company_phone: str
    status: str = Field(default="pending")
    payment_proof_filename: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = Field(default=None)
