from sqlmodel import Session, select
from app.models.alert import Alert

def create_automatic_alert(db: Session, reading_value: float, sensor_name: str, reading_id: int, min_val: float, max_val: float):
    description = (
        f"CRÍTICO en {sensor_name}: valor {reading_value} fuera de rango. "
        f"Límites: {min_val} - {max_val}."
    )
    new_alert = Alert(
        description=description,
        severity="high",
        reading_id=reading_id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

def create_ai_prediction_alert(db: Session, sensor_name: str, reading_id: int, ai_message: str):
    description = f"PREDICCIÓN IA en {sensor_name}: {ai_message}"
    
    new_alert = Alert(
        description=description,
        severity="medium",
        reading_id=reading_id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

def get_unresolved_alerts(db: Session):
    statement = select(Alert).where(Alert.is_resolved == False)
    return db.exec(statement).all()