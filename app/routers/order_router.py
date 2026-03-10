from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from app.database.connection import get_session
from app.schemas.order_schema import OrderCreate, OrderRead, OrderUpdate
from app.models.order import Order
from app.models.user import User
from app.models.notification import Notification
from app.models.service import Service
from app.core.security import verify_token
from datetime import datetime
import uuid

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderRead)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    service = db.get(Service, order_data.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    order = Order(
        user_id=current_user['id'],
        service_id=order_data.service_id,
        company_name=order_data.company_name,
        company_address=order_data.company_address,
        company_phone=order_data.company_phone,
        status="pending"
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    notification = Notification(
        user_id=current_user['id'],
        type="order_created",
        message=f"Tu pedido #{order.id} ha sido creado y está pendiente de pago."
    )
    db.add(notification)
    db.commit()
    
    return order


@router.get("/me", response_model=list[OrderRead])
def get_my_orders(
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    statement = select(Order).where(Order.user_id == current_user['id']).order_by(Order.created_at.desc())
    orders = db.exec(statement).all()
    return orders


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    
    return order


@router.post("/{order_id}/payment", response_model=OrderRead)
async def upload_payment_proof(
    order_id: int,
    payment_proof: UploadFile = File(...),
    db: Session = Depends(get_session),
    current_user: dict = Depends(verify_token)
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Este pedido ya fue procesado")
    
    file_ext = payment_proof.filename.split(".")[-1] if "." in payment_proof.filename else "jpg"
    file_name = f"payment_{order_id}_{uuid.uuid4()}.{file_ext}"
    
    try:
        from app.core.config import SUPABASE_SERVICE_KEY, SUPABASE_URL
        from supabase import create_client
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        file_content = await payment_proof.read()
        supabase.storage.from_("payments").upload(file_name, file_content)
        
        order.payment_proof_filename = file_name
    except Exception as e:
        print(f"Error uploading file: {e}")
        order.payment_proof_filename = file_name
    
    order.status = "pending_review"
    order.updated_at = datetime.utcnow()
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    notification = Notification(
        user_id=current_user['id'],
        type="payment_uploaded",
        message=f"Comprobante de pago subido para el pedido #{order.id}. Estado: En revisión."
    )
    db.add(notification)
    db.commit()
    
    return order
