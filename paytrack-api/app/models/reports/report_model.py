from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from app.models.users.user_model import UserModel

class ReportType(str, enum.Enum):
    daily_summary = "daily_summary"
    monthly_summary = "monthly_summary"
    loan_report = "loan_report"
    payment_report = "payment_report"
    collection_report = "collection_report"
    financial_report = "financial_report"
    client_report = "client_report"
    employee_performance = "employee_performance"
    overdue_report = "overdue_report"

class ReportStatus(str, enum.Enum):
    generating = "generating"
    completed = "completed"
    failed = "failed"
    scheduled = "scheduled"

class ReportFormat(str, enum.Enum):
    pdf = "pdf"
    excel = "excel"
    csv = "csv"
    json = "json"

class ReportModel(BasePayTrackModel, table=True):
    __tablename__ = "reports"

    report_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Información básica
    report_name: str = Field(description="Nombre del reporte")
    report_type: ReportType = Field(sa_column=Column(Enum(ReportType), nullable=False))
    
    # Usuario generador
    generator_user_id: UUID = Field(foreign_key="users.user_id", description="ID del usuario que generó el reporte")
    
    # Fechas
    generation_date: datetime = Field(default_factory=datetime.now, description="Fecha de generación")
    report_period_start: Optional[datetime] = Field(default=None, description="Inicio del período del reporte")
    report_period_end: Optional[datetime] = Field(default=None, description="Fin del período del reporte")
    
    # Estado y formato
    status: ReportStatus = Field(default=ReportStatus.generating, sa_column=Column(Enum(ReportStatus), nullable=False))
    format: ReportFormat = Field(default=ReportFormat.pdf, sa_column=Column(Enum(ReportFormat), nullable=False))
    
    # Archivos y contenido
    file_path: Optional[str] = Field(default=None, description="Ruta del archivo generado")
    file_size: Optional[int] = Field(default=None, description="Tamaño del archivo en bytes")
    
    # Filtros aplicados (JSON)
    filters_applied: Optional[str] = Field(default=None, description="Filtros aplicados al reporte (JSON)")
    
    # Métricas del reporte
    total_records: Optional[int] = Field(default=None, description="Total de registros en el reporte")
    processing_time: Optional[float] = Field(default=None, description="Tiempo de procesamiento en segundos")
    
    # Configuración
    is_scheduled: bool = Field(default=False, description="Si es un reporte programado")
    schedule_frequency: Optional[str] = Field(default=None, description="Frecuencia de programación")
    
    # Descripción y notas
    description: Optional[str] = Field(default=None, description="Descripción del reporte")
    notes: Optional[str] = Field(default=None, description="Notas adicionales")

    # Relaciones
    generator: "UserModel" = Relationship(back_populates="generated_reports")
    
    @property
    def is_completed(self) -> bool:
        """Verifica si el reporte está completado"""
        return self.status == ReportStatus.completed
    
    @property
    def is_failed(self) -> bool:
        """Verifica si falló la generación"""
        return self.status == ReportStatus.failed
    
    @property
    def file_size_mb(self) -> Optional[float]:
        """Retorna el tamaño del archivo en MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None