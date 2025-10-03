from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
import enum

if TYPE_CHECKING:
    from .user_qr_code_model import UserQRCodeModel
    from .verification_code_model import VerificationCodeModel
    from .verification_code_password_reset_model import VerificationCodePasswordResetModel
    from ..loans.loan_model import LoanModel
    from ..payments.payment_model import PaymentModel
    from ..expenses.expense_model import ExpenseModel
    from ..collection_routes.collection_route_model import CollectionRouteModel
    from ..reports.report_model import ReportModel
    from ..daily_cutoff.daily_cutoff_model import DailyCutoffModel
    from ..files.file_model import FileModel

class UserRole(str, enum.Enum):
    admin = "admin"
    employee = "employee"  # Trabajadores de la empresa

class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class UserModel(BasePayTrackModel, table=True):
    __tablename__ = "users"

    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    role: UserRole = Field(default=UserRole.employee, sa_column=Column(Enum(UserRole), nullable=False))
    
    # Información personal
    name: str = Field(description="Nombre del usuario")
    paternal_surname: str = Field(description="Apellido paterno")
    maternal_surname: str = Field(description="Apellido materno")
    national_id: str = Field(description="INE o identificación nacional")
    phone: str = Field(description="Teléfono de contacto")
    address: str = Field(description="Dirección")
    
    # Información laboral (para empleados)
    salary: Optional[Decimal] = Field(default=None, description="Salario del empleado")
    
    # Estado y verificación
    status: UserStatus = Field(default=UserStatus.active, sa_column=Column(Enum(UserStatus), nullable=False))
    
    # Campos de autenticación (mantenemos del modelo original)
    email: str = Field(index=True, unique=True, description="Email para login")
    password: str = Field(description="Contraseña hasheada")
    is_verified: bool = Field(default=False, description="Si el email está verificado")
    
    # Soft delete

    # Relaciones
    verification_codes: List["VerificationCodeModel"] = Relationship(back_populates="user")
    verification_codes_password_reset: List["VerificationCodePasswordResetModel"] = Relationship(back_populates="user")
    
    # Relaciones del sistema de préstamos
    authorized_loans: List["LoanModel"] = Relationship(back_populates="authorizer")
    payments_responsible: List["PaymentModel"] = Relationship(back_populates="responsible")
    expenses: List["ExpenseModel"] = Relationship(back_populates="responsible")
    collection_routes: List["CollectionRouteModel"] = Relationship(back_populates="employee")
    generated_reports: List["ReportModel"] = Relationship(back_populates="generator")
    daily_cutoffs: List["DailyCutoffModel"] = Relationship(back_populates="responsible")
    uploaded_files: List["FileModel"] = Relationship(back_populates="uploader")
    
    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del usuario"""
        return f"{self.name} {self.paternal_surname} {self.maternal_surname}".strip()
    
    @property
    def is_admin(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.role == UserRole.admin
    
    @property
    def is_employee(self) -> bool:
        """Verifica si el usuario es empleado"""
        return self.role == UserRole.employee
    
    @property
    def is_active(self) -> bool:
        """Verifica si el usuario está activo"""
        return self.status == UserStatus.active and self.deleted_at is None
