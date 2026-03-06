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

-- 3. Agregar columnas a tabla user
ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);

-- 4. Agregar columnas a tabla sensor
ALTER TABLE sensor ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);
ALTER TABLE sensor ADD COLUMN IF NOT EXISTS position_x FLOAT DEFAULT 0;
ALTER TABLE sensor ADD COLUMN IF NOT EXISTS position_y FLOAT DEFAULT 0;

-- 5. Agregar columnas a tabla alert
ALTER TABLE alert ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);

-- 6. Agregar columnas a tabla reading
ALTER TABLE reading ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES company(id);

-- 7. Insertar company inicial (para datos existentes)
INSERT INTO company (name, industry, onboarding_completed)
VALUES ('Mina Default', 'mining', TRUE)
ON CONFLICT DO NOTHING;

-- 8. Obtener el ID de la company insertada
DO $$
DECLARE
    company_id INTEGER;
BEGIN
    SELECT id INTO company_id FROM company LIMIT 1;
    
    -- 9. Actualizar sensores existentes con company_id
    UPDATE sensor SET company_id = company_id WHERE company_id IS NULL;
    
    -- 10. Actualizar usuarios existentes (opcional, si hay usuarios)
    -- UPDATE auth.users SET company_id = company_id WHERE company_id IS NULL;
END $$;

-- 11. Habilitar RLS (Row Level Security)
ALTER TABLE company ENABLE ROW LEVEL SECURITY;
ALTER TABLE zone ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensor ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading ENABLE ROW LEVEL SECURITY;

-- 12. Políticas RLS para company
CREATE POLICY "Users can view own company" ON company
    FOR SELECT USING (id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can insert own company" ON company
    FOR INSERT WITH CHECK (created_by = auth.uid());

CREATE POLICY "Users can update own company" ON company
    FOR UPDATE USING (id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

-- 13. Políticas RLS para sensor
CREATE POLICY "Users can view own sensors" ON sensor
    FOR SELECT USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can insert own sensors" ON sensor
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can update own sensors" ON sensor
    FOR UPDATE USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can delete own sensors" ON sensor
    FOR DELETE USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

-- 14. Políticas RLS para zone
CREATE POLICY "Users can view own zones" ON zone
    FOR SELECT USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can insert own zones" ON zone
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can update own zones" ON zone
    FOR UPDATE USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can delete own zones" ON zone
    FOR DELETE USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

-- 15. Políticas RLS para alert
CREATE POLICY "Users can view own alerts" ON alert
    FOR SELECT USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can insert own alerts" ON alert
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can update own alerts" ON alert
    FOR UPDATE USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

-- 16. Políticas RLS para reading
CREATE POLICY "Users can view own readings" ON reading
    FOR SELECT USING (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

CREATE POLICY "Users can insert own readings" ON reading
    FOR INSERT WITH CHECK (company_id IN (SELECT company_id FROM auth.users WHERE id = auth.uid()));

-- =============================================
-- VERIFICACIÓN
-- =============================================
-- Ejecutar estas consultas para verificar:

-- SELECT * FROM company;
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'sensor';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'zone';
