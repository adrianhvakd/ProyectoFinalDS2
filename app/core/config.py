import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("USER_DB")
DB_PASSWORD = os.getenv("PASSWORD_DB")
DB_HOST = os.getenv("HOST_DB")
DB_PORT = os.getenv("PORT_DB")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")