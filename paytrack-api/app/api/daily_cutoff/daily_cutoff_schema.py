from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class DailyCutoffBase(BaseModel):
    cutoff_date: date = Field(..., description="Fecha del corte diario")
    total_collections: Decimal = Field(..., description="Total de cobranzas del día", ge=0)
    total_payments: Decimal = Field(..., description="Total de pagos del día", ge=0)
    total_expenses: Decimal = Field(..., description="Total de gastos del día", ge=0)
    balance: Decimal = Field(..., description="Balance del día (cobranzas - gastos)")
    employee_id: UUID = Field(..., description="ID del empleado responsable del corte")
    notes: Optional[str] = Field(None, description="Notas adicionales del corte")
    status: str = Field(default="pending", description="Estado del corte (pending, approved, rejected)")


class DailyCutoffCreate(DailyCutoffBase):
    """Schema para crear un nuevo corte diario"""
    pass


class DailyCutoffUpdate(BaseModel):
    """Schema para actualizar un corte diario"""
    total_collections: Optional[Decimal] = Field(None, description="Total de cobranzas del día", ge=0)
    total_payments: Optional[Decimal] = Field(None, description="Total de pagos del día", ge=0)
    total_expenses: Optional[Decimal] = Field(None, description="Total de gastos del día", ge=0)
    balance: Optional[Decimal] = Field(None, description="Balance del día")
    notes: Optional[str] = Field(None, description="Notas adicionales del corte")
    status: Optional[str] = Field(None, description="Estado del corte")


class DailyCutoffResponse(DailyCutoffBase):
    """Schema para respuesta de corte diario"""
    cutoff_id: UUID = Field(..., description="ID único del corte diario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    model_config = {"from_attributes": True}


class DailyCutoffListResponse(BaseModel):
    """Schema para respuesta de lista de cortes diarios"""
    items: List[DailyCutoffResponse] = Field(..., description="Lista de cortes diarios")
    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros omitidos")
    limit: int = Field(..., description="Límite de registros")