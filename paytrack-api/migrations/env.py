from logging.config import fileConfig
import os
from pathlib import Path
from dotenv import load_dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Importa settings desde tu app
from app.core.settings import settings

# Importa los modelos para que entren al metadata
from app.models.users.user_model import UserModel
from app.models.users.verification_code_model import VerificationCodeModel
from app.models.users.verification_code_password_reset_model import VerificationCodePasswordResetModel
from app.models.clients.client_model import ClientModel
from app.models.clients.client_financial_history_model import ClientFinancialHistoryModel
from app.models.loans.loan_model import LoanModel
from app.models.payments.payment_model import PaymentModel
from app.models.expenses.expense_model import ExpenseModel
from app.models.suppliers.supplier_model import SupplierModel
from app.models.files.file_model import FileModel
from app.models.collection_routes.collection_route_model import CollectionRouteModel
from app.models.reports.report_model import ReportModel
from app.models.daily_cutoff.daily_cutoff_model import DailyCutoffModel

# Carga el .env desde el root del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# Usa la URL desde settings
database_url = os.getenv("DATABASE_URL", "").strip()
if not database_url:
    try:
        database_url = getattr(settings, "DATABASE_URL", "") or getattr(settings, "DATABASE_URL_EFFECTIVE", "")
    except Exception:
        database_url = ""
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada. Exporta la URL o configúrala en .env.")

# Alembic config
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# Logging desde alembic.ini (opcional)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
