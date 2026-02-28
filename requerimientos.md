# Requerimientos para Generar Diagrama de Clases PlantUML

## Proyecto: Sistema de Monitoreo Minero con IA

**Stack Tecnológico:** FastAPI + Python + SQLModel + PostgreSQL (Supabase) + scikit-learn

---

## Contexto del Proyecto

Este backend es un sistema de monitoreo en tiempo real diseñado para la detección de riesgos en entornos mineros. El sistema recolecta datos de sensores (temperatura, gases, vibración), los procesa mediante un motor de IA para predecir anomalías y gestiona alertas críticas.

### Arquitectura General

El proyecto sigue una **arquitectura limpia (clean architecture)** con las siguientes capas:

1. **Models (Capa de Datos)** - Modelos SQLModel que representan las tablas de la base de datos PostgreSQL/Supabase
2. **Schemas (Capa de Validación)** - Esquemas Pydantic para validación de datos entrantes y salientes
3. **Services (Capa de Negocio)** - Lógica de negocio incluyendo el motor de IA predictivo
4. **Routers (Capa de Presentación)** - Endpoints de la API REST
5. **Core (Configuración)** - Configuración global y seguridad
6. **Database (Persistencia)** - Conexión a la base de datos

---

## Entidades Principales

| Entidad | Descripción | Atributos principales |
|---------|-------------|---------------------|
| **User** | Usuario del sistema (operadores, administradores) | id, username, email, full_name, role, is_active, created_at |
| **Sensor** | Dispositivo físico que mide variables ambientales | id, name, type, location, description, min_threshold, max_threshold, is_active |
| **Reading** | Lectura individual de un sensor en un momento dado | id, value, timestamp, sensor_id |
| **Alert** | Alerta generada por umbral excedido o predicción de IA | id, description, severity, timestamp, is_resolved, reading_id |

---

## Relaciones entre Entidades

- **Sensor** 1:N **Reading** (Un sensor puede tener muchas lecturas)
- **Reading** 1:1 **Alert** (Una lectura puede generar una alerta)
- **User** no tiene relación directa con las demás entidades en el modelo de datos

---

## Servicios Principales

| Servicio | Responsabilidad |
|----------|-----------------|
| **auth_service** | Gestión de perfiles de usuario (obtener, actualizar, estado) |
| **sensor_service** | CRUD de sensores y generación de estadísticas del dashboard |
| **reading_service** | Procesamiento de lecturas, validación de umbrales, integración con IA |
| **alert_service** | Creación de alertas (automáticas y predichas por IA), consulta de alertas pendientes |
| **ai_service** | Motor predictivo usando Regresión Lineal de scikit-learn para detectar fallas inminentes |

---

## Seguridad

- **Frontend → API**: Autenticación mediante JWT de Supabase (verificado en `verify_token`)
- **Hardware (Arduino/ESP32) → API**: Validación mediante API Key en header `X-Arduino-Key`

---

## Instrucciones para PlantUML

1. **Usar diagrama de clases** (`@startuml` ... `@enduml`)
2. **Organizar por paquetes** que representen las capas:
   - Models (Capa de Datos)
   - Schemas (Capa de Validación)
   - Services (Capa de Negocio)
   - Routers (Capa de Presentación)
   - Core (Configuración)
   - Main (Aplicación)
3. **Mostrar relaciones** entre clases usando flechas de dependencia (`..>`, `-->`)
4. **Incluir herencia** entre schemas (`<|--`)
5. **Ocultar círculo** central de los diamonds (`hide circle`)
6. **Usar tema plain** para mejor compatibilidad

---

## Endpoints Principales

| Router | Prefijo | Métodos principales |
|--------|---------|---------------------|
| auth_router | /users | GET (perfil), PATCH (actualizar) |
| sensor_router | /sensors | GET (listar, dashboard), POST (crear) |
| reading_router | /readings | POST (enviar lectura), GET (últimas, tendencias) |
| alert_router | /alerts | GET (pendientes) |
