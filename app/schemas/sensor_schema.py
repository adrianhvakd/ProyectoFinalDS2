from pydantic import BaseModel
from typing import Optional

class SensorCreate(BaseModel):
    name: str
    type: str
    location: str
    min_threshold: float
    max_threshold: float

class SensorRead(SensorCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    gases_criticos: float | None
    temperatura_promedio: float | None
    sensores_activos: int
    sensores_totales: int
    alertas_pendientes: int