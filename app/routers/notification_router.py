from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database.connection import get_session
from app.models.notification import Notification
from app.core.security import verify_token

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
def get_notifications(
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    statement = select(Notification).where(
        Notification.user_id == current_user['id']
    ).order_by(Notification.created_at.desc()).limit(50)
    notifications = db.exec(statement).all()
    return notifications


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    notification = db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    if notification.user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta notificación")
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.patch("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    statement = select(Notification).where(
        Notification.user_id == current_user['id'],
        Notification.is_read == False
    )
    notifications = db.exec(statement).all()
    
    for notification in notifications:
        notification.is_read = True
        db.add(notification)
    
    db.commit()
    
    return {"message": f"{len(notifications)} notificaciones marcadas como leídas"}
