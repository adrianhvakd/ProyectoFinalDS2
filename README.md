# Sistema de Monitoreo Minero con IA - Backend

Plataforma de monitoreo en tiempo real diseñada para la detección de riesgos en entornos mineros. El sistema recolecta datos de sensores, los procesa mediante un motor de IA para predecir anomalías y gestiona alertas críticas.

---

## Características Principales

- **API de Alto Rendimiento:** Construida con FastAPI y Python 3.10 o superior.
- **Inteligencia Artificial:** Motor predictivo que analiza tendencias de datos para generar alertas preventivas.
- **Seguridad Híbrida:**
  - *Frontend (Next.js):* Protegido con JWT mediante Supabase Auth.
  - *Hardware (Arduino/ESP32):* Validación mediante API Keys para asegurar la integridad de las lecturas.
- **Base de Datos:** Integración con PostgreSQL mediante Supabase utilizando SQLModel.
- **Documentación Automática:** Swagger y ReDoc integrados.

---

## Stack Tecnológico

| Componente     | Tecnología                        |
|----------------|-----------------------------------|
| Lenguaje       | Python 3.10+                      |
| Framework      | FastAPI                           |
| ORM            | SQLModel (SQLAlchemy + Pydantic)  |
| Base de Datos  | PostgreSQL (Supabase)             |
| Seguridad      | PyJWT y Supabase Auth             |
| Migraciones    | Alembic                           |

---

## Estructura del Proyecto

```
backend/
├── app/
│   ├── core/          # Configuración global y seguridad
│   ├── database/      # Conexión y sesión de DB
│   ├── models/        # Modelos de SQLModel (Tablas)
│   ├── schemas/       # Esquemas de validación Pydantic
│   ├── services/      # Lógica de negocio e IA
│   ├── routers/       # Endpoints de la API
│   └── utils/         # Funciones auxiliares
├── migrations/        # Archivos de gestión de base de datos
├── .env               # Variables de entorno
├── main.py            # Punto de entrada de la aplicación
└── simulate_arduino.py  # Script de prueba para hardware
```

---

## Instalación y Configuración

**1. Clonar el repositorio y entrar al directorio:**
```bash
git clone <url-del-repositorio>
cd backend
```

**2. Crear y activar entorno virtual:**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instalar dependencias:**
```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno:**

Crea un archivo `.env` en la raíz del backend con el siguiente contenido:
```env
USER_DB=postgres
PASSWORD_DB=tu_password
HOST_DB=db.tu_proyecto.supabase.co
PORT_DB=5432
DB_NAME=postgres
SUPABASE_JWT_SECRET=tu_secreto_jwt
ARDUINO_KEY=tu_clave_secreta
```

**5. Ejecutar el servidor:**
```bash
uvicorn app.main:app --reload
```

---

## Simulación de Hardware

Para probar el motor de IA sin hardware real, ejecuta el simulador:

```bash
python simulate_arduino.py
```

El script enviará una serie de lecturas con tendencia al alza para verificar la generación automática de alertas preventivas en la base de datos.

---

## Documentación de la API

El sistema ofrece documentación interactiva en las siguientes rutas:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

Para descargar la especificación OpenAPI en formato JSON:

```
http://127.0.0.1:8000/openapi.json
```

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**.