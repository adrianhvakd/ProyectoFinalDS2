from app.database.connection import get_session
from app.models.service import Service
from sqlmodel import select

def seed_services():
    session = next(get_session())
    
    existing = session.exec(select(Service)).first()
    if existing:
        print("Service already exists, skipping seed")
        return
    
    service = Service(
        name="Plan Monitoreo Minero",
        description="Sistema completo de monitoreo en tiempo real para minas. Incluye gestión de sensores de gas y temperatura, alertas automáticas con IA, dashboard en tiempo real y mapa interactivo.",
        price=0,
        features='["Monitoreo en tiempo real", "Sensores de gas y temperatura", "Alertas automáticas con IA", "Dashboard interactivo", "Mapa de la mina", "Gestión de alertas", "Acceso para múltiples operadores", "Soporte 24/7"]',
        is_active=True
    )
    
    session.add(service)
    session.commit()
    session.refresh(service)
    print(f"Service created: {service.name} (ID: {service.id})")

if __name__ == "__main__":
    seed_services()
