from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_ANON_KEY

security = HTTPBearer()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    try:
        user = supabase.auth.get_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado o token inválido")
            
        return user.user
    except Exception as e:
        print(f"Error con SDK de Supabase: {str(e)}")
        raise HTTPException(status_code=401, detail="No autorizado")