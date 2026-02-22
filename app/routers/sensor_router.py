from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.database.connection import get_session
from app.schemas.sensor_schema import SensorCreate, SensorRead
from app.services import sensor_service
from app.core.security import verify_token

router = APIRouter(prefix="/sensors", tags=["Sensors"], dependencies=[Depends(verify_token)])

@router.post("/", response_model=SensorRead)
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_session)):
    return sensor_service.create_sensor(db, sensor)

@router.get("/", response_model=List[SensorRead])
def list_sensors(db: Session = Depends(get_session)):
    return sensor_service.get_all_sensors(db)

@router.get("/{sensor_id}", response_model=SensorRead)
def get_sensor(sensor_id: int, db: Session = Depends(get_session)):
    sensor = sensor_service.get_sensor_by_id(db, sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor