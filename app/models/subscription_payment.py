from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class SubscriptionPayment(SQLModel, table=True):
    __tablename__ = "subscription_payment"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    company_id: int = Field(foreign_key="company.id")
    service_id: int = Field(foreign_key="service.id")
    
    period_start: datetime
    period_end: datetime
    
    amount: float
    
    status: str = Field(default="pending")
    payment_type: str = Field(default="renewal")
    
    payment_proof_filename: Optional[str] = None
    
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    approved_by: Optional[str] = Field(default=None)
