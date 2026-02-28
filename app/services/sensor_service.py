from sqlmodel import Session, select, text
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

def get_dashboard_summary(db: Session):
    query = text("SELECT * FROM get_mining_dashboard_stats()")
    result = db.execute(query).fetchone()

    if not result:
        return {
            "gases_criticos": 0,
            "temperatura_promedio": 0.0,
            "sensores_activos": 0,
            "sensores_totales": 0,
            "alertas_pendientes": 0
        }

    return {
        "gases_criticos": getattr(result, "gases_criticos", 0),
        "temperatura_promedio": getattr(result, "temperatura_promedio", 0.0),
        "sensores_activos": getattr(result, "sensores_activos_conteo", 0),
        "sensores_totales": getattr(result, "sensores_totales", 0),
        "alertas_pendientes": getattr(result, "alertas_pendientes", 0)
    }