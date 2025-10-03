import requests
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

# Configuración de la API
API_BASE_URL = "http://localhost:8000/api/v1"

def test_api_connection():
    """Probar conexión con la API"""
    try:
        response = requests.get("http://localhost:8000")
        print(f"✅ Conexión exitosa - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def create_clients():
    """Crear clientes de prueba"""
    print("\n🏢 Creando clientes...")
    
    clients_data = [
        {
            "name": "Juan",
            "paternalSurname": "García",
            "maternalSurname": "López",
            "occupation": "Comerciante",
            "nationalId": "GALJ850315HDFRPN01",
            "address": "Av. Principal 123, Col. Centro",
            "phone": "5551234567",
            "birthDate": "1985-03-15",
            "notes": "Cliente confiable con historial de pagos puntuales"
        },
        {
            "name": "María",
            "paternalSurname": "Rodríguez",
            "maternalSurname": "Hernández",
            "occupation": "Profesora",
            "nationalId": "ROHM900210MDFDRR02",
            "address": "Calle Secundaria 456, Col. Educación",
            "phone": "5559876543",
            "birthDate": "1990-02-10",
            "notes": "Nueva cliente"
        },
        {
            "name": "Carlos",
            "paternalSurname": "Martínez",
            "maternalSurname": "Silva",
            "occupation": "Mecánico",
            "nationalId": "MASC880705HDFRLR03",
            "address": "Blvd. Industrial 789, Col. Trabajo",
            "phone": "5555555555",
            "birthDate": "1988-07-05"
        },
        {
            "name": "Ana",
            "paternalSurname": "Torres",
            "maternalSurname": "Gutiérrez",
            "occupation": "Doctora",
            "nationalId": "TOGA920825MDFRTN04",
            "address": "Av. Salud 321, Col. Médica",
            "phone": "5552468135",
            "birthDate": "1992-08-25",
            "notes": "Cliente VIP"
        },
        {
            "name": "Luis",
            "paternalSurname": "Vázquez",
            "maternalSurname": "Morales",
            "occupation": "Taxista",
            "nationalId": "VAML870418HDFZRS05",
            "address": "Calle Transporte 654, Col. Movilidad",
            "phone": "5557894561",
            "birthDate": "1987-04-18"
        }
    ]
    
    created_clients = []
    for client_data in clients_data:
        try:
            response = requests.post(f"{API_BASE_URL}/clients", json=client_data)
            if response.status_code == 201:
                client = response.json()["data"]
                created_clients.append(client)
                print(f"✅ Cliente creado: {client['name']} {client['paternalSurname']}")
            else:
                print(f"❌ Error creando cliente {client_data['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return created_clients

def create_suppliers():
    """Crear proveedores de prueba"""
    print("\n🏭 Creando proveedores...")
    
    suppliers_data = [
        {
            "name": "Papelería El Estudiante",
            "phone": "5551111111",
            "contact": "Roberto Pérez",
            "description": "Suministros de oficina y papelería",
            "folio": "PROV001",
            "address": "Av. Papelería 100, Col. Oficinas",
            "supplierType": "office",
            "email": "contacto@papeleriaestudiante.com",
            "website": "www.papeleriaestudiante.com",
            "taxId": "PAE850101ABC"
        },
        {
            "name": "Servicios de Limpieza Brillante",
            "phone": "5552222222",
            "contact": "Patricia Sánchez",
            "description": "Servicios de limpieza para oficinas",
            "folio": "PROV002",
            "address": "Calle Limpia 200, Col. Servicios",
            "supplierType": "service",
            "email": "info@brillante.com",
            "taxId": "SLB900202DEF"
        },
        {
            "name": "Mantenimiento TecnoFix",
            "phone": "5553333333",
            "contact": "Ingeniero Miguel Tech",
            "description": "Mantenimiento de equipos de cómputo",
            "folio": "PROV003",
            "address": "Zona Industrial 300, Col. Tecnología",
            "supplierType": "maintenance",
            "email": "soporte@tecnofix.mx",
            "website": "www.tecnofix.mx",
            "taxId": "MTF950303GHI"
        },
        {
            "name": "Cafetería Los Aromáticos",
            "phone": "5554444444",
            "contact": "Sofía Café",
            "description": "Suministro de café y snacks para oficina",
            "address": "Calle Café 400, Col. Sabores",
            "supplierType": "product",
            "email": "pedidos@losaromaticos.com",
            "taxId": "CLA880404JKL"
        },
        {
            "name": "Seguridad Integral Pro",
            "phone": "5555555555",
            "contact": "Comandante Seguro",
            "description": "Servicios de seguridad privada",
            "folio": "PROV005",
            "address": "Av. Protección 500, Col. Seguridad",
            "supplierType": "service",
            "website": "www.seguridadpro.mx",
            "taxId": "SIP920505MNO"
        }
    ]
    
    created_suppliers = []
    for supplier_data in suppliers_data:
        try:
            response = requests.post(f"{API_BASE_URL}/suppliers", json=supplier_data)
            if response.status_code == 201:
                supplier = response.json()["data"]
                created_suppliers.append(supplier)
                print(f"✅ Proveedor creado: {supplier['name']}")
            else:
                print(f"❌ Error creando proveedor {supplier_data['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return created_suppliers

def create_loans(clients):
    """Crear préstamos de prueba"""
    print("\n💰 Creando préstamos...")
    
    if len(clients) < 3:
        print("❌ No hay suficientes clientes para crear préstamos")
        return []
    
    # ID de usuario administrador temporal (deberás cambiarlo por un ID real)
    admin_user_id = str(uuid.uuid4())  # En producción, esto vendría del token JWT
    
    loans_data = [
        {
            "clientId": clients[0]["clientId"],
            "amount": 10000.00,
            "paymentCount": 12,
            "interestRate": 0.15,
            "paymentStartDate": (date.today() + timedelta(days=7)).isoformat(),
            "lateInterest": 0.05
        },
        {
            "clientId": clients[1]["clientId"],
            "amount": 25000.00,
            "paymentCount": 24,
            "interestRate": 0.12,
            "paymentStartDate": (date.today() + timedelta(days=14)).isoformat(),
            "lateInterest": 0.03
        },
        {
            "clientId": clients[2]["clientId"],
            "amount": 5000.00,
            "paymentCount": 6,
            "interestRate": 0.20,
            "paymentStartDate": (date.today() + timedelta(days=3)).isoformat(),
            "lateInterest": 0.08
        }
    ]
    
    created_loans = []
    for loan_data in loans_data:
        try:
            response = requests.post(
                f"{API_BASE_URL}/loans?authorizer_id={admin_user_id}", 
                json=loan_data
            )
            if response.status_code == 201:
                loan = response.json()["data"]
                created_loans.append(loan)
                print(f"✅ Préstamo creado: ${loan['amount']} para cliente {loan['clientId']}")
            else:
                print(f"❌ Error creando préstamo: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return created_loans

def create_expenses(suppliers):
    """Crear gastos de prueba"""
    print("\n💸 Creando gastos...")
    
    # ID de usuario administrador temporal (deberás cambiarlo por un ID real)
    admin_user_id = str(uuid.uuid4())  # En producción, esto vendría del token JWT
    
    expenses_data = [
        {
            "supplierId": suppliers[0]["supplierId"] if len(suppliers) > 0 else None,
            "expenseDate": date.today().isoformat(),
            "paymentMethod": "Transferencia bancaria",
            "description": "Compra de suministros de oficina para el mes",
            "amount": 3500.00,
            "category": "office_supplies",
            "invoiceNumber": "FAC-001-2025",
            "notes": "Papel, bolígrafos, carpetas y material de oficina"
        },
        {
            "supplierId": suppliers[1]["supplierId"] if len(suppliers) > 1 else None,
            "expenseDate": (date.today() - timedelta(days=5)).isoformat(),
            "paymentMethod": "Efectivo",
            "description": "Servicio de limpieza semanal de oficinas",
            "amount": 2800.00,
            "category": "services",
            "invoiceNumber": "SRV-002-2025"
        },
        {
            "expenseDate": (date.today() - timedelta(days=10)).isoformat(),
            "paymentMethod": "Cheque",
            "description": "Pago de renta mensual de oficina",
            "amount": 15000.00,
            "category": "rent",
            "invoiceNumber": "RNT-003-2025",
            "notes": "Renta correspondiente al mes actual"
        },
        {
            "supplierId": suppliers[2]["supplierId"] if len(suppliers) > 2 else None,
            "expenseDate": (date.today() - timedelta(days=3)).isoformat(),
            "paymentMethod": "Tarjeta de crédito",
            "description": "Mantenimiento preventivo de equipos de cómputo",
            "amount": 4500.00,
            "category": "maintenance",
            "invoiceNumber": "MNT-004-2025"
        }
    ]
    
    created_expenses = []
    for expense_data in expenses_data:
        try:
            response = requests.post(
                f"{API_BASE_URL}/expenses?responsible_id={admin_user_id}", 
                json=expense_data
            )
            if response.status_code == 201:
                expense = response.json()["data"]
                created_expenses.append(expense)
                print(f"✅ Gasto creado: ${expense['amount']} - {expense['description'][:50]}...")
            else:
                print(f"❌ Error creando gasto: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return created_expenses

def main():
    """Función principal para crear todos los datos de prueba"""
    print("🚀 Iniciando creación de datos de prueba para PayTrack API")
    print("=" * 60)
    
    # Verificar conexión
    if not test_api_connection():
        return
    
    # Crear datos de prueba
    clients = create_clients()
    suppliers = create_suppliers()
    loans = create_loans(clients)
    expenses = create_expenses(suppliers)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DATOS CREADOS:")
    print(f"👥 Clientes: {len(clients)}")
    print(f"🏭 Proveedores: {len(suppliers)}")
    print(f"💰 Préstamos: {len(loans)}")
    print(f"💸 Gastos: {len(expenses)}")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("🌐 Accede a la documentación de la API en: http://localhost:8000/docs")
    print("🔧 pgAdmin disponible en: http://localhost:8001")
    print("   📧 Email: admin@paytrack.com")
    print("   🔑 Password: admin123")

if __name__ == "__main__":
    main()