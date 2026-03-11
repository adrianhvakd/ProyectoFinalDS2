from sqlmodel import Session, select, text
from datetime import datetime, timedelta
from app.models.reading import Reading
from app.models.sensor import Sensor
from app.models.alert import Alert
from app.schemas.reading_schema import ReadingCreate
from app.services import alert_service, ai_service

ALERT_COOLDOWN_MINUTES = 5
READINGS_BETWEEN_ANALYSIS = 10

_last_analysis_count = {}


def should_create_automatic_alert(db: Session, sensor_id: int, is_over_threshold: bool) -> bool:
    cutoff_time = datetime.utcnow() - timedelta(minutes=ALERT_COOLDOWN_MINUTES)
    
    keyword = "CRÍTICO" if is_over_threshold else "fuera de rango"
    statement = (
        select(Alert)
        .join(Reading)
        .where(Reading.sensor_id == sensor_id)
        .where(Alert.timestamp >= cutoff_time)
        .where(Alert.description.contains(keyword))
        .order_by(Alert.timestamp.desc())
        .limit(1)
    )
    recent_alert = db.exec(statement).first()
    return recent_alert is None


def should_create_ai_alert(db: Session, sensor_id: int, alert_type: str) -> bool:
    cutoff_time = datetime.utcnow() - timedelta(minutes=ALERT_COOLDOWN_MINUTES)
    
    statement = (
        select(Alert)
        .join(Reading)
        .where(Reading.sensor_id == sensor_id)
        .where(Alert.timestamp >= cutoff_time)
        .where(Alert.description.contains(alert_type))
        .order_by(Alert.timestamp.desc())
        .limit(1)
    )
    recent_alert = db.exec(statement).first()
    return recent_alert is None


def process_reading(db: Session, reading_data: ReadingCreate):

    sensor = db.get(Sensor, reading_data.sensor_id)
    if not sensor:
        return None

    # Crear lectura con company_id del sensor
    reading_dict = reading_data.model_dump()
    reading_dict['company_id'] = sensor.company_id
    
    new_reading = Reading(**reading_dict)
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    is_out_of_range = (
        new_reading.value > sensor.max_threshold or 
        new_reading.value < sensor.min_threshold
    )

    if is_out_of_range:
        if should_create_automatic_alert(db, reading_data.sensor_id, new_reading.value > sensor.max_threshold):
            alert_service.create_automatic_alert(
                db=db,
                reading_value=new_reading.value,
                sensor_name=sensor.name,
                reading_id=new_reading.id,
                min_val=sensor.min_threshold,
                max_val=sensor.max_threshold,
                company_id=sensor.company_id
            )

    current_count = _last_analysis_count.get(sensor.id, 0)
    current_count += 1
    _last_analysis_count[sensor.id] = current_count

    if current_count >= READINGS_BETWEEN_ANALYSIS:
        _last_analysis_count[sensor.id] = 0
        
        statement = (
            select(Reading)
            .where(Reading.sensor_id == sensor.id)
            .order_by(Reading.timestamp.desc())
            .limit(50)
        )
        recent_readings = db.exec(statement).all()
        
        prediction = ai_service.predict_sensor_failure(
            recent_readings=recent_readings,
            max_threshold=sensor.max_threshold,
            min_threshold=sensor.min_threshold
        )
        
        stable_states = ["Estable", "Iniciando"]
        if prediction.get("status") not in stable_states:
            alert_type = prediction.get("alert_type", "PREDICCIÓN")
            if should_create_ai_alert(db, reading_data.sensor_id, alert_type):
                alert_service.create_ai_prediction_alert(
                    db=db,
                    sensor_name=sensor.name,
                    reading_id=new_reading.id,
                    ai_message=prediction.get("message", "Análisis predictivo: posible anomalía detectada."),
                    company_id=sensor.company_id
                )

    return new_reading

def get_latest_readings(db: Session, limit: int = 10):
    statement = select(Reading).order_by(Reading.timestamp.desc()).limit(limit)
    return db.exec(statement).all()

def get_trend_by_type(db: Session, sensor_type: str, hours: int = 24, company_id: int = None):
    # Normalizar tipo a minúsculas para comparar con la DB
    sensor_type_lower = sensor_type.lower()
    
    if company_id:
        try:
            company_id = int(company_id)
        except (ValueError, TypeError):
            company_id = None
    
    if company_id:
        query = text("SELECT hora, promedio FROM get_sensor_trend(:stype, :hours, :company_id)")
        params = {"stype": sensor_type_lower, "hours": hours, "company_id": company_id}
    else:
        query = text("SELECT hora, promedio FROM get_sensor_trend(:stype, :hours, NULL)")
        params = {"stype": sensor_type_lower, "hours": hours}
    
    result = db.execute(query, params).fetchall()

    return [{"hora": r.hora, "valor": r.promedio} for r in result]
