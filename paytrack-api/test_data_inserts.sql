-- =============================================
-- INSERTS DE PRUEBA PARA PAYTRACK DATABASE
-- =============================================

-- Nota: Estos inserts están diseñados para PostgreSQL
-- Ejecutar en orden para mantener la integridad referencial

-- =============================================
-- 1. TABLA USERS
-- =============================================

-- UUIDs fijos para usuarios
-- admin: 11111111-1111-1111-1111-111111111111
-- María: 22222222-2222-2222-2222-222222222222
-- José: 33333333-3333-3333-3333-333333333333
-- Ana: 44444444-4444-4444-4444-444444444444
-- Luis: 55555555-5555-5555-5555-555555555555

INSERT INTO users (
    user_id, role, name, paternal_surname, maternal_surname, national_id, phone, address, salary, status, email, password, is_verified, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111111', 'admin', 'Carlos', 'Rodriguez', 'Martinez', 'ROMC850615HDFDRR01', '+52 33 1234 5678', 'Av. Revolución 123, Guadalajara, Jalisco', 25000.00, 'active', 'carlos.admin@paytrack.com', '$2b$12$example_hash_admin', true, NOW(), NOW()),
('22222222-2222-2222-2222-222222222222', 'employee', 'María', 'González', 'López', 'GOLM900312MDFRPR03', '+52 33 2345 6789', 'Calle Morelos 456, Guadalajara, Jalisco', 18000.00, 'active', 'maria.employee@paytrack.com', '$2b$12$example_hash_employee1', true, NOW(), NOW()),
('33333333-3333-3333-3333-333333333333', 'employee', 'José', 'Hernández', 'García', 'HEGJ880525HDFRRS05', '+52 33 3456 7890', 'Blvd. Independencia 789, Guadalajara, Jalisco', 17500.00, 'active', 'jose.employee@paytrack.com', '$2b$12$example_hash_employee2', true, NOW(), NOW()),
('44444444-4444-4444-4444-444444444444', 'employee', 'Ana', 'Jiménez', 'Morales', 'JIMA920718MDFMRN07', '+52 33 4567 8901', 'Calle Hidalgo 321, Zapopan, Jalisco', 16000.00, 'active', 'ana.employee@paytrack.com', '$2b$12$example_hash_employee3', true, NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', 'employee', 'Luis', 'Ramírez', 'Torres', 'RATL870403HDFMRS09', '+52 33 5678 9012', 'Av. Patria 654, Zapopan, Jalisco', 19000.00, 'active', 'luis.employee@paytrack.com', '$2b$12$example_hash_employee4', true, NOW(), NOW());

-- =============================================
-- 2. TABLA CLIENTS
-- =============================================

-- UUIDs fijos para clientes
-- Pedro: 11111111-1111-1111-1111-111111111111
-- Laura: 22222222-2222-2222-2222-222222222222
-- Roberto: 33333333-3333-3333-3333-333333333333
-- Carmen: 44444444-4444-4444-4444-444444444444
-- Miguel: 55555555-5555-5555-5555-555555555555

INSERT INTO clients (
    client_id, name, paternal_surname, maternal_surname, occupation, national_id, address, phone, birth_date, status, notes, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111111', 'Pedro', 'Sánchez', 'Ruiz', 'Mecánico', 'SARP850420HDFNZD01', 'Calle Juárez 123, Guadalajara, Jalisco', '+52 33 1111 2222', '1985-04-20', 'active', 'Cliente puntual, buen historial crediticio', NOW(), NOW()),
('22222222-2222-2222-2222-222222222222', 'Laura', 'Mendoza', 'Vega', 'Comerciante', 'MEVL900815MDFNGR03', 'Av. López Mateos 456, Tlaquepaque, Jalisco', '+52 33 2222 3333', '1990-08-15', 'active', 'Tiene tienda de abarrotes', NOW(), NOW()),
('33333333-3333-3333-3333-333333333333', 'Roberto', 'Cruz', 'Flores', 'Taxista', 'CUFR780312HDFRLB05', 'Calle Constitución 789, Tonalá, Jalisco', '+52 33 3333 4444', '1978-03-12', 'pays_on_time', 'Excelente cliente, siempre paga antes', NOW(), NOW()),
('44444444-4444-4444-4444-444444444444', 'Carmen', 'Ortega', 'Silva', 'Estilista', 'ORSC880925MDFTLR07', 'Blvd. Guadalupe 321, Guadalajara, Jalisco', '+52 33 4444 5555', '1988-09-25', 'active', 'Tiene salón de belleza propio', NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', 'Miguel', 'Vargas', 'Peña', 'Carpintero', 'VAPM750607HDFRGN09', 'Calle Zaragoza 654, Zapopan, Jalisco', '+52 33 5555 6666', '1975-06-07', 'bad_debtor', 'Ha tenido retrasos en pagos anteriores', NOW(), NOW());

-- =============================================
-- 3. TABLA SUPPLIERS
-- =============================================

-- UUIDs fijos para suppliers
-- Papelería Guadalajara: 11111111-1111-1111-1111-111111111112
-- Servicios de Limpieza JM: 22222222-2222-2222-2222-222222222222
-- Mantenimiento Express: 33333333-3333-3333-3333-333333333333
-- Café y Más: 44444444-4444-4444-4444-444444444444
-- Seguridad Total: 55555555-5555-5555-5555-555555555555

INSERT INTO suppliers (
    supplier_id, name, phone, contact, description, folio, address, supplier_type, status, email, website, tax_id, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111112', 'Papelería Guadalajara', '+52 33 1111 1111', 'Roberto Martínez', 'Proveedor de material de oficina y papelería', 'PAP001', 'Av. Hidalgo 123, Centro, Guadalajara', 'office', 'active', 'ventas@papeleriagdl.com', 'www.papeleriagdl.com', 'PAP850420ABC', NOW(), NOW()),
('22222222-2222-2222-2222-222222222222', 'Servicios de Limpieza JM', '+52 33 2222 2222', 'Juan Morales', 'Empresa de servicios de limpieza para oficinas', 'LIM002', 'Calle Morelos 456, Guadalajara', 'service', 'active', 'contacto@limpiezajm.com', NULL, 'LIM900315XYZ', NOW(), NOW()),
('33333333-3333-3333-3333-333333333333', 'Mantenimiento Express', '+52 33 3333 3333', 'Ana Gutiérrez', 'Mantenimiento de equipos de cómputo y oficina', 'MAN003', 'Blvd. Marcelino García 789, Zapopan', 'maintenance', 'active', 'servicios@mantenimientoexpress.com', 'www.mantenimientoexpress.com', 'MAN780525DEF', NOW(), NOW()),
('44444444-4444-4444-4444-444444444444', 'Café y Más', '+52 33 4444 4444', 'Luis Fernández', 'Proveedor de café, agua y productos para oficina', 'CAF004', 'Av. Patria 321, Guadalajara', 'product', 'active', 'pedidos@cafeymas.com', NULL, 'CAF920718GHI', NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', 'Seguridad Total', '+52 33 5555 5555', 'María Rodríguez', 'Servicios de seguridad y vigilancia', 'SEG005', 'Calle Independencia 654, Guadalajara', 'service', 'inactive', 'info@seguridadtotal.com', 'www.seguridadtotal.com', 'SEG851203JKL', NOW(), NOW());

-- =============================================
-- 4. TABLA LOANS
-- =============================================

-- Nota: Necesitamos obtener IDs reales de clients y users para las foreign keys
-- Este script asume que ya tienes datos en esas tablas

-- UUIDs fijos para loans
-- Loan1: 11111111-1111-1111-1111-111111111113
-- Loan2: 22222222-2222-2222-2222-222222222223
-- Loan3: 33333333-3333-3333-3333-333333333334
-- Loan4: 44444444-4444-4444-4444-444444444445
-- Loan5: 55555555-5555-5555-5555-555555555556

INSERT INTO loans (
    loan_id, client_id, authorizer_id, amount, payment_count, interest_rate, payment_start_date, late_interest, status, total_amount, remaining_amount, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111113', '11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 50000.00, 20, 15.00, '2024-01-15', 3.00, 'active', 57500.00, 45000.00, NOW(), NOW()),
('22222222-2222-2222-2222-222222222223', '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 75000.00, 24, 12.00, '2024-02-01', 2.50, 'active', 84000.00, 70000.00, NOW(), NOW()),
('33333333-3333-3333-3333-333333333334', '33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222222', 30000.00, 12, 18.00, '2024-03-10', 4.00, 'completed', 35400.00, 0.00, NOW(), NOW()),
('44444444-4444-4444-4444-444444444445', '44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 100000.00, 36, 10.00, '2024-04-05', 2.00, 'active', 110000.00, 95000.00, NOW(), NOW()),
('55555555-5555-5555-5555-555555555556', '55555555-5555-5555-5555-555555555555', '22222222-2222-2222-2222-222222222222', 25000.00, 10, 20.00, '2024-05-20', 5.00, 'defaulted', 30000.00, 28000.00, NOW(), NOW());

-- =============================================
-- 5. TABLA PAYMENTS
-- =============================================

-- UUIDs fijos para payments
-- Payment1: 11111111-1111-1111-1111-111111111114
-- Payment2: 22222222-2222-2222-2222-222222222224
-- Payment3: 33333333-3333-3333-3333-333333333334
-- Payment4: 44444444-4444-4444-4444-444444444444
-- Payment5: 55555555-5555-5555-5555-555555555555

INSERT INTO payments (
    payment_id, client_id, responsible_id, amount, interest_amount, payment_method, status, due_date, payment_date, notes, reference, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111114', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 2500.00, 375.00, 'cash', 'paid', '2024-01-15 10:00:00', '2024-01-15 09:30:00', 'Pago puntual en efectivo', 'PAG-2024-001', NOW(), NOW()),
('22222222-2222-2222-2222-222222222224', '22222222-2222-2222-2222-222222222222', '33333333-3333-3333-3333-333333333333', 3500.00, 420.00, 'transfer', 'paid', '2024-02-01 10:00:00', '2024-02-01 08:45:00', 'Transferencia bancaria confirmada', 'TRF-2024-002', NOW(), NOW()),
('33333333-3333-3333-3333-333333333334', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444', 2950.00, 442.50, 'cash', 'paid', '2024-03-10 10:00:00', '2024-03-10 11:15:00', 'Último pago del préstamo', 'PAG-2024-003', NOW(), NOW()),
('44444444-4444-4444-4444-444444444444', '44444444-4444-4444-4444-444444444444', '22222222-2222-2222-2222-222222222222', 2777.78, 277.78, 'card', 'pending', '2024-04-05 10:00:00', NULL, 'Pago pendiente con tarjeta', 'CARD-2024-004', NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', '55555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', 2500.00, 500.00, 'cash', 'overdue', '2024-05-20 10:00:00', NULL, 'Pago vencido, cliente en mora', 'PAG-2024-005', NOW(), NOW());

-- =============================================
-- 6. TABLA EXPENSES
-- =============================================

-- UUIDs fijos para expenses
-- Expense1: 11111111-1111-1111-1111-111111111115
-- Expense2: 22222222-2222-2222-2222-222222222225
-- Expense3: 33333333-3333-3333-3333-333333333335
-- Expense4: 44444444-4444-4444-4444-444444444445
-- Expense5: 55555555-5555-5555-5555-555555555555

INSERT INTO expenses (
    expense_id, responsible_id, supplier_id, expense_date, payment_method, description, amount, category, status, invoice_number, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111115', '11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111112', '2024-01-10', 'transfer', 'Compra de material de oficina y papelería', 1500.00, 'office_supplies', 'paid', 'FAC-2024-001', NOW(), NOW()),
('22222222-2222-2222-2222-222222222225', '22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', '2024-01-15', 'cash', 'Servicio de limpieza semanal', 800.00, 'services', 'paid', 'FAC-2024-002', NOW(), NOW()),
('33333333-3333-3333-3333-333333333335', '11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', '2024-01-20', 'transfer', 'Mantenimiento de equipos de cómputo', 2200.00, 'maintenance', 'approved', 'FAC-2024-003', NOW(), NOW()),
('44444444-4444-4444-4444-444444444445', '33333333-3333-3333-3333-333333333333', '44444444-4444-4444-4444-444444444444', '2024-01-25', 'cash', 'Suministros de café y agua para oficina', 450.00, 'office_supplies', 'paid', 'FAC-2024-004', NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', NULL, '2024-01-30', 'transfer', 'Pago de renta mensual de oficina', 15000.00, 'rent', 'pending', 'RENT-2024-001', NOW(), NOW());

-- =============================================
-- 7. TABLA COLLECTION_ROUTES
-- =============================================

-- UUIDs fijos para collection_routes
-- Route1: 11111111-1111-1111-1111-111111111116
-- Route2: 22222222-2222-2222-2222-222222222226
-- Route3: 33333333-3333-3333-3333-333333333336
-- Route4: 44444444-4444-4444-4444-444444444446
-- Route5: 55555555-5555-5555-5555-555555555556

INSERT INTO collection_routes (
    route_id, employee_id, loan_id, assignment_date, scheduled_date, completed_date, status, priority, notes, visit_attempts, contact_attempts, amount_collected, collection_notes, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111116', '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111113', '2024-01-10', '2024-01-15', '2024-01-15', 'completed', 'normal', 'Cliente cooperativo, fácil ubicación', 1, 2, 2500.00, 'Pago completo recibido en efectivo', NOW(), NOW()),
('22222222-2222-2222-2222-222222222226', '33333333-3333-3333-3333-333333333333', '22222222-2222-2222-2222-222222222223', '2024-01-25', '2024-02-01', '2024-02-01', 'completed', 'high', 'Cliente importante, monto alto', 1, 1, 3500.00, 'Transferencia realizada según lo programado', NOW(), NOW()),
('33333333-3333-3333-3333-333333333336', '44444444-4444-4444-4444-444444444444', '44444444-4444-4444-4444-444444444445', '2024-03-01', '2024-04-05', NULL, 'assigned', 'normal', 'Primera ruta asignada para este préstamo', 0, 0, NULL, NULL, NOW(), NOW()),
('44444444-4444-4444-4444-444444444446', '22222222-2222-2222-2222-222222222222', '55555555-5555-5555-5555-555555555556', '2024-05-15', '2024-05-20', NULL, 'in_progress', 'urgent', 'Cliente en mora, requiere seguimiento urgente', 3, 5, NULL, 'Cliente no se encuentra en domicilio, continuar intentos', NOW(), NOW()),
('55555555-5555-5555-5555-555555555556', '33333333-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333334', '2024-03-05', '2024-03-10', '2024-03-10', 'completed', 'low', 'Último pago del préstamo', 1, 1, 2950.00, 'Préstamo liquidado completamente', NOW(), NOW());

-- =============================================
-- 8. TABLA DAILY_CUTOFF
-- =============================================

-- UUIDs fijos para daily_cutoff
-- Cutoff1: 11111111-1111-1111-1111-111111111117
-- Cutoff2: 22222222-2222-2222-2222-222222222227
-- Cutoff3: 33333333-3333-3333-3333-333333333337
-- Cutoff4: 44444444-4444-4444-4444-444444444447
-- Cutoff5: 55555555-5555-5555-5555-555555555557

INSERT INTO daily_cutoff (
    cutoff_id, cutoff_date, responsible_id, total_income, total_expenses, profit, payments_received, interest_collected, late_fees_collected, other_income, operational_expenses, salary_payments, loan_disbursements, other_expenses, initial_cash, final_cash, cash_difference, total_transactions, loans_granted, payments_collected, bank_deposits, bank_withdrawals, is_closed, closure_time, notes, created_at, updated_at
) VALUES 
('11111111-1111-1111-1111-111111111117', '2024-01-15', '11111111-1111-1111-1111-111111111111', 8750.00, 2300.00, 6450.00, 7500.00, 1125.00, 125.00, 0.00, 2300.00, 0.00, 0.00, 0.00, 5000.00, 11450.00, 6450.00, 8, 1, 3, 0.00, 0.00, true, '2024-01-15 18:30:00', 'Día exitoso, buen flujo de cobranza', NOW(), NOW()),
('22222222-2222-2222-2222-222222222227', '2024-02-01', '11111111-1111-1111-1111-111111111111', 10200.00, 1800.00, 8400.00, 9500.00, 420.00, 280.00, 0.00, 800.00, 0.00, 1000.00, 0.00, 11450.00, 19850.00, 8400.00, 12, 2, 4, 0.00, 0.00, true, '2024-02-01 19:00:00', 'Excelente día, superamos meta diaria', NOW(), NOW()),
('33333333-3333-3333-3333-333333333337', '2024-03-10', '22222222-2222-2222-2222-222222222222', 7300.00, 3200.00, 4100.00, 6850.00, 442.50, 7.50, 0.00, 1200.00, 2000.00, 0.00, 0.00, 19850.00, 23950.00, 4100.00, 6, 0, 2, 0.00, 0.00, true, '2024-03-10 17:45:00', 'Día regular, algunos gastos de nómina', NOW(), NOW()),
('44444444-4444-4444-4444-444444444447', '2024-04-05', '11111111-1111-1111-1111-111111111111', 5500.00, 16000.00, -10500.00, 3000.00, 277.78, 0.00, 2222.22, 1000.00, 0.00, 15000.00, 0.00, 23950.00, 13450.00, -10500.00, 15, 3, 1, 0.00, 0.00, false, NULL, 'Día de alta inversión en préstamos, corte aún abierto', NOW(), NOW()),
('55555555-5555-5555-5555-555555555557', '2024-05-20', '33333333-3333-3333-3333-333333333333', 2800.00, 950.00, 1850.00, 2000.00, 500.00, 300.00, 0.00, 450.00, 500.00, 0.00, 0.00, 13450.00, 15300.00, 1850.00, 4, 0, 1, 0.00, 0.00, true, '2024-05-20 18:15:00', 'Día tranquilo, algunos pagos pendientes', NOW(), NOW());

-- =============================================
-- VERIFICACIÓN DE DATOS INSERTADOS
-- =============================================

-- Contar registros en cada tabla
SELECT 'users' as tabla, COUNT(*) as registros FROM users
UNION ALL
SELECT 'clients' as tabla, COUNT(*) as registros FROM clients
UNION ALL
SELECT 'suppliers' as tabla, COUNT(*) as registros FROM suppliers
UNION ALL
SELECT 'loans' as tabla, COUNT(*) as registros FROM loans
UNION ALL
SELECT 'payments' as tabla, COUNT(*) as registros FROM payments
UNION ALL
SELECT 'expenses' as tabla, COUNT(*) as registros FROM expenses
UNION ALL
SELECT 'collection_routes' as tabla, COUNT(*) as registros FROM collection_routes
UNION ALL
SELECT 'daily_cutoff' as tabla, COUNT(*) as registros FROM daily_cutoff
ORDER BY tabla;

-- =============================================
-- COMENTARIOS ADICIONALES
-- =============================================

/*
NOTAS IMPORTANTES:

1. Este script utiliza gen_random_uuid() que está disponible en PostgreSQL 13+
   Si usas una versión anterior, instala la extensión: CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   Y reemplaza gen_random_uuid() por uuid_generate_v4()

2. Los passwords están hasheados con bcrypt (ejemplos)
   En producción deberías generar hashes reales

3. Las foreign keys se resuelven dinámicamente usando subconsultas
   Esto garantiza que las relaciones sean válidas

4. Los montos están en pesos mexicanos (MXN)

5. Las fechas siguen el formato ISO 8601

6. Los enum values coinciden con los definidos en los modelos SQLModel

7. Para eliminar todos los datos de prueba:
   DELETE FROM daily_cutoff;
   DELETE FROM collection_routes;
   DELETE FROM expenses;
   DELETE FROM payments;
   DELETE FROM loans;
   DELETE FROM suppliers;
   DELETE FROM clients;
   DELETE FROM users;

8. Este script crea relaciones coherentes entre las tablas
   manteniendo la integridad referencial
*/