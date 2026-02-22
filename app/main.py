import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.routers import sensor_router, reading_router, alert_router, auth_router

app = FastAPI(
    title="Sistema de Monitoreo Minero API",
    description="API para gestión de sensores, lecturas y alertas con IA",
    version="1.0.0"
)

app.include_router(sensor_router.router)
app.include_router(reading_router.router)
app.include_router(alert_router.router)
app.include_router(auth_router.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "API de Monitoreo Minero funcionando correctamente"
    }