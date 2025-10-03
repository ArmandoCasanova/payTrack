from uuid import UUID
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from pydantic.alias_generators import to_camel

from app.models.suppliers.supplier_model import SupplierStatus, SupplierType


class SupplierSchema(BaseModel):
    supplier_id: UUID
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=15)
    contact: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    folio: Optional[str] = None
    address: str = Field(min_length=5, max_length=200)
    supplier_type: SupplierType
    status: SupplierStatus = SupplierStatus.active
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class SupplierCreateSchema(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=15)
    contact: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    folio: Optional[str] = None
    address: str = Field(min_length=5, max_length=200)
    supplier_type: SupplierType
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None

    class Config:
        extra = "forbid"


class SupplierUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=15)
    contact: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    folio: Optional[str] = None
    address: Optional[str] = Field(default=None, min_length=5, max_length=200)
    supplier_type: Optional[SupplierType] = None
    status: Optional[SupplierStatus] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None

    class Config:
        extra = "forbid"


class SupplierResponseSchema(SupplierSchema):
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SupplierListResponseSchema(BaseModel):
    suppliers: list[SupplierResponseSchema]
    total: int
    page: int
    size: int