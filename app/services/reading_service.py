from sqlmodel import Session, select
from app.models.reading import Reading
from app.models.sensor import Sensor
from app.schemas.reading_schema import ReadingCreate
from app.services import alert_service, ai_service

def process_reading(db: Session, reading_data: ReadingCreate):

    sensor = db.get(Sensor, reading_data.sensor_id)
    if not sensor:
        return None

    new_reading = Reading(**reading_data.model_dump())
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    is_out_of_range = (
        new_reading.value > sensor.max_threshold or 
        new_reading.value < sensor.min_threshold
    )

    if is_out_of_range:
        alert_service.create_automatic_alert(
            db=db,
            reading_value=new_reading.value,
            sensor_name=sensor.name,
            reading_id=new_reading.id,
            min_val=sensor.min_threshold,
            max_val=sensor.max_threshold
        )


    statement = (
        select(Reading)
        .where(Reading.sensor_id == sensor.id)
        .order_by(Reading.timestamp.desc())
        .limit(10)
    )
    recent_readings = db.exec(statement).all()
    
    prediction = ai_service.predict_sensor_failure(recent_readings)
    
    if prediction["prediction"] not in ["Estable", "Iniciando"]:
        alert_service.create_ai_prediction_alert(
            db=db,
            sensor_name=sensor.name,
            reading_id=new_reading.id,
            ai_message=prediction["message"]
        )

    return new_reading

def get_latest_readings(db: Session, limit: int = 10):
    statement = select(Reading).order_by(Reading.timestamp.desc()).limit(limit)
    return db.exec(statement).all()