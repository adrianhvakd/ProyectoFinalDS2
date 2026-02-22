from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

# 1. IMPORTA SQLMODEL Y TU ENGINE
from sqlmodel import SQLModel
from app.database.connection import engine

# 2. IMPORTA TODOS TUS MODELOS (Crucial para que detecte las tablas)
from app.models.sensor import Sensor
from app.models.reading import Reading
from app.models.alert import Alert
from app.models.user import User

# Acceso a la configuración del archivo .ini
config = context.config

# Configuración de logs
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. VINCULA LOS METADATOS DE SQLMODEL
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Modo offline: genera scripts SQL sin conectarse a la DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Modo online: se conecta a Postgres y crea las tablas."""
    
    # Usamos directamente el 'engine' que definiste en connection.py
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()