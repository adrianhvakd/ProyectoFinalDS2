from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubscriptionPaymentBase(BaseModel):
    company_id: int
    service_id: int
    period_start: datetime
    period_end: datetime
    amount: float
    payment_type: str = "renewal"


class SubscriptionPaymentCreate(SubscriptionPaymentBase):
    payment_proof_filename: Optional[str] = None


class SubscriptionPaymentUpdate(BaseModel):
    status: Optional[str] = None
    paid_at: Optional[datetime] = None
    approved_by: Optional[str] = None


class SubscriptionPaymentRead(SubscriptionPaymentBase):
    id: int
    status: str
    payment_proof_filename: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    approved_by: Optional[str] = None

    class Config:
        from_attributes = True
