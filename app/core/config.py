import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("USER_DB")
DB_PASSWORD = os.getenv("PASSWORD_DB")
DB_HOST = os.getenv("HOST_DB")
DB_PORT = os.getenv("PORT_DB")
DB_NAME = os.getenv("DB_NAME")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
