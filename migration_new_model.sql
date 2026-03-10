-- =============================================
-- SCRIPT DE MIGRACIÓN - NUEVO MODELO DE DATOS
-- Ejecutar en Supabase SQL Editor
-- =============================================

-- 1. Crear tabla company
CREATE TABLE IF NOT EXISTS company (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT DEFAULT 'mining',
    public_token TEXT UNIQUE DEFAULT gen_random_uuid(),
    is_public_enabled BOOLEAN DEFAULT FALSE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by TEXT REFERENCES auth.users(id)
);

-- 2. Crear tabla zone
CREATE TABLE IF NOT EXISTS zone (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#3B82F6',
    position_x FLOAT NOT NULL,
    position_y FLOAT NOT NULL,
    width FLOAT DEFAULT 10,
    height FLOAT DEFAULT 10,
    description TEXT
);

-- 3. Crear tabla service
CREATE TABLE IF NOT EXISTS service (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    features TEXT DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Crear tabla "order" (ordenes de compra)
CREATE TABLE IF NOT EXISTS "order" (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES service(id),
    company_name TEXT NOT NULL,
    company_address TEXT NOT NULL,
    company_phone TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'pending_review', 'approved', 'rejected')),
    payment_proof_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_by TEXT
);

-- 5. Crear tabla notification
CREATE TABLE IF NOT EXISTS notification (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Agregar columnas a tabla user (public.user)
ALTER TABLE public.user ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE public.user ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);

-- Verificar y agregar/modificar columna role
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user' AND table_schema = 'public' AND column_name = 'role'
    ) THEN
        ALTER TABLE public.user ADD COLUMN role TEXT DEFAULT 'user';
    ELSE
        ALTER TABLE public.user ALTER COLUMN role SET DEFAULT 'user';
    END IF;
END $$;

-- 7. Agregar columnas a tabla sensor
ALTER TABLE sensor ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);
ALTER TABLE sensor ADD COLUMN IF NOT EXISTS position_x FLOAT DEFAULT 0;
ALTER TABLE sensor ADD COLUMN IF NOT EXISTS position_y FLOAT DEFAULT 0;

-- 8. Agregar columnas a tabla alert
ALTER TABLE alert ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);

-- 9. Agregar columnas a tabla reading
ALTER TABLE reading ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);

-- 10. Insertar company inicial (para datos existentes)
INSERT INTO company (name, industry, onboarding_completed)
VALUES ('Mina Default', 'mining', TRUE)
ON CONFLICT DO NOTHING;

-- 11. Insertar servicio inicial si no existe
INSERT INTO service (name, description, price, features, is_active)
SELECT 
    'Plan Monitoreo Minero',
    'Sistema completo de monitoreo en tiempo real para minas. Incluye gestión de sensores de gas y temperatura, alertas automáticas con IA, dashboard en tiempo real y mapa interactivo.',
    0,
    '["Monitoreo en tiempo real", "Sensores de gas y temperatura", "Alertas automáticas con IA", "Dashboard interactivo", "Mapa de la mina", "Gestión de alertas", "Acceso para múltiples operadores", "Soporte 24/7"]',
    true
WHERE NOT EXISTS (SELECT 1 FROM service WHERE name = 'Plan Monitoreo Minero');

-- 12. Actualizar registros existentes con company_id
DO $$
DECLARE
    default_company_id INTEGER;
BEGIN
    SELECT id INTO default_company_id FROM company LIMIT 1;
    
    UPDATE sensor SET company_id = default_company_id WHERE company_id IS NULL;
    UPDATE alert SET company_id = default_company_id WHERE company_id IS NULL;
    UPDATE reading SET company_id = default_company_id WHERE company_id IS NULL;
    UPDATE zone SET company_id = default_company_id WHERE company_id IS NULL;
END $$;

-- =============================================
-- FUNCIONES AUXILIARES
-- =============================================

-- Función para obtener dashboard summary filtrado por company_id
CREATE OR REPLACE FUNCTION get_dashboard_summary(p_company_id INTEGER)
RETURNS TABLE (
    sensores_activos INTEGER,
    sensores_totales INTEGER,
    alertas_pendientes INTEGER,
    temperatura_promedio FLOAT
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*)::INT FROM sensor WHERE is_active = true AND company_id = p_company_id),
        (SELECT COUNT(*)::INT FROM sensor WHERE company_id = p_company_id),
        (SELECT COUNT(*)::INT FROM alert WHERE is_resolved = false AND company_id = p_company_id),
        (SELECT AVG(r.value)::float FROM reading r
         JOIN sensor s ON r.sensor_id = s.id
         WHERE s.type = 'Temperature' AND s.company_id = p_company_id
         ORDER BY r.timestamp DESC LIMIT 1);
END;
$$;

-- Función para obtener promedio de lecturas por tipo de sensor
CREATE OR REPLACE FUNCTION get_sensor_trend(
    p_sensor_type TEXT,
    p_hours_back INTEGER,
    p_company_id INTEGER
)
RETURNS TABLE (hora TEXT, promedio FLOAT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        to_char(date_trunc('hour', r.timestamp), 'HH24:MI') as hora,
        ROUND(AVG(r.value)::numeric, 2)::float as promedio
    FROM reading r
    JOIN sensor s ON r.sensor_id = s.id
    WHERE s.type = p_sensor_type
      AND r.timestamp >= NOW() - (p_hours_back || ' hours')::interval
      AND s.company_id = p_company_id
    GROUP BY date_trunc('hour', r.timestamp)
    ORDER BY date_trunc('hour', r.timestamp) ASC;
END;
$$;

-- Función para resolver alertas de un sensor
CREATE OR REPLACE FUNCTION resolve_alerts_by_sensor(p_sensor_id INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    rows_affected INT;
BEGIN
    UPDATE alert
    SET is_resolved = true
    WHERE is_resolved = false 
      AND reading_id IN (SELECT id FROM reading WHERE sensor_id = p_sensor_id);
    
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    RETURN rows_affected;
END;
$$;

-- Función para obtener última lectura de un sensor
CREATE OR REPLACE FUNCTION get_last_reading(p_sensor_id INTEGER)
RETURNS FLOAT
LANGUAGE plpgsql
AS $$
DECLARE
    last_value FLOAT;
BEGIN
    SELECT value INTO last_value
    FROM reading
    WHERE sensor_id = p_sensor_id
    ORDER BY timestamp DESC
    LIMIT 1;
    
    RETURN COALESCE(last_value, 0);
END;
$$;

-- =============================================
-- RLS (Row Level Security)
-- =============================================

ALTER TABLE company ENABLE ROW LEVEL SECURITY;
ALTER TABLE zone ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading ENABLE ROW LEVEL SECURITY;
ALTER TABLE service ENABLE ROW LEVEL SECURITY;
ALTER TABLE "order" ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification ENABLE ROW LEVEL SECURITY;

-- Políticas para company
DROP POLICY IF EXISTS "Users can view own company" ON company;
CREATE POLICY "Users can view own company" ON company
    FOR SELECT USING (id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can insert own company" ON company;
CREATE POLICY "Users can insert own company" ON company
    FOR INSERT WITH CHECK (created_by = auth.uid());

DROP POLICY IF EXISTS "Users can update own company" ON company;
CREATE POLICY "Users can update own company" ON company
    FOR UPDATE USING (id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

-- Políticas para service (público para leer)
DROP POLICY IF EXISTS "Anyone can view services" ON service;
CREATE POLICY "Anyone can view services" ON service
    FOR SELECT USING (is_active = true);

-- Políticas para "order"
DROP POLICY IF EXISTS "Users can view own orders" ON "order";
CREATE POLICY "Users can view own orders" ON "order"
    FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Anyone can insert orders" ON "order";
CREATE POLICY "Anyone can insert orders" ON "order"
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Políticas para notification
DROP POLICY IF EXISTS "Users can view own notifications" ON notification;
CREATE POLICY "Users can view own notifications" ON notification
    FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own notifications" ON notification;
CREATE POLICY "Users can update own notifications" ON notification
    FOR UPDATE USING (user_id = auth.uid());

-- Políticas para sensor (actualizadas con company_id)
DROP POLICY IF EXISTS "Users can view own sensors" ON sensor;
CREATE POLICY "Users can view own sensors" ON sensor
    FOR SELECT USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can insert own sensors" ON sensor;
CREATE POLICY "Users can insert own sensors" ON sensor
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can update own sensors" ON sensor;
CREATE POLICY "Users can update own sensors" ON sensor
    FOR UPDATE USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can delete own sensors" ON sensor;
CREATE POLICY "Users can delete own sensors" ON sensor
    FOR DELETE USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

-- Políticas para zone
DROP POLICY IF EXISTS "Users can view own zones" ON zone;
CREATE POLICY "Users can view own zones" ON zone
    FOR SELECT USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can insert own zones" ON zone;
CREATE POLICY "Users can insert own zones" ON zone
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can update own zones" ON zone;
CREATE POLICY "Users can update own zones" ON zone
    FOR UPDATE USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can delete own zones" ON zone;
CREATE POLICY "Users can delete own zones" ON zone
    FOR DELETE USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

-- Políticas para alert
DROP POLICY IF EXISTS "Users can view own alerts" ON alert;
CREATE POLICY "Users can view own alerts" ON alert
    FOR SELECT USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can insert own alerts" ON alert;
CREATE POLICY "Users can insert own alerts" ON alert
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can update own alerts" ON alert;
CREATE POLICY "Users can update own alerts" ON alert
    FOR UPDATE USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

-- Políticas para reading
DROP POLICY IF EXISTS "Users can view own readings" ON reading;
CREATE POLICY "Users can view own readings" ON reading
    FOR SELECT USING (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

DROP POLICY IF EXISTS "Users can insert own readings" ON reading;
CREATE POLICY "Users can insert own readings" ON reading
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM public.user WHERE id = auth.uid()));

-- =============================================
-- ACTUALIZAR FUNCION DE REGISTRO DE USUARIO
-- =============================================

-- Actualizar trigger function para incluir phone
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user (
        id, 
        email, 
        username, 
        full_name,
        phone,
        role, 
        is_active, 
        created_at
    )
    VALUES (
        new.id,
        new.email,
        COALESCE(new.raw_user_meta_data->>'username', SPLIT_PART(new.email, '@', 1)),
        new.raw_user_meta_data->>'full_name',
        new.raw_user_meta_data->>'phone',
        COALESCE(new.raw_user_meta_data->>'role', 'user'),
        true,
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================
-- VERIFICACIÓN
-- =============================================
-- Ejecutar estas consultas para verificar:

-- SELECT * FROM service;
-- SELECT * FROM "order";
-- SELECT * FROM notification;
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user';
-- SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public';
