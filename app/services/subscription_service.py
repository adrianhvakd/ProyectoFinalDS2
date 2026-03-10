from sqlmodel import Session, select
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.models.company import Company
from app.models.service import Service
from app.models.subscription_payment import SubscriptionPayment
from app.models.user import User
from app.models.notification import Notification


class SubscriptionService:
    
    @staticmethod
    def create_initial_subscription(db: Session, company_id: int, service_id: int, user_id: str) -> SubscriptionPayment:
        service = db.get(Service, service_id)
        if not service:
            raise ValueError("Servicio no encontrado")
        
        now = datetime.utcnow()
        period_end = now + timedelta(days=service.duration_days)
        
        subscription_payment = SubscriptionPayment(
            company_id=company_id,
            service_id=service_id,
            period_start=now,
            period_end=period_end,
            amount=service.price,
            status="approved",
            payment_type="initial",
            paid_at=now
        )
        
        db.add(subscription_payment)
        
        company = db.get(Company, company_id)
        if company:
            company.service_id = service_id
            company.subscription_start = now
            company.subscription_end = period_end
            company.is_subscription_active = True
            db.add(company)
        
        db.commit()
        db.refresh(subscription_payment)
        return subscription_payment
    
    @staticmethod
    def get_company_subscription(db: Session, company_id: int) -> Optional[SubscriptionPayment]:
        statement = select(SubscriptionPayment).where(
            SubscriptionPayment.company_id == company_id
        ).order_by(SubscriptionPayment.created_at.desc())
        return db.exec(statement).first()
    
    @staticmethod
    def get_subscription_history(db: Session, company_id: int) -> list[SubscriptionPayment]:
        statement = select(SubscriptionPayment).where(
            SubscriptionPayment.company_id == company_id
        ).order_by(SubscriptionPayment.created_at.desc())
        return db.exec(statement).all()
    
    @staticmethod
    def calculate_renewal_payment(db: Session, company_id: int) -> Dict[str, Any]:
        company = db.get(Company, company_id)
        if not company or not company.service_id:
            raise ValueError("Compañía o servicio no encontrado")
        
        service = db.get(Service, company.service_id)
        if not service:
            raise ValueError("Servicio no encontrado")
        
        days_remaining = 0
        if company.subscription_end:
            delta = company.subscription_end - datetime.utcnow()
            days_remaining = max(0, delta.days)
        
        return {
            "service_id": service.id,
            "service_name": service.name,
            "price": service.price,
            "days_remaining": days_remaining,
            "total_to_pay": service.price
        }
    
    @staticmethod
    def create_renewal_payment(db: Session, company_id: int, payment_proof_filename: str) -> SubscriptionPayment:
        company = db.get(Company, company_id)
        if not company or not company.service_id:
            raise ValueError("Compañía o servicio no encontrado")
        
        service = db.get(Service, company.service_id)
        if not service:
            raise ValueError("Servicio no encontrado")
        
        period_start = company.subscription_end + timedelta(days=1) if company.subscription_end else datetime.utcnow()
        period_end = period_start + timedelta(days=service.duration_days)
        
        subscription_payment = SubscriptionPayment(
            company_id=company_id,
            service_id=company.service_id,
            period_start=period_start,
            period_end=period_end,
            amount=service.price,
            status="pending_review",
            payment_type="renewal",
            payment_proof_filename=payment_proof_filename
        )
        
        db.add(subscription_payment)
        db.commit()
        db.refresh(subscription_payment)
        return subscription_payment
    
    @staticmethod
    def calculate_upgrade_payment(db: Session, company_id: int, new_service_id: int) -> Dict[str, Any]:
        company = db.get(Company, company_id)
        if not company or not company.service_id:
            raise ValueError("Compañía o servicio no encontrado")
        
        current_service = db.get(Service, company.service_id)
        new_service = db.get(Service, new_service_id)
        
        if not current_service or not new_service:
            raise ValueError("Servicio no encontrado")
        
        if new_service.plan_level <= current_service.plan_level:
            raise ValueError("El nuevo plan debe ser de nivel superior")
        
        days_remaining = 0
        if company.subscription_end:
            delta = company.subscription_end - datetime.utcnow()
            days_remaining = max(0, delta.days)
        
        daily_rate_current = current_service.price / current_service.duration_days if current_service.duration_days > 0 else 0
        credit_from_remaining_days = days_remaining * daily_rate_current
        
        amount_to_pay = max(0, new_service.price - credit_from_remaining_days)
        
        return {
            "current_service": {
                "id": current_service.id,
                "name": current_service.name,
                "price": current_service.price,
                "days_remaining": days_remaining,
                "credit": credit_from_remaining_days
            },
            "new_service": {
                "id": new_service.id,
                "name": new_service.name,
                "price": new_service.price
            },
            "amount_to_pay": amount_to_pay,
            "new_period_days": new_service.duration_days + days_remaining
        }
    
    @staticmethod
    def process_upgrade(db: Session, company_id: int, new_service_id: int, payment_proof_filename: str) -> SubscriptionPayment:
        company = db.get(Company, company_id)
        if not company or not company.service_id:
            raise ValueError("Compañía o servicio no encontrado")
        
        new_service = db.get(Service, new_service_id)
        if not new_service:
            raise ValueError("Servicio no encontrado")
        
        if new_service.plan_level <= company.service_id:
            raise ValueError("El nuevo plan debe ser de nivel superior")
        
        days_remaining = 0
        if company.subscription_end:
            delta = company.subscription_end - datetime.utcnow()
            days_remaining = max(0, delta.days)
        
        daily_rate_current = 0
        current_service = db.get(Service, company.service_id)
        if current_service:
            daily_rate_current = current_service.price / current_service.duration_days if current_service.duration_days > 0 else 0
        
        credit_from_remaining_days = days_remaining * daily_rate_current
        amount_to_pay = max(0, new_service.price - credit_from_remaining_days)
        
        now = datetime.utcnow()
        new_period_end = now + timedelta(days=new_service.duration_days + days_remaining)
        
        subscription_payment = SubscriptionPayment(
            company_id=company_id,
            service_id=new_service_id,
            period_start=now,
            period_end=new_period_end,
            amount=amount_to_pay,
            status="pending_review",
            payment_type="upgrade",
            payment_proof_filename=payment_proof_filename
        )
        
        db.add(subscription_payment)
        
        company.previous_service_id = company.service_id
        company.service_id = new_service_id
        company.subscription_end = new_period_end
        
        db.add(company)
        db.commit()
        db.refresh(subscription_payment)
        return subscription_payment
    
    @staticmethod
    def calculate_downgrade(db: Session, company_id: int, new_service_id: int) -> Dict[str, Any]:
        company = db.get(Company, company_id)
        if not company or not company.service_id:
            raise ValueError("Compañía o servicio no encontrado")
        
        current_service = db.get(Service, company.service_id)
        new_service = db.get(Service, new_service_id)
        
        if not current_service or not new_service:
            raise ValueError("Servicio no encontrado")
        
        if new_service.plan_level >= current_service.plan_level:
            raise ValueError("El nuevo plan debe ser de nivel inferior")
        
        days_remaining = 0
        if company.subscription_end:
            delta = company.subscription_end - datetime.utcnow()
            days_remaining = max(0, delta.days)
        
        return {
            "current_service": {
                "id": current_service.id,
                "name": current_service.name,
                "price": current_service.price
            },
            "new_service": {
                "id": new_service.id,
                "name": new_service.name,
                "price": new_service.price
            },
            "days_remaining": days_remaining,
            "effective_date": company.subscription_end.isoformat() if company.subscription_end else None,
            "message": f"El cambio a {new_service.name} se aplicará el {company.subscription_end.strftime('%d/%m/%Y') if company.subscription_end else 'próximo período'}"
        }
    
    @staticmethod
    def process_downgrade(db: Session, company_id: int, new_service_id: int) -> Company:
        company = db.get(Company, company_id)
        if not company or not company.service_id:
            raise ValueError("Compañía o servicio no encontrado")
        
        new_service = db.get(Service, new_service_id)
        if not new_service:
            raise ValueError("Servicio no encontrado")
        
        if new_service.plan_level >= company.service_id:
            raise ValueError("El nuevo plan debe ser de nivel inferior")
        
        company.previous_service_id = company.service_id
        company.service_id = new_service_id
        
        db.add(company)
        db.commit()
        db.refresh(company)
        return company
    
    @staticmethod
    def approve_payment(db: Session, payment_id: int, admin_id: str) -> SubscriptionPayment:
        payment = db.get(SubscriptionPayment, payment_id)
        if not payment:
            raise ValueError("Pago no encontrado")
        
        if payment.status != "pending_review":
            raise ValueError("Este pago ya fue procesado")
        
        payment.status = "approved"
        payment.paid_at = datetime.utcnow()
        payment.approved_by = admin_id
        
        company = db.get(Company, payment.company_id)
        if company:
            company.is_subscription_active = True
            
            if payment.payment_type in ["upgrade", "initial"]:
                company.subscription_start = payment.period_start
                company.subscription_end = payment.period_end
            
            if payment.payment_type == "renewal":
                old_end = company.subscription_end
                company.subscription_start = old_end + timedelta(days=1) if old_end else payment.period_start
                company.subscription_end = payment.period_end
            
            db.add(company)
            
            users_statement = select(User).where(User.company_id == company.id)
            users = db.exec(users_statement).all()
            for user in users:
                user.is_active = True
                db.add(user)
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def reject_payment(db: Session, payment_id: int, admin_id: str) -> SubscriptionPayment:
        payment = db.get(SubscriptionPayment, payment_id)
        if not payment:
            raise ValueError("Pago no encontrado")
        
        if payment.status != "pending_review":
            raise ValueError("Este pago ya fue procesado")
        
        payment.status = "rejected"
        payment.approved_by = admin_id
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment
    
    @staticmethod
    def process_subscription_expiry(db: Session, company_id: int) -> Dict[str, Any]:
        company = db.get(Company, company_id)
        if not company:
            raise ValueError("Compañía no encontrada")
        
        now = datetime.utcnow()
        
        if company.subscription_end and now >= company.subscription_end:
            if company.is_subscription_active:
                company.is_subscription_active = False
                
                users_statement = select(User).where(User.company_id == company.id)
                users = db.exec(users_statement).all()
                for user in users:
                    user.is_active = False
                    db.add(user)
                
                notification = Notification(
                    user_id=company.created_by,
                    type="subscription_expired",
                    message="Tu suscripción ha vencido y ha sido suspendida. Por favor contacta al administrador."
                )
                db.add(notification)
                
                db.add(company)
                db.commit()
                
                return {
                    "status": "expired",
                    "is_active": company.is_subscription_active
                }
        
        return {
            "status": "active",
            "is_active": company.is_subscription_active
        }
    
    @staticmethod
    def check_subscriptions_expiring_soon(db: Session, days_threshold: int = 7) -> list[Company]:
        from datetime import timedelta
        target_date = datetime.utcnow() + timedelta(days=days_threshold)
        
        statement = select(Company).where(
            Company.subscription_end <= target_date,
            Company.is_subscription_active == True,
            Company.subscription_end >= datetime.utcnow()
        )
        return db.exec(statement).all()
