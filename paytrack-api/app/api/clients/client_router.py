from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_db
from app.api.clients.client_service import ClientService
from app.api.clients.client_controller import ClientController
from app.api.clients.client_schema import (
    ClientCreateSchema, 
    ClientUpdateSchema,
    ClientResponseSchema, 
    ClientListResponseSchema
)
from app.models.clients.client_model import ClientStatus
from app.core.http_response import PayTrackHttpResponse

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientResponseSchema, status_code=201)
async def create_client(
    client_data: ClientCreateSchema,
    session: Session = Depends(get_db)
):
    """Crear un nuevo cliente"""
    try:
        controller = ClientController(session)
        
        # Validar que no exista un cliente con el mismo national_id
        await controller.validate_existing_client_national_id(client_data.national_id)
        
        # Crear el cliente
        new_client = await ClientService.create_client(client_data, session)
        
        # Retornar directamente con FastAPI (maneja la serialización automáticamente)
        return new_client
    except Exception as e:
        raise e


@router.get("/", response_model=ClientListResponseSchema)
async def get_clients(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por nombre, apellidos, identificación o teléfono"),
    status: Optional[ClientStatus] = Query(None, description="Filtrar por estado del cliente"),
    session: Session = Depends(get_db)
):
    """Obtener lista de clientes con paginación y filtros"""
    try:
        clients, total = await ClientService.get_clients(
            session=session,
            skip=skip,
            limit=limit,
            search=search,
            status=status
        )
        
        response_data = {
            "clients": clients,
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(clients)
        }
        
        return response_data
    except Exception as e:
        raise e


@router.get("/{client_id}", response_model=ClientResponseSchema)
async def get_client_by_id(
    client_id: UUID,
    session: Session = Depends(get_db)
):
    """Obtener un cliente por su ID"""
    try:
        controller = ClientController(session)
        client = await controller.get_client_by_id_or_raise(client_id)
        
        return client
    except Exception as e:
        raise e


@router.put("/{client_id}", response_model=ClientResponseSchema)
async def update_client(
    client_id: UUID,
    client_data: ClientUpdateSchema,
    session: Session = Depends(get_db)
):
    """Actualizar un cliente"""
    try:
        controller = ClientController(session)
        
        # Verificar que el cliente existe
        existing_client = await controller.get_client_by_id_or_raise(client_id)
        
        # Si se está actualizando el national_id, validar que no exista otro cliente con ese ID
        if client_data.national_id and client_data.national_id != existing_client.national_id:
            await controller.validate_existing_client_national_id(client_data.national_id)
        
        # Si se está actualizando el status, validar el cambio
        if client_data.status and client_data.status != existing_client.status:
            await controller.validate_client_status_change(existing_client.status, client_data.status)
        
        # Actualizar el cliente
        updated_client = await ClientService.update_client(client_id, client_data, session)
        
        return updated_client
    except Exception as e:
        raise e


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: UUID,
    session: Session = Depends(get_db)
):
    """Eliminar un cliente (soft delete)"""
    try:
        controller = ClientController(session)
        
        # Verificar que el cliente existe
        await controller.get_client_by_id_or_raise(client_id)
        
        # Eliminar el cliente
        await ClientService.delete_client(client_id, session)
        
        return None
    except Exception as e:
        raise e
