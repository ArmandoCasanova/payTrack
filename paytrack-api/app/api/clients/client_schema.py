from uuid import UUID
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

from app.models.clients.client_model import ClientStatus


class ClientSchema(BaseModel):
    client_id: UUID
    name: str = Field(min_length=2, max_length=50)
    paternal_surname: str = Field(min_length=2, max_length=50)
    maternal_surname: str = Field(min_length=2, max_length=50)
    occupation: str = Field(min_length=2, max_length=100)
    national_id: str = Field(min_length=10, max_length=20)
    address: str = Field(min_length=5, max_length=200)
    phone: str = Field(min_length=10, max_length=15)
    birth_date: date
    status: ClientStatus = ClientStatus.active
    notes: Optional[str] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class ClientCreateSchema(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    paternal_surname: str = Field(min_length=2, max_length=50)
    maternal_surname: str = Field(min_length=2, max_length=50)
    occupation: str = Field(min_length=2, max_length=100)
    national_id: str = Field(min_length=10, max_length=20)
    address: str = Field(min_length=5, max_length=200)
    phone: str = Field(min_length=10, max_length=15)
    birth_date: date
    notes: Optional[str] = None

    class Config:
        extra = "forbid"


class ClientUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    paternal_surname: Optional[str] = Field(default=None, min_length=2, max_length=50)
    maternal_surname: Optional[str] = Field(default=None, min_length=2, max_length=50)
    occupation: Optional[str] = Field(default=None, min_length=2, max_length=100)
    national_id: Optional[str] = Field(default=None, min_length=10, max_length=20)
    address: Optional[str] = Field(default=None, min_length=5, max_length=200)
    phone: Optional[str] = Field(default=None, min_length=10, max_length=15)
    birth_date: Optional[date] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = None

    class Config:
        extra = "forbid"


class ClientResponseSchema(ClientSchema):
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClientListResponseSchema(BaseModel):
    clients: list[ClientResponseSchema]
    total: int
    page: int
    size: int