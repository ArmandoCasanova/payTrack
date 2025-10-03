from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.http_response import PayTrackHttpResponse, PayTrackResponseModel
from app.api.collection_routes.collection_route_controller import CollectionRouteController
from app.api.collection_routes.collection_route_schema import (
    CollectionRouteResponse,
    CollectionRouteCreate,
    CollectionRouteUpdate,
    CollectionRouteListResponse
)

router = APIRouter(prefix="/collection_routes", tags=["Collection Routes"])


def get_collection_route_controller(db: Session = Depends(get_db)) -> CollectionRouteController:
    """Dependency para obtener el controlador de rutas de cobranza"""
    return CollectionRouteController(db)


@router.post("/", response_model=PayTrackResponseModel[CollectionRouteResponse])
async def create_collection_route(
    collection_route_data: CollectionRouteCreate,
    controller: CollectionRouteController = Depends(get_collection_route_controller)
):
    """Crear una nueva ruta de cobranza"""
    try:
        collection_route = controller.create_collection_route(collection_route_data)
        return PayTrackHttpResponse.created(CollectionRouteResponse.model_validate(collection_route).model_dump(mode='json'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{route_id}", response_model=PayTrackResponseModel[CollectionRouteResponse])
async def get_collection_route(
    route_id: UUID,
    controller: CollectionRouteController = Depends(get_collection_route_controller)
):
    """Obtener ruta de cobranza por ID"""
    collection_route = controller.get_collection_route_by_id(route_id)
    if not collection_route:
        raise HTTPException(status_code=404, detail="Ruta de cobranza no encontrada")
    
    return PayTrackHttpResponse.ok(CollectionRouteResponse.model_validate(collection_route))


@router.get("/", response_model=PayTrackResponseModel[CollectionRouteListResponse])
async def get_collection_routes(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    employee_id: Optional[UUID] = Query(None, description="Filtrar por ID del empleado"),
    loan_id: Optional[UUID] = Query(None, description="Filtrar por ID del préstamo"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    controller: CollectionRouteController = Depends(get_collection_route_controller)
):
    """Obtener lista de rutas de cobranza con filtros opcionales"""
    collection_routes, total = controller.get_collection_routes(
        skip=skip,
        limit=limit,
        employee_id=employee_id,
        loan_id=loan_id,
        status=status
    )
    
    collection_routes_response = [
        CollectionRouteResponse.model_validate(route) for route in collection_routes
    ]
    
    return PayTrackHttpResponse.ok(CollectionRouteListResponse(
        items=collection_routes_response,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.put("/{route_id}", response_model=PayTrackResponseModel[CollectionRouteResponse])
async def update_collection_route(
    route_id: UUID,
    collection_route_data: CollectionRouteUpdate,
    controller: CollectionRouteController = Depends(get_collection_route_controller)
):
    """Actualizar ruta de cobranza"""
    collection_route = controller.update_collection_route(route_id, collection_route_data)
    if not collection_route:
        raise HTTPException(status_code=404, detail="Ruta de cobranza no encontrada")
    
    return PayTrackHttpResponse.updated(CollectionRouteResponse.model_validate(collection_route))


@router.delete("/{route_id}", response_model=PayTrackResponseModel[None])
async def delete_collection_route(
    route_id: UUID,
    controller: CollectionRouteController = Depends(get_collection_route_controller)
):
    """Eliminar ruta de cobranza (eliminación lógica)"""
    success = controller.delete_collection_route(route_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ruta de cobranza no encontrada")
    
    return PayTrackHttpResponse.updated(None)


@router.get("/employee/{employee_id}", response_model=PayTrackResponseModel[List[CollectionRouteResponse]])
async def get_routes_by_employee(
    employee_id: UUID,
    controller: CollectionRouteController = Depends(get_collection_route_controller)
):
    """Obtener todas las rutas asignadas a un empleado específico"""
    collection_routes = controller.get_routes_by_employee(employee_id)
    
    collection_routes_response = [
        CollectionRouteResponse.model_validate(route) for route in collection_routes
    ]
    
    return PayTrackHttpResponse.ok(collection_routes_response)