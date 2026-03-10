from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database.connection import get_session
from app.schemas.service_schema import ServiceRead
from app.models.service import Service

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=list[ServiceRead])
def get_services(db: Session = Depends(get_session)):
    statement = select(Service).where(Service.is_active == True)
    services = db.exec(statement).all()
    return services


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_session)):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service
