from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
import enum

if TYPE_CHECKING:
    from app.models.clients.client_model import ClientModel
    from app.models.users.user_model import UserModel
    from app.models.collection_routes.collection_route_model import CollectionRouteModel

class LoanStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    defaulted = "defaulted"
    cancelled = "cancelled"
    pending_approval = "pending_approval"

class LoanModel(BasePayTrackModel, table=True):
    __tablename__ = "loans"

    loan_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Relaciones
    client_id: UUID = Field(foreign_key="clients.client_id", description="ID del cliente")
    authorizer_id: UUID = Field(foreign_key="users.user_id", description="ID del usuario que autorizó el préstamo")
    
    # Información del préstamo
    amount: Decimal = Field(description="Monto del préstamo")
    payment_count: int = Field(description="Cantidad de pagos programados")
    interest_rate: Decimal = Field(description="Tasa de interés")
    payment_start_date: date = Field(description="Fecha de inicio de pagos")
    late_interest: Decimal = Field(description="Interés por atraso")
    
    # Estado
    status: LoanStatus = Field(default=LoanStatus.pending_approval, sa_column=Column(Enum(LoanStatus), nullable=False))
    
    # Campos calculados
    total_amount: Optional[Decimal] = Field(default=None, description="Monto total a pagar (calculado)")
    remaining_amount: Optional[Decimal] = Field(default=None, description="Monto restante por pagar")
    
    # Soft delete

    # Relaciones
    client: "ClientModel" = Relationship(back_populates="loans")
    authorizer: "UserModel" = Relationship(back_populates="authorized_loans")
    collection_routes: List["CollectionRouteModel"] = Relationship(back_populates="loan")
    
    @property
    def is_active(self) -> bool:
        """Verifica si el préstamo está activo"""
        return self.status == LoanStatus.active and self.deleted_at is None
    
    @property
    def is_completed(self) -> bool:
        """Verifica si el préstamo está completado"""
        return self.status == LoanStatus.completed
    
    @property
    def is_overdue(self) -> bool:
        """Verifica si el préstamo está en mora"""
        return self.status == LoanStatus.defaulted
    
    def calculate_payment_amount(self) -> Decimal:
        """Calcula el monto de cada pago"""
        if self.payment_count > 0:
            total_with_interest = self.amount * (1 + self.interest_rate)
            return total_with_interest / self.payment_count
        return Decimal("0.00")