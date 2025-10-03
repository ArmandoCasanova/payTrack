from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, validator
from pydantic.alias_generators import to_camel

from app.models.loans.loan_model import LoanStatus


class LoanSchema(BaseModel):
    loan_id: UUID
    client_id: UUID
    authorizer_id: UUID
    amount: Decimal = Field(gt=0, description="Monto del préstamo")
    payment_count: int = Field(gt=0, le=60, description="Cantidad de pagos (max 60)")
    interest_rate: Decimal = Field(ge=0, le=1, description="Tasa de interés (0-1)")
    payment_start_date: date
    late_interest: Decimal = Field(ge=0, le=1, description="Interés por atraso (0-1)")
    status: LoanStatus = LoanStatus.pending_approval
    total_amount: Optional[Decimal] = None
    remaining_amount: Optional[Decimal] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class LoanCreateSchema(BaseModel):
    client_id: UUID
    amount: Decimal = Field(gt=0, description="Monto del préstamo")
    payment_count: int = Field(gt=0, le=60, description="Cantidad de pagos (max 60)")
    interest_rate: Decimal = Field(ge=0, le=1, description="Tasa de interés (0-1)")
    payment_start_date: date
    late_interest: Decimal = Field(ge=0, le=1, description="Interés por atraso (0-1)")

    @validator('payment_start_date')
    def validate_payment_start_date(cls, v):
        from datetime import date
        if v < date.today():
            raise ValueError('La fecha de inicio de pagos no puede ser anterior a hoy')
        return v

    class Config:
        extra = "forbid"


class LoanUpdateSchema(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0, description="Monto del préstamo")
    payment_count: Optional[int] = Field(default=None, gt=0, le=60, description="Cantidad de pagos")
    interest_rate: Optional[Decimal] = Field(default=None, ge=0, le=1, description="Tasa de interés")
    payment_start_date: Optional[date] = None
    late_interest: Optional[Decimal] = Field(default=None, ge=0, le=1, description="Interés por atraso")
    status: Optional[LoanStatus] = None

    class Config:
        extra = "forbid"


class LoanApprovalSchema(BaseModel):
    action: str = Field(description="approve o reject")
    notes: Optional[str] = None

    @validator('action')
    def validate_action(cls, v):
        if v not in ['approve', 'reject']:
            raise ValueError('La acción debe ser "approve" o "reject"')
        return v

    class Config:
        extra = "forbid"


class LoanResponseSchema(LoanSchema):
    client_name: str
    authorizer_name: str
    payment_amount: Decimal
    is_active: bool
    is_completed: bool
    is_overdue: bool
    created_at: datetime
    updated_at: datetime


class LoanListResponseSchema(BaseModel):
    loans: list[LoanResponseSchema]
    total: int
    page: int
    size: int