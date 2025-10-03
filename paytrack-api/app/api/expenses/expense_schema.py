from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, validator
from pydantic.alias_generators import to_camel

from app.models.expenses.expense_model import ExpenseStatus, ExpenseCategory


class ExpenseSchema(BaseModel):
    expense_id: UUID
    responsible_id: UUID
    supplier_id: Optional[UUID] = None
    expense_date: date
    payment_method: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=5, max_length=500)
    amount: Decimal = Field(gt=0, description="Monto del egreso")
    category: ExpenseCategory = ExpenseCategory.other
    status: ExpenseStatus = ExpenseStatus.pending
    invoice_number: Optional[str] = None
    receipt_path: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class ExpenseCreateSchema(BaseModel):
    supplier_id: Optional[UUID] = None
    expense_date: date
    payment_method: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=5, max_length=500)
    amount: Decimal = Field(gt=0, description="Monto del egreso")
    category: ExpenseCategory = ExpenseCategory.other
    invoice_number: Optional[str] = None
    receipt_path: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        extra = "forbid"


class ExpenseUpdateSchema(BaseModel):
    supplier_id: Optional[UUID] = None
    expense_date: Optional[date] = None
    payment_method: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, min_length=5, max_length=500)
    amount: Optional[Decimal] = Field(default=None, gt=0, description="Monto del egreso")
    category: Optional[ExpenseCategory] = None
    status: Optional[ExpenseStatus] = None
    invoice_number: Optional[str] = None
    receipt_path: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        extra = "forbid"


class ExpenseApprovalSchema(BaseModel):
    action: str = Field(description="approve, reject, o pay")
    notes: Optional[str] = None

    @validator('action')
    def validate_action(cls, v):
        if v not in ['approve', 'reject', 'pay']:
            raise ValueError('La acción debe ser "approve", "reject" o "pay"')
        return v

    class Config:
        extra = "forbid"


class ExpenseResponseSchema(ExpenseSchema):
    responsible_name: str
    supplier_name: Optional[str] = None
    is_paid: bool
    is_pending: bool
    created_at: datetime
    updated_at: datetime


class ExpenseListResponseSchema(BaseModel):
    expenses: list[ExpenseResponseSchema]
    total: int
    page: int
    size: int


class ExpenseSummarySchema(BaseModel):
    total_pending: Decimal
    total_approved: Decimal
    total_paid: Decimal
    total_rejected: Decimal
    count_pending: int
    count_approved: int
    count_paid: int
    count_rejected: int
    by_category: dict[str, Decimal]