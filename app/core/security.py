from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client
from sqlmodel import Session
from app.core.config import SUPABASE_URL, SUPABASE_ANON_KEY
from app.models.user import User
from app.database.connection import engine

security = HTTPBearer()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    try:
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado o token inválido")
        
        user_id = user_response.user.id
        
        with Session(engine) as db:
            db_user = db.get(User, user_id)
            if not db_user:
                raise HTTPException(status_code=401, detail="Usuario no encontrado en la base de datos")
            
            return {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username,
                "full_name": db_user.full_name,
                "role": db_user.role,
                "company_id": db_user.company_id,
                "is_active": db_user.is_active,
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en verify_token: {str(e)}")
        raise HTTPException(status_code=401, detail="No autorizado")