from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from ..loans.loan_model import LoanModel
    from ..payments.payment_model import PaymentModel
    from ..files.file_model import FileModel
    from .client_financial_history_model import ClientFinancialHistoryModel

class ClientStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    pays_on_time = "pays_on_time"  # Paga a tiempo
    bad_debtor = "bad_debtor"  # Mal adeudor

class ClientModel(BasePayTrackModel, table=True):
    __tablename__ = "clients"

    client_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Información personal
    name: str = Field(description="Nombre del cliente")
    paternal_surname: str = Field(description="Apellido paterno")
    maternal_surname: str = Field(description="Apellido materno")
    occupation: str = Field(description="Ocupación del cliente")
    national_id: str = Field(description="INE o identificación nacional")
    address: str = Field(description="Dirección")
    phone: str = Field(description="Teléfono de contacto")
    birth_date: date = Field(description="Fecha de nacimiento")
    
    # Estado y notas
    status: ClientStatus = Field(default=ClientStatus.active, sa_column=Column(Enum(ClientStatus), nullable=False))
    notes: Optional[str] = Field(default=None, description="Notas adicionales sobre el cliente")
    
    # Soft delete

    # Relaciones - Comentadas temporalmente para evitar errores de importación circular
    # loans: List["LoanModel"] = Relationship(back_populates="client")
    # payments: List["PaymentModel"] = Relationship(back_populates="client")
    # files: List["FileModel"] = Relationship(back_populates="client")
    # financial_history: List["ClientFinancialHistoryModel"] = Relationship(back_populates="client")
    
    @property
    def full_name(self) -> str:
        """Retorna el nombre completo del cliente"""
        return f"{self.name} {self.paternal_surname} {self.maternal_surname}".strip()
    
    @property
    def is_active(self) -> bool:
        """Verifica si el cliente está activo"""
        return self.status == ClientStatus.active and self.deleted_at is None
    
    @property
    def is_good_payer(self) -> bool:
        """Verifica si el cliente paga a tiempo"""
        return self.status == ClientStatus.pays_on_time
    
    @property
    def is_bad_debtor(self) -> bool:
        """Verifica si el cliente es mal adeudor"""
        return self.status == ClientStatus.bad_debtor