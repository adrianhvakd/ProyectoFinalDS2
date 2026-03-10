from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.database.connection import get_session
from app.schemas.alert_schema import AlertRead
from app.services import alert_service
from app.core.security import verify_token

router = APIRouter(prefix="/alerts", tags=["Alerts"], dependencies=[Depends(verify_token)])

@router.get("/unresolved", response_model=List[AlertRead])
def get_active_alerts(db: Session = Depends(get_session)):
    return alert_service.get_unresolved_alerts(db)