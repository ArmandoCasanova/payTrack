from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.users.user_model import UserModel

class DailyCutoffModel(BasePayTrackModel, table=True):
    __tablename__ = "daily_cutoff"

    cutoff_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Información básica
    cutoff_date: date = Field(description="Fecha del corte")
    responsible_id: UUID = Field(foreign_key="users.user_id", description="ID del usuario responsable del corte")
    
    # Información financiera
    total_income: Decimal = Field(default=Decimal("0.00"), description="Total de ingresos del día")
    total_expenses: Decimal = Field(default=Decimal("0.00"), description="Total de egresos del día")
    profit: Decimal = Field(default=Decimal("0.00"), description="Utilidad del día")
    
    # Desglose de ingresos
    payments_received: Decimal = Field(default=Decimal("0.00"), description="Pagos recibidos")
    interest_collected: Decimal = Field(default=Decimal("0.00"), description="Intereses cobrados")
    late_fees_collected: Decimal = Field(default=Decimal("0.00"), description="Comisiones por atraso")
    other_income: Decimal = Field(default=Decimal("0.00"), description="Otros ingresos")
    
    # Desglose de egresos
    operational_expenses: Decimal = Field(default=Decimal("0.00"), description="Gastos operacionales")
    salary_payments: Decimal = Field(default=Decimal("0.00"), description="Pagos de salarios")
    loan_disbursements: Decimal = Field(default=Decimal("0.00"), description="Desembolsos de préstamos")
    other_expenses: Decimal = Field(default=Decimal("0.00"), description="Otros gastos")
    
    # Información de caja
    initial_cash: Decimal = Field(default=Decimal("0.00"), description="Efectivo inicial")
    final_cash: Decimal = Field(default=Decimal("0.00"), description="Efectivo final")
    cash_difference: Decimal = Field(default=Decimal("0.00"), description="Diferencia de efectivo")
    
    # Estadísticas del día
    total_transactions: int = Field(default=0, description="Total de transacciones")
    loans_granted: int = Field(default=0, description="Préstamos otorgados")
    payments_collected: int = Field(default=0, description="Pagos cobrados")
    
    # Estado y notas
    is_closed: bool = Field(default=False, description="Si el corte está cerrado")
    closure_time: Optional[datetime] = Field(default=None, description="Hora de cierre del corte")
    notes: Optional[str] = Field(default=None, description="Notas del corte")
    discrepancies: Optional[str] = Field(default=None, description="Discrepancias encontradas")
    
    # Información bancaria
    bank_deposits: Decimal = Field(default=Decimal("0.00"), description="Depósitos bancarios")
    bank_withdrawals: Decimal = Field(default=Decimal("0.00"), description="Retiros bancarios")
    bank_balance: Optional[Decimal] = Field(default=None, description="Saldo bancario al cierre")

    # Relaciones
    responsible: "UserModel" = Relationship(back_populates="daily_cutoffs")
    
    @property
    def net_cash_flow(self) -> Decimal:
        """Calcula el flujo neto de efectivo"""
        return self.total_income - self.total_expenses
    
    @property
    def profit_margin(self) -> float:
        """Calcula el margen de utilidad"""
        if self.total_income > 0:
            return float((self.profit / self.total_income) * 100)
        return 0.0
    
    @property
    def has_discrepancies(self) -> bool:
        """Verifica si hay discrepancias en el corte"""
        return self.cash_difference != Decimal("0.00") or bool(self.discrepancies)
    
    @property
    def average_transaction_amount(self) -> Decimal:
        """Calcula el monto promedio por transacción"""
        if self.total_transactions > 0:
            return self.total_income / self.total_transactions
        return Decimal("0.00")
    
    def close_cutoff(self, closing_user_id: UUID, notes: Optional[str] = None):
        """Cierra el corte diario"""
        self.is_closed = True
        self.closure_time = datetime.now()
        if notes:
            self.notes = notes