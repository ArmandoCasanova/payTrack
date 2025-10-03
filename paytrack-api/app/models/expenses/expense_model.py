from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
import enum

if TYPE_CHECKING:
    from app.models.users.user_model import UserModel
    from app.models.suppliers.supplier_model import SupplierModel

class ExpenseStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    paid = "paid"
    rejected = "rejected"

class ExpenseCategory(str, enum.Enum):
    office_supplies = "office_supplies"
    maintenance = "maintenance"
    services = "services"
    rent = "rent"
    utilities = "utilities"
    salaries = "salaries"
    marketing = "marketing"
    travel = "travel"
    other = "other"

class ExpenseModel(BasePayTrackModel, table=True):
    __tablename__ = "expenses"

    expense_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Relaciones
    responsible_id: UUID = Field(foreign_key="users.user_id", description="ID del usuario responsable")
    supplier_id: Optional[UUID] = Field(default=None, foreign_key="suppliers.supplier_id", description="ID del proveedor (opcional)")
    
    # Información del egreso
    expense_date: date = Field(description="Fecha del egreso")
    payment_method: str = Field(description="Método de pago utilizado")
    description: str = Field(description="Descripción del egreso")
    amount: Decimal = Field(description="Monto del egreso")
    
    # Clasificación
    category: ExpenseCategory = Field(default=ExpenseCategory.other, sa_column=Column(Enum(ExpenseCategory), nullable=False))
    status: ExpenseStatus = Field(default=ExpenseStatus.pending, sa_column=Column(Enum(ExpenseStatus), nullable=False))
    
    # Información adicional
    invoice_number: Optional[str] = Field(default=None, description="Número de factura")
    receipt_path: Optional[str] = Field(default=None, description="Ruta del comprobante")
    notes: Optional[str] = Field(default=None, description="Notas adicionales")
    
    # Soft delete

    # Relaciones
    # responsible: "UserModel" = Relationship(back_populates="expenses")
    # supplier: Optional["SupplierModel"] = Relationship(back_populates="expenses")
    
    @property
    def is_paid(self) -> bool:
        """Verifica si el egreso está pagado"""
        return self.status == ExpenseStatus.paid
    
    @property
    def is_pending(self) -> bool:
        """Verifica si el egreso está pendiente"""
        return self.status == ExpenseStatus.pending