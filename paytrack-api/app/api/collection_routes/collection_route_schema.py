from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class CollectionRouteBase(BaseModel):
    employee_id: UUID = Field(..., description="ID del empleado responsable")
    loan_id: UUID = Field(..., description="ID del préstamo")
    assignment_date: date = Field(..., description="Fecha de asignación")
    scheduled_date: Optional[date] = Field(None, description="Fecha programada de visita")
    priority: str = Field(default="normal", description="Prioridad (low, normal, high, urgent)")
    notes: Optional[str] = Field(None, description="Notas del cobrador")


class CollectionRouteCreate(CollectionRouteBase):
    pass


class CollectionRouteUpdate(BaseModel):
    employee_id: Optional[UUID] = None
    loan_id: Optional[UUID] = None
    assignment_date: Optional[date] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    visit_attempts: Optional[int] = None
    contact_attempts: Optional[int] = None
    amount_collected: Optional[float] = None
    collection_notes: Optional[str] = None
    client_address: Optional[str] = None
    gps_coordinates: Optional[str] = None


class CollectionRouteResponse(CollectionRouteBase):
    route_id: UUID
    completed_date: Optional[date]
    status: str
    visit_attempts: int
    contact_attempts: int
    amount_collected: Optional[float]
    collection_notes: Optional[str]
    client_address: Optional[str]
    gps_coordinates: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CollectionRouteListResponse(BaseModel):
    collection_routes: list[CollectionRouteResponse]
    total: int
    page: int
    size: int