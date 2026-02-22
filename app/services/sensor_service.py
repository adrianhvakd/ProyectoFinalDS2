from sqlmodel import Session, select
from app.models.sensor import Sensor
from app.schemas.sensor_schema import SensorCreate

def create_sensor(db: Session, sensor_data: SensorCreate):
    db_sensor = Sensor(**sensor_data.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def get_all_sensors(db: Session):
    return db.exec(select(Sensor)).all()

def get_sensor_by_id(db: Session, sensor_id: int):
    return db.get(Sensor, sensor_id)