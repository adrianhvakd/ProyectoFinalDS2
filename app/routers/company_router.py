from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.database.connection import get_session
from app.schemas.company_schema import CompanyCreate, CompanyUpdate, CompanyRead
from app.models.company import Company
from app.models.user import User

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyRead)
def create_company(company: CompanyCreate, session: Session = Depends(get_session)):
    db_company = Company.model_validate(company)
    session.add(db_company)
    session.commit()
    session.refresh(db_company)
    return db_company


@router.get("/", response_model=List[CompanyRead])
def get_companies(session: Session = Depends(get_session)):
    companies = session.exec(select(Company)).all()
    return companies


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, company_update: CompanyUpdate, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company_data = company_update.model_dump(exclude_unset=True)
    for key, value in company_data.items():
        setattr(company, key, value)
    
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


@router.delete("/{company_id}")
def delete_company(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    session.delete(company)
    session.commit()
    return {"message": "Company deleted successfully"}


@router.get("/{company_id}/onboarding-status")
def get_onboarding_status(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"onboarding_completed": company.onboarding_completed}


@router.patch("/{company_id}/complete-onboarding")
def complete_onboarding(company_id: int, session: Session = Depends(get_session)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.onboarding_completed = True
    session.add(company)
    session.commit()
    return {"message": "Onboarding completed", "onboarding_completed": True}
