from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal
import enum

if TYPE_CHECKING:
    from app.models.clients.client_model import ClientModel
    from app.models.users.user_model import UserModel

class PaymentStatus(str, enum.Enum):
    paid = "paid"  # Pagado
    pending = "pending"  # Pendiente
    overdue = "overdue"  # Vencido
    partial = "partial"  # Pago parcial
    cancelled = "cancelled"  # Cancelado

class PaymentMethod(str, enum.Enum):
    cash = "cash"  # Efectivo
    transfer = "transfer"  # Transferencia
    card = "card"  # Tarjeta
    check = "check"  # Cheque

class PaymentModel(BasePayTrackModel, table=True):
    __tablename__ = "payments"

    payment_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Relaciones con otras tablas
    client_id: UUID = Field(foreign_key="clients.client_id", description="ID del cliente")
    responsible_id: UUID = Field(foreign_key="users.user_id", description="ID del empleado responsable")
    
    # Información del pago
    amount: Decimal = Field(description="Monto del pago")
    interest_amount: Decimal = Field(default=Decimal("0.00"), description="Monto de interés")
    payment_method: PaymentMethod = Field(sa_column=Column(Enum(PaymentMethod), nullable=False))
    status: PaymentStatus = Field(default=PaymentStatus.pending, sa_column=Column(Enum(PaymentStatus), nullable=False))
    
    # Fechas importantes
    due_date: Optional[datetime] = Field(default=None, description="Fecha de vencimiento")
    payment_date: Optional[datetime] = Field(default=None, description="Fecha de pago efectivo")
    
    # Notas y referencias
    notes: Optional[str] = Field(default=None, description="Notas adicionales del pago")
    reference: Optional[str] = Field(default=None, description="Referencia del pago")
    
    # Soft delete

    # Relaciones - Comentadas temporalmente para evitar errores de importación circular
    # client: "ClientModel" = Relationship(back_populates="payments")
    # responsible: "UserModel" = Relationship(back_populates="payments_responsible")
    
    @property
    def total_amount(self) -> Decimal:
        """Retorna el monto total (capital + interés)"""
        return self.amount + self.interest_amount
    
    @property
    def is_paid(self) -> bool:
        """Verifica si el pago está completado"""
        return self.status == PaymentStatus.paid
    
    @property
    def is_overdue(self) -> bool:
        """Verifica si el pago está vencido"""
        return self.status == PaymentStatus.overdue
    
    @property
    def days_overdue(self) -> int:
        """Calcula los días de atraso"""
        if self.due_date and not self.is_paid:
            now = datetime.now()
            if now > self.due_date:
                return (now - self.due_date).days
        return 0