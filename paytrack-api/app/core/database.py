from typing import Generator, Annotated

from fastapi import Depends
from sqlalchemy.sql import text
from sqlmodel import SQLModel, create_engine, Session
from .settings import settings

# Importa todos los modelos principales para evitar errores de mapeo
from app.models.users.user_model import UserModel
from app.models.users.verification_code_model import VerificationCodeModel
from app.models.users.verification_code_password_reset_model import VerificationCodePasswordResetModel
from app.models.clients.client_model import ClientModel
from app.models.clients.client_financial_history_model import ClientFinancialHistoryModel
from app.models.suppliers.supplier_model import SupplierModel
from app.models.loans.loan_model import LoanModel
from app.models.payments.payment_model import PaymentModel
from app.models.expenses.expense_model import ExpenseModel
from app.models.collection_routes.collection_route_model import CollectionRouteModel
from app.models.daily_cutoff.daily_cutoff_model import DailyCutoffModel
from app.models.reports.report_model import ReportModel
from app.models.files.file_model import FileModel


engine = create_engine(settings.DATABASE_URL_EFFECTIVE, pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    """Yields a database session for use in FastAPI endpoints."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def create_db_and_tables():
    """Creates the database and tables if they don't exist, but should be replaced with migrations."""
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_db)]
