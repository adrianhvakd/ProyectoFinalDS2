from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class OrderBase(BaseModel):
    service_id: int
    company_name: str
    company_address: str
    company_phone: str


class OrderCreate(OrderBase):
    payment_proof_filename: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_proof_filename: Optional[str] = None


class OrderRead(OrderBase):
    id: int
    user_id: UUID
    status: str
    payment_proof_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    approved_by: Optional[UUID] = None

    class Config:
        from_attributes = True
