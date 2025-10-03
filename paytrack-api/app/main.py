from fastapi import FastAPI
from app.api.auth.auth_router import router as auth_router
from app.api.users.user_router import router as user_router
from app.api.clients.client_router import router as client_router
from app.api.suppliers.supplier_router import router as supplier_router
from app.api.loans.loan_router import router as loan_router
from app.api.payments.payment_router import router as payment_router
from app.api.expenses.expense_router import router as expense_router

app = FastAPI(
    title="PayTrack API",
    description="API para gestión de préstamos y pagos",
    version="1.0.0"
)

# Incluir routers
app.include_router(auth_router)
app.include_router(user_router, prefix="/api/v1")
app.include_router(client_router, prefix="/api/v1")
app.include_router(supplier_router, prefix="/api/v1")
app.include_router(loan_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
app.include_router(expense_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Hello": "World"}