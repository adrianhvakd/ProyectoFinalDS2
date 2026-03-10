from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from app.database.connection import get_session
from app.schemas.sensor_schema import SensorCreate, SensorRead, SensorUpdate, DashboardSummary
from app.services import sensor_service
from app.core.security import verify_token

router = APIRouter(prefix="/sensors", tags=["Sensors"], dependencies=[Depends(verify_token)])

@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary(company_id: Optional[int] = None, db: Session = Depends(get_session)):
    return sensor_service.get_dashboard_summary(db, company_id)

@router.post("/", response_model=SensorRead)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_session)):
    return sensor_service.create_sensor(db, sensor)

@router.get("/", response_model=List[SensorRead])
def list_sensors(company_id: Optional[int] = None, db: Session = Depends(get_session)):
    return sensor_service.get_all_sensors(db, company_id)

@router.get("/{sensor_id}", response_model=SensorRead)
def get_sensor(sensor_id: int, db: Session = Depends(get_session)):
    sensor = sensor_service.get_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor

@router.patch("/{sensor_id}", response_model=SensorRead)
def update_sensor(sensor_id: int, sensor_update: SensorUpdate, db: Session = Depends(get_session)):
    sensor = sensor_service.update_sensor(db, sensor_id, sensor_update)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor

@router.delete("/{sensor_id}")
def delete_sensor(sensor_id: int, db: Session = Depends(get_session)):
    success = sensor_service.delete_sensor(db, sensor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return {"message": "Sensor eliminado"}