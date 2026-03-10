from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
from app.database.connection import get_session
from app.schemas.subscription_payment_schema import (
    SubscriptionPaymentRead,
    SubscriptionPaymentCreate
)
from app.models.subscription_payment import SubscriptionPayment
from app.models.company import Company
from app.models.user import User
from app.services import subscription_service
from app.core.security import verify_token
from datetime import datetime
import uuid

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


def get_current_company(current_user: dict = Depends(verify_token), db: Session = Depends(get_session)) -> Company:
    statement = select(User).where(User.id == current_user['id'])
    user = db.exec(statement).first()
    if not user or not user.company_id:
        raise HTTPException(status_code=404, detail="Usuario no tiene compañía asociada")
    
    company = db.get(Company, user.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    
    return company


@router.get("/me", response_model=dict)
def get_my_subscription(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    statement = select(User).where(User.id == current_user['id'])
    user = db.exec(statement).first()
    if not user or not user.company_id:
        raise HTTPException(status_code=404, detail="Usuario no tiene compañía asociada")
    
    company = db.get(Company, user.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Compañía no encontrada")
    
    subscription = subscription_service.SubscriptionService.get_company_subscription(db, company.id)
    
    days_remaining = 0
    if company.subscription_end:
        delta = company.subscription_end - datetime.utcnow()
        days_remaining = max(0, delta.days)
    
    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "service_id": company.service_id,
            "is_subscription_active": company.is_subscription_active,
            "subscription_start": company.subscription_start,
            "subscription_end": company.subscription_end,
            "days_remaining": days_remaining
        },
        "subscription": subscription
    }


@router.get("/history", response_model=List[SubscriptionPaymentRead])
def get_subscription_history(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    return subscription_service.SubscriptionService.get_subscription_history(db, company.id)


@router.get("/renewal/calculate", response_model=dict)
def calculate_renewal(
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    return subscription_service.SubscriptionService.calculate_renewal_payment(db, company.id)


@router.post("/renewal", response_model=SubscriptionPaymentRead)
async def create_renewal_payment(
    payment_proof: UploadFile = File(...),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    
    file_ext = payment_proof.filename.split(".")[-1] if "." in payment_proof.filename else "jpg"
    file_name = f"payment_{company.id}_{uuid.uuid4()}.{file_ext}"
    
    try:
        from app.core.config import SUPABASE_SERVICE_KEY, SUPABASE_URL
        from supabase import create_client
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        file_content = await payment_proof.read()
        supabase.storage.from_("payments").upload(file_name, file_content)
        
    except Exception as e:
        print(f"Error uploading file: {e}")
    
    payment = subscription_service.SubscriptionService.create_renewal_payment(
        db, company.id, file_name
    )
    
    return payment


@router.get("/upgrade/calculate/{new_service_id}", response_model=dict)
def calculate_upgrade(
    new_service_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    return subscription_service.SubscriptionService.calculate_upgrade_payment(db, company.id, new_service_id)


@router.post("/upgrade/{new_service_id}", response_model=SubscriptionPaymentRead)
async def process_upgrade(
    new_service_id: int,
    payment_proof: UploadFile = File(...),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    
    file_ext = payment_proof.filename.split(".")[-1] if "." in payment_proof.filename else "jpg"
    file_name = f"upgrade_{company.id}_{uuid.uuid4()}.{file_ext}"
    
    try:
        from app.core.config import SUPABASE_SERVICE_KEY, SUPABASE_URL
        from supabase import create_client
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        file_content = await payment_proof.read()
        supabase.storage.from_("payments").upload(file_name, file_content)
        
    except Exception as e:
        print(f"Error uploading file: {e}")
    
    payment = subscription_service.SubscriptionService.process_upgrade(
        db, company.id, new_service_id, file_name
    )
    
    return payment


@router.get("/downgrade/calculate/{new_service_id}", response_model=dict)
def calculate_downgrade(
    new_service_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    return subscription_service.SubscriptionService.calculate_downgrade(db, company.id, new_service_id)


@router.post("/downgrade/{new_service_id}", response_model=dict)
def process_downgrade(
    new_service_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    company = get_current_company(current_user, db)
    company = subscription_service.SubscriptionService.process_downgrade(db, company.id, new_service_id)
    return {"message": "Downgrade procesado correctamente", "company_id": company.id}
