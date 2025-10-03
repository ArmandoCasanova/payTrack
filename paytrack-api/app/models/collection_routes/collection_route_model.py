from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from app.models.users.user_model import UserModel
    from app.models.loans.loan_model import LoanModel

class CollectionRouteStatus(str, enum.Enum):
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    pending = "pending"

class CollectionPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

class CollectionRouteModel(BasePayTrackModel, table=True):
    __tablename__ = "collection_routes"

    route_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Relaciones
    employee_id: UUID = Field(foreign_key="users.user_id", description="ID del empleado asignado")
    loan_id: UUID = Field(foreign_key="loans.loan_id", description="ID del préstamo")
    
    # Información de la ruta
    assignment_date: date = Field(description="Fecha de asignación")
    scheduled_date: Optional[date] = Field(default=None, description="Fecha programada para el cobro")
    completed_date: Optional[date] = Field(default=None, description="Fecha de completado")
    
    # Estado y prioridad
    status: CollectionRouteStatus = Field(default=CollectionRouteStatus.assigned, sa_column=Column(Enum(CollectionRouteStatus), nullable=False))
    priority: CollectionPriority = Field(default=CollectionPriority.normal, sa_column=Column(Enum(CollectionPriority), nullable=False))
    
    # Información adicional
    notes: Optional[str] = Field(default=None, description="Notas del cobrador")
    visit_attempts: int = Field(default=0, description="Número de intentos de visita")
    contact_attempts: int = Field(default=0, description="Número de intentos de contacto")
    
    # Resultados
    amount_collected: Optional[float] = Field(default=None, description="Monto cobrado")
    collection_notes: Optional[str] = Field(default=None, description="Notas del resultado del cobro")
    
    # Ubicación
    client_address: Optional[str] = Field(default=None, description="Dirección del cliente para esta ruta")
    gps_coordinates: Optional[str] = Field(default=None, description="Coordenadas GPS")
    
    # Soft delete

    # Relaciones
    # employee: "UserModel" = Relationship(back_populates="collection_routes")
    # loan: "LoanModel" = Relationship(back_populates="collection_routes")
    
    @property
    def is_completed(self) -> bool:
        """Verifica si la ruta está completada"""
        return self.status == CollectionRouteStatus.completed
    
    @property
    def is_in_progress(self) -> bool:
        """Verifica si la ruta está en progreso"""
        return self.status == CollectionRouteStatus.in_progress
    
    @property
    def is_overdue(self) -> bool:
        """Verifica si la ruta está vencida"""
        if self.scheduled_date and self.status not in [CollectionRouteStatus.completed, CollectionRouteStatus.cancelled]:
            return datetime.now().date() > self.scheduled_date
        return False
    
    @property
    def days_since_assignment(self) -> int:
        """Calcula los días desde la asignación"""
        return (datetime.now().date() - self.assignment_date).days