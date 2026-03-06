from pydantic import BaseModel
from typing import Optional

class SensorCreate(BaseModel):
    name: str
    type: str
    location: str
    description: Optional[str] = None
    min_threshold: float
    max_threshold: float
    position_x: float = 0
    position_y: float = 0
    company_id: int

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    is_active: Optional[bool] = None

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