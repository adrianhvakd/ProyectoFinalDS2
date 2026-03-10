import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app.routers import sensor_router, reading_router, alert_router, auth_router, company_router
from app.routers import service_router, order_router, admin_router, notification_router
from app.routers import subscription_router

app = FastAPI(
    title="Sistema de Monitoreo Minero API",
    description="API para gestión de sensores, lecturas y alertas con IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensor_router.router)
app.include_router(reading_router.router)
app.include_router(alert_router.router)
app.include_router(auth_router.router)
app.include_router(company_router.router)
app.include_router(service_router.router)
app.include_router(order_router.router)
app.include_router(admin_router.router)
app.include_router(notification_router.router)
app.include_router(subscription_router.router)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "API de Monitoreo Minero funcionando correctamente"
    }