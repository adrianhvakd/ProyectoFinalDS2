from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user_schema import UserRead

def get_user_profile(db: Session, user_id: str):
    return db.get(User, user_id)

def update_user_profile(db: Session, user_id: str, data_to_update: dict):

    db_user = db.get(User, user_id)
    if not db_user:
        return None
    
    user_data = data_to_update
    for key, value in user_data.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def set_user_status(db: Session, user_id: str, active: bool):
    db_user = db.get(User, user_id)
    if db_user:
        db_user.is_active = active
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user