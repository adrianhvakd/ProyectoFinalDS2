from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database.connection import get_session
from app.schemas.user_schema import UserRead
from app.services import auth_service
from app.core.security import verify_token

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(verify_token)])

@router.get("/{user_id}", response_model=UserRead)
def get_profile(user_id: str, db: Session = Depends(get_session)):
    user = auth_service.get_user_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.patch("/{user_id}", response_model=UserRead)
def update_profile(user_id: str, data: dict, db: Session = Depends(get_session)):
    user = auth_service.update_user_profile(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="No se pudo actualizar")
    return user