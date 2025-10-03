from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.http_response import PayTrackHttpResponse, PayTrackResponseModel
from app.api.daily_cutoff.daily_cutoff_controller import DailyCutoffController
from app.api.daily_cutoff.daily_cutoff_schema import (
    DailyCutoffResponse,
    DailyCutoffCreate,
    DailyCutoffUpdate,
    DailyCutoffListResponse
)

router = APIRouter(prefix="/dailycutoff", tags=["Daily Cutoff"])


def get_daily_cutoff_controller(db: Session = Depends(get_db)) -> DailyCutoffController:
    """Dependency para obtener el controlador de cortes diarios"""
    return DailyCutoffController(db)


@router.post("/", response_model=PayTrackResponseModel[DailyCutoffResponse])
async def create_daily_cutoff(
    cutoff_data: DailyCutoffCreate,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Crear un nuevo corte diario"""
    try:
        # Verificar si ya existe un corte para esa fecha y empleado
        existing_cutoff = controller.get_cutoff_by_date_and_employee(
            cutoff_data.cutoff_date, 
            cutoff_data.employee_id
        )
        if existing_cutoff:
            raise HTTPException(
                status_code=400, 
                detail="Ya existe un corte para esta fecha y empleado"
            )
            
        cutoff = controller.create_daily_cutoff(cutoff_data)
        return PayTrackHttpResponse.created(DailyCutoffResponse.model_validate(cutoff))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{cutoff_id}", response_model=PayTrackResponseModel[DailyCutoffResponse])
async def get_daily_cutoff(
    cutoff_id: UUID,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Obtener corte diario por ID"""
    cutoff = controller.get_daily_cutoff_by_id(cutoff_id)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Corte diario no encontrado")
    
    return PayTrackHttpResponse.ok(DailyCutoffResponse.model_validate(cutoff))


@router.get("/", response_model=PayTrackResponseModel[DailyCutoffListResponse])
async def get_daily_cutoffs(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    employee_id: Optional[UUID] = Query(None, description="Filtrar por ID del empleado"),
    cutoff_date: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    date_from: Optional[date] = Query(None, description="Fecha inicial del rango"),
    date_to: Optional[date] = Query(None, description="Fecha final del rango"),
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Obtener lista de cortes diarios con filtros opcionales"""
    cutoffs, total = controller.get_daily_cutoffs(
        skip=skip,
        limit=limit,
        employee_id=employee_id,
        cutoff_date=cutoff_date,
        status=status,
        date_from=date_from,
        date_to=date_to
    )
    
    cutoffs_response = [
        DailyCutoffResponse.model_validate(cutoff) for cutoff in cutoffs
    ]
    
    return PayTrackHttpResponse.ok(DailyCutoffListResponse(
        items=cutoffs_response,
        total=total,
        skip=skip,
        limit=limit
    ))


@router.put("/{cutoff_id}", response_model=PayTrackResponseModel[DailyCutoffResponse])
async def update_daily_cutoff(
    cutoff_id: UUID,
    cutoff_data: DailyCutoffUpdate,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Actualizar corte diario"""
    cutoff = controller.update_daily_cutoff(cutoff_id, cutoff_data)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Corte diario no encontrado")
    
    return PayTrackHttpResponse.updated(DailyCutoffResponse.model_validate(cutoff))


@router.delete("/{cutoff_id}", response_model=PayTrackResponseModel[None])
async def delete_daily_cutoff(
    cutoff_id: UUID,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Eliminar corte diario (eliminación lógica)"""
    success = controller.delete_daily_cutoff(cutoff_id)
    if not success:
        raise HTTPException(status_code=404, detail="Corte diario no encontrado")
    
    return PayTrackHttpResponse.updated(None)


@router.get("/employee/{employee_id}", response_model=PayTrackResponseModel[List[DailyCutoffResponse]])
async def get_cutoffs_by_employee(
    employee_id: UUID,
    date_from: Optional[date] = Query(None, description="Fecha inicial del rango"),
    date_to: Optional[date] = Query(None, description="Fecha final del rango"),
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Obtener todos los cortes de un empleado específico"""
    cutoffs = controller.get_cutoffs_by_employee(
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to
    )
    
    cutoffs_response = [
        DailyCutoffResponse.model_validate(cutoff) for cutoff in cutoffs
    ]
    
    return PayTrackHttpResponse.ok(cutoffs_response)


@router.get("/date/{cutoff_date}/employee/{employee_id}", response_model=PayTrackResponseModel[DailyCutoffResponse])
async def get_cutoff_by_date_and_employee(
    cutoff_date: date,
    employee_id: UUID,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Obtener corte específico por fecha y empleado"""
    cutoff = controller.get_cutoff_by_date_and_employee(cutoff_date, employee_id)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Corte no encontrado para esa fecha y empleado")
    
    return PayTrackHttpResponse.ok(DailyCutoffResponse.model_validate(cutoff))


@router.post("/{cutoff_id}/approve", response_model=PayTrackResponseModel[DailyCutoffResponse])
async def approve_cutoff(
    cutoff_id: UUID,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Aprobar un corte diario"""
    cutoff = controller.approve_cutoff(cutoff_id)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Corte diario no encontrado")
    
    return PayTrackHttpResponse.updated(DailyCutoffResponse.model_validate(cutoff))


@router.post("/{cutoff_id}/reject", response_model=PayTrackResponseModel[DailyCutoffResponse])
async def reject_cutoff(
    cutoff_id: UUID,
    controller: DailyCutoffController = Depends(get_daily_cutoff_controller)
):
    """Rechazar un corte diario"""
    cutoff = controller.reject_cutoff(cutoff_id)
    if not cutoff:
        raise HTTPException(status_code=404, detail="Corte diario no encontrado")
    
    return PayTrackHttpResponse.updated(DailyCutoffResponse.model_validate(cutoff))