from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship
from app.core.base_model import BasePayTrackModel
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.clients.client_model import ClientModel

class ClientFinancialHistoryModel(BasePayTrackModel, table=True):
    __tablename__ = "client_financial_history"

    history_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Relación con cliente
    client_id: UUID = Field(foreign_key="clients.client_id", description="ID del cliente")
    
    # Información financiera actual
    current_debt: Decimal = Field(default=Decimal("0.00"), description="Adeudo actual")
    active_loans_count: int = Field(default=0, description="Cantidad de préstamos activos")
    payment_delays_count: int = Field(default=0, description="Cantidad de atrasos en pagos")
    average_delay_days: int = Field(default=0, description="Promedio de días de atraso")
    total_loaned_amount: Decimal = Field(default=Decimal("0.00"), description="Monto total prestado históricamente")
    
    # Métricas adicionales
    total_paid_amount: Decimal = Field(default=Decimal("0.00"), description="Monto total pagado")
    total_interest_paid: Decimal = Field(default=Decimal("0.00"), description="Total de intereses pagados")
    completed_loans_count: int = Field(default=0, description="Préstamos completados exitosamente")
    defaulted_loans_count: int = Field(default=0, description="Préstamos en mora")
    
    # Calificación crediticia
    credit_score: Optional[int] = Field(default=None, description="Puntuación crediticia (1-100)")
    risk_level: Optional[str] = Field(default=None, description="Nivel de riesgo (bajo/medio/alto)")
    
    # Fechas importantes
    first_loan_date: Optional[datetime] = Field(default=None, description="Fecha del primer préstamo")
    last_payment_date: Optional[datetime] = Field(default=None, description="Fecha del último pago")
    last_update_date: datetime = Field(default_factory=datetime.now, description="Última actualización del historial")
    
    # Información de comportamiento
    payment_consistency: Optional[float] = Field(default=None, description="Consistencia de pagos (0.0-1.0)")
    preferred_payment_method: Optional[str] = Field(default=None, description="Método de pago preferido")
    
    # Soft delete

    # Relaciones
    client: "ClientModel" = Relationship(back_populates="financial_history")
    
    @property
    def debt_to_income_ratio(self) -> Optional[float]:
        """Calcula la relación deuda-ingreso si hay información disponible"""
        # Esto se podría calcular si tuviéramos información de ingresos del cliente
        return None
    
    @property
    def payment_success_rate(self) -> float:
        """Calcula la tasa de éxito en pagos"""
        total_payments = self.payment_delays_count + self.completed_loans_count
        if total_payments > 0:
            return (self.completed_loans_count / total_payments) * 100
        return 0.0
    
    @property
    def is_good_client(self) -> bool:
        """Determina si es un buen cliente basado en métricas"""
        return (
            self.payment_delays_count <= 2 and
            self.average_delay_days <= 5 and
            self.defaulted_loans_count == 0
        )
    
    @property
    def risk_assessment(self) -> str:
        """Evalúa el riesgo del cliente"""
        if self.defaulted_loans_count > 0 or self.average_delay_days > 15:
            return "alto"
        elif self.payment_delays_count > 3 or self.average_delay_days > 7:
            return "medio"
        else:
            return "bajo"