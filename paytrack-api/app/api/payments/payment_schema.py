from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, validator
from pydantic.alias_generators import to_camel

from app.models.payments.payment_model import PaymentStatus, PaymentMethod


class PaymentSchema(BaseModel):
    payment_id: UUID
    client_id: UUID
    responsible_id: UUID
    amount: Decimal = Field(gt=0, description="Monto del pago")
    interest_amount: Decimal = Field(ge=0, description="Monto de interés")
    payment_method: PaymentMethod
    status: PaymentStatus = PaymentStatus.pending
    due_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    reference: Optional[str] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class PaymentCreateSchema(BaseModel):
    client_id: UUID
    amount: Decimal = Field(gt=0, description="Monto del pago")
    interest_amount: Decimal = Field(ge=0, default=Decimal("0.00"), description="Monto de interés")
    payment_method: PaymentMethod
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    reference: Optional[str] = None

    class Config:
        extra = "forbid"


class PaymentUpdateSchema(BaseModel):
    amount: Optional[Decimal] = Field(default=None, gt=0, description="Monto del pago")
    interest_amount: Optional[Decimal] = Field(default=None, ge=0, description="Monto de interés")
    payment_method: Optional[PaymentMethod] = None
    status: Optional[PaymentStatus] = None
    due_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    reference: Optional[str] = None

    class Config:
        extra = "forbid"


class PaymentProcessSchema(BaseModel):
    action: str = Field(description="process, cancel, o mark_overdue")
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None

    @validator('action')
    def validate_action(cls, v):
        if v not in ['process', 'cancel', 'mark_overdue']:
            raise ValueError('La acción debe ser "process", "cancel" o "mark_overdue"')
        return v

    @validator('payment_date')
    def validate_payment_date(cls, v, values):
        if values.get('action') == 'process' and not v:
            raise ValueError('payment_date es requerido para procesar un pago')
        return v

    class Config:
        extra = "forbid"


class PaymentResponseSchema(PaymentSchema):
    client_name: str
    responsible_name: str
    total_amount: Decimal
    is_paid: bool
    is_overdue: bool
    days_overdue: int
    created_at: datetime
    updated_at: datetime


class PaymentListResponseSchema(BaseModel):
    payments: list[PaymentResponseSchema]
    total: int
    page: int
    size: int


class PaymentSummarySchema(BaseModel):
    total_pending: Decimal
    total_paid: Decimal
    total_overdue: Decimal
    count_pending: int
    count_paid: int
    count_overdue: int