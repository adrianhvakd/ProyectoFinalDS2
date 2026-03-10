from sqlmodel import Session, select, text
from typing import Optional
from app.models.sensor import Sensor
from app.models.alert import Alert
from app.models.reading import Reading
from app.schemas.sensor_schema import SensorCreate, SensorUpdate


def create_sensor(db: Session, sensor_data: SensorCreate):
    db_sensor = Sensor(**sensor_data.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


def get_all_sensors(db: Session, company_id: Optional[int] = None):
    query = select(Sensor)
    if company_id:
        query = query.where(Sensor.company_id == company_id)
    return db.exec(query).all()


def get_sensor_by_id(db: Session, sensor_id: int):
    return db.get(Sensor, sensor_id)


def update_sensor(db: Session, sensor_id: int, sensor_update: SensorUpdate):
    sensor = db.get(Sensor, sensor_id)
    if not sensor:
        return None
    
    update_data = sensor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(sensor, key, value)
    
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


def delete_sensor(db: Session, sensor_id: int):
    sensor = db.get(Sensor, sensor_id)
    if not sensor:
        return False
    
    db.delete(sensor)
    db.commit()
    return True


def get_dashboard_summary(db: Session, company_id: Optional[int] = None):
    sensors_query = select(Sensor)
    if company_id:
        sensors_query = sensors_query.where(Sensor.company_id == company_id)
    
    sensors = db.exec(sensors_query).all()
    
    if not sensors:
        return {
            "gases_criticos": 0,
            "temperatura_promedio": 0.0,
            "sensores_activos": 0,
            "sensores_totales": 0,
            "alertas_pendientes": 0
        }
    
    sensores_activos = sum(1 for s in sensors if s.is_active)
    sensores_totales = len(sensors)
    
    alertas_query = select(Alert).where(Alert.is_resolved == False)
    if company_id:
        alertas_query = alertas_query.where(Alert.company_id == company_id)
    alertas_pendientes = len(db.exec(alertas_query).all())
    
    gas_sensors = [s for s in sensors if s.type.lower() == "gas"]
    temp_sensors = [s for s in sensors if s.type.lower() == "temperatura"]
    
    gases_criticos = len(gas_sensors)
    temperatura_promedio = 0.0
    if temp_sensors:
        temperatura_promedio = sum(s.max_threshold for s in temp_sensors) / len(temp_sensors)
    
    return {
        "gases_criticos": float(gases_criticos),
        "temperatura_promedio": float(round(temperatura_promedio, 2)),
        "sensores_activos": sensores_activos,
        "sensores_totales": sensores_totales,
        "alertas_pendientes": alertas_pendientes
    }