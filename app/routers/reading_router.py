from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session
from typing import List, Optional
from app.database.connection import get_session
from app.schemas.reading_schema import ReadingCreate, ReadingRead, TrendPoint
from app.services import reading_service
from app.core.security import verify_token
from app.models.sensor import Sensor

router = APIRouter(prefix="/readings", tags=["Readings"])

@router.post("/", response_model=ReadingRead)
def add_reading(reading: ReadingCreate, db: Session = Depends(get_session), x_arduino_key: Optional[str] = Header(None)):

    if not x_arduino_key:
        raise HTTPException(status_code=403, detail="Se requiere API key")

    sensor = db.query(Sensor).filter(Sensor.api_key == x_arduino_key).first()
    if not sensor:
        raise HTTPException(status_code=403, detail="API key inválida")

    if sensor.id != reading.sensor_id:
        raise HTTPException(status_code=403, detail="El sensor_id no coincide con la API key")

    result = reading_service.process_reading(db, reading)
    if not result:
        raise HTTPException(status_code=404, detail="Sensor no registrado")
    return result

@router.get("/latest", response_model=List[ReadingRead])
def get_recent(limit: int = 20, db: Session = Depends(get_session), user_info: dict = Depends(verify_token)):
    return reading_service.get_latest_readings(db, limit)

@router.get("/trend/{sensor_type}", response_model=List[TrendPoint])
async def get_sensor_trend(sensor_type: str, hours: int = 24, db: Session = Depends(get_session), user_info: dict = Depends(verify_token)):
    return reading_service.get_trend_by_type(db, sensor_type, hours)