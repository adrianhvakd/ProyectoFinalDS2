from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.database.connection import get_session
from app.schemas.order_schema import OrderRead
from app.schemas.user_schema import UserRead
from app.schemas.subscription_payment_schema import SubscriptionPaymentRead
from app.models.order import Order
from app.models.user import User
from app.models.notification import Notification
from app.models.company import Company
from app.models.service import Service
from app.models.subscription_payment import SubscriptionPayment
from app.services import subscription_service
from app.core.security import verify_token
from datetime import datetime
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])


def check_admin(current_user: dict = Depends(verify_token)):
    if current_user['role'] != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden acceder")
    return current_user


@router.get("/orders", response_model=list[OrderRead])
def get_all_orders(
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    statement = select(Order).order_by(Order.created_at.desc())
    orders = db.exec(statement).all()
    return orders


@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


@router.post("/orders/{order_id}/approve", response_model=OrderRead)
def approve_order(
    order_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order.status not in ["pending", "pending_review"]:
        raise HTTPException(status_code=400, detail="Este pedido no puede ser aprobado")
    
    company = Company(
        name=order.company_name,
        industry="mining",
        created_by=order.user_id
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    user = db.get(User, order.user_id)
    if user:
        user.role = "operator"
        user.company_id = company.id
        db.add(user)
    
    subscription_service.SubscriptionService.create_initial_subscription(
        db, company.id, order.service_id, order.user_id
    )
    
    order.status = "approved"
    order.approved_by = current_user['id']
    order.updated_at = datetime.utcnow()
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    notification = Notification(
        user_id=order.user_id,
        type="order_approved",
        message=f"¡Tu pedido #{order.id} ha sido aprobado! Ya puedes acceder al panel de operador."
    )
    db.add(notification)
    db.commit()
    
    return order


@router.post("/orders/{order_id}/reject", response_model=OrderRead)
def reject_order(
    order_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order.status not in ["pending", "pending_review"]:
        raise HTTPException(status_code=400, detail="Este pedido no puede ser rechazado")
    
    order.status = "rejected"
    order.updated_at = datetime.utcnow()
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    notification = Notification(
        user_id=order.user_id,
        type="order_rejected",
        message=f"Tu pedido #{order.id} ha sido rechazado. Por favor contacta al administrador."
    )
    db.add(notification)
    db.commit()
    
    return order


@router.get("/users", response_model=list[UserRead])
def get_all_users(
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    statement = select(User).where(User.id != current_user['id']).order_by(User.created_at.desc())
    users = db.exec(statement).all()
    return users


@router.patch("/users/{user_id}/toggle", response_model=UserRead)
def toggle_user_active(
    user_id: str,
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")
    
    user = db.get(User, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.id == current_user['id']:
        raise HTTPException(status_code=400, detail="No puedes desactivarte a ti mismo")
    
    user.is_active = not user.is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    total_users = db.exec(select(func.count(User.id))).one()
    total_orders = db.exec(select(func.count(Order.id))).one()
    pending_orders = db.exec(select(func.count(Order.id)).where(Order.status == "pending")).one()
    pending_review_orders = db.exec(select(func.count(Order.id)).where(Order.status == "pending_review")).one()
    approved_orders = db.exec(select(func.count(Order.id)).where(Order.status == "approved")).one()
    rejected_orders = db.exec(select(func.count(Order.id)).where(Order.status == "rejected")).one()
    
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "pending_orders": pending_orders + pending_review_orders,
        "approved_orders": approved_orders,
        "rejected_orders": rejected_orders
    }


@router.get("/subscription-payments", response_model=list[SubscriptionPaymentRead])
def get_all_subscription_payments(
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    statement = select(SubscriptionPayment).order_by(SubscriptionPayment.created_at.desc())
    payments = db.exec(statement).all()
    return payments


@router.get("/subscription-payments/pending", response_model=list[SubscriptionPaymentRead])
def get_pending_subscription_payments(
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    statement = select(SubscriptionPayment).where(
        SubscriptionPayment.status == "pending_review"
    ).order_by(SubscriptionPayment.created_at.desc())
    payments = db.exec(statement).all()
    return payments


@router.post("/subscription-payments/{payment_id}/approve", response_model=SubscriptionPaymentRead)
def approve_subscription_payment(
    payment_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    try:
        payment = subscription_service.SubscriptionService.approve_payment(
            db, payment_id, current_user['id']
        )
        
        notification = Notification(
            user_id=payment.company.created_by if payment.company else None,
            type="subscription_payment_approved",
            message=f"Tu pago de suscripción ha sido aprobado. Tu servicio está activo."
        )
        db.add(notification)
        db.commit()
        
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/subscription-payments/{payment_id}/reject", response_model=SubscriptionPaymentRead)
def reject_subscription_payment(
    payment_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(check_admin)
):
    try:
        payment = subscription_service.SubscriptionService.reject_payment(
            db, payment_id, current_user['id']
        )
        
        notification = Notification(
            user_id=payment.company.created_by if payment.company else None,
            type="subscription_payment_rejected",
            message=f"Tu pago de suscripción ha sido rechazado. Por favor contacta al administrador."
        )
        db.add(notification)
        db.commit()
        
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
