from typing import Optional, TYPE_CHECKING, List
from sqlmodel import Field, Column, Enum, Relationship
from app.core.base_model import BasePayTrackModel
from datetime import datetime
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from app.models.expenses.expense_model import ExpenseModel

class SupplierStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class SupplierType(str, enum.Enum):
    service = "service"  # Servicios
    product = "product"  # Productos
    maintenance = "maintenance"  # Mantenimiento
    office = "office"  # Oficina
    other = "other"  # Otros

class SupplierModel(BasePayTrackModel, table=True):
    __tablename__ = "suppliers"

    supplier_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Información básica
    name: str = Field(description="Nombre del proveedor")
    phone: str = Field(description="Teléfono de contacto")
    contact: str = Field(description="Persona de contacto")
    description: Optional[str] = Field(default=None, description="Descripción del proveedor")
    folio: Optional[str] = Field(default=None, description="Número de folio o código")
    address: str = Field(description="Dirección del proveedor")
    
    # Clasificación y estado
    supplier_type: SupplierType = Field(sa_column=Column(Enum(SupplierType), nullable=False))
    status: SupplierStatus = Field(default=SupplierStatus.active, sa_column=Column(Enum(SupplierStatus), nullable=False))
    
    # Información adicional
    email: Optional[str] = Field(default=None, description="Email del proveedor")
    website: Optional[str] = Field(default=None, description="Sitio web")
    tax_id: Optional[str] = Field(default=None, description="RFC o ID fiscal")
    
    # Soft delete

    # Relaciones
    expenses: List["ExpenseModel"] = Relationship(back_populates="supplier")
    
    @property
    def is_active(self) -> bool:
        """Verifica si el proveedor está activo"""
        return self.status == SupplierStatus.active and self.deleted_at is None
    
    def __str__(self) -> str:
        return f"{self.name} ({self.supplier_type.value})"