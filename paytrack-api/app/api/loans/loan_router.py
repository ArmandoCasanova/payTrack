from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_db
from app.api.loans.loan_service import LoanService
from app.api.loans.loan_controller import LoanController
from app.api.loans.loan_schema import (
    LoanSchema,
    LoanCreateSchema, 
    LoanUpdateSchema,
    LoanApprovalSchema,
    LoanResponseSchema, 
    LoanListResponseSchema
)
from app.models.loans.loan_model import LoanStatus
from app.core.http_response import PayTrackHttpResponse

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/", response_model=LoanSchema, status_code=201)
async def create_loan(
    loan_data: LoanCreateSchema,
    # TODO: Obtener el authorizer_id del token JWT del usuario autenticado
    authorizer_id: UUID = Query(description="ID del usuario que autoriza (temporal)"),
    session: Session = Depends(get_db)
):
    """Crear un nuevo préstamo"""
    try:
        controller = LoanController(session)
        
        # Validar que el cliente exista y esté activo
        await controller.validate_client_exists(loan_data.client_id)
        
        # Crear el préstamo
        new_loan = await LoanService.create_loan(loan_data, authorizer_id, session)
        
        return new_loan
    except Exception as e:
        raise e


@router.get("/")
async def get_loans(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por nombre del cliente o identificación"),
    status: Optional[LoanStatus] = Query(None, description="Filtrar por estado del préstamo"),
    client_id: Optional[UUID] = Query(None, description="Filtrar por cliente específico"),
    authorizer_id: Optional[UUID] = Query(None, description="Filtrar por autorizador específico"),
    session: Session = Depends(get_db)
):
    """Obtener lista de préstamos con paginación y filtros"""
    try:
        loans, total = await LoanService.get_loans(
            session=session,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            client_id=client_id,
            authorizer_id=authorizer_id
        )
        
        response_data = {
            "loans": loans,
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(loans)
        }
        
        return response_data
    except Exception as e:
        raise e


@router.get("/{loan_id}")
async def get_loan_by_id(
    loan_id: UUID,
    session: Session = Depends(get_db)
):
    """Obtener un préstamo por su ID"""
    try:
        controller = LoanController(session)
        loan = await controller.get_loan_by_id_or_raise(loan_id)
        
        return loan
    except Exception as e:
        raise e


@router.put("/{loan_id}")
async def update_loan(
    loan_id: UUID,
    loan_data: LoanUpdateSchema,
    session: Session = Depends(get_db)
):
    """Actualizar un préstamo (solo si está pendiente de aprobación)"""
    try:
        controller = LoanController(session)
        
        # Validar que se pueda modificar
        await controller.validate_loan_modification(loan_id)
        
        # Si se actualiza el client_id, validar que el cliente exista
        if loan_data.client_id:
            await controller.validate_client_exists(loan_data.client_id)
        
        # Actualizar el préstamo
        updated_loan = await LoanService.update_loan(loan_id, loan_data, session)
        
        return updated_loan
    except Exception as e:
        raise e


@router.post("/{loan_id}/approval")
async def handle_loan_approval(
    loan_id: UUID,
    approval_data: LoanApprovalSchema,
    session: Session = Depends(get_db)
):
    """Aprobar o rechazar un préstamo"""
    try:
        controller = LoanController(session)
        
        # Validar que se pueda aprobar/rechazar
        await controller.validate_loan_approval_action(loan_id)
        
        if approval_data.action == "approve":
            updated_loan = await LoanService.approve_loan(loan_id, session)
            message = "Préstamo aprobado exitosamente"
        else:  # reject
            updated_loan = await LoanService.reject_loan(loan_id, session)
            message = "Préstamo rechazado exitosamente"
        
        return updated_loan
    except Exception as e:
        raise e


@router.delete("/{loan_id}", status_code=204)
async def delete_loan(
    loan_id: UUID,
    session: Session = Depends(get_db)
):
    """Eliminar un préstamo (soft delete) - solo préstamos pendientes o cancelados"""
    try:
        controller = LoanController(session)
        
        # Verificar que el préstamo existe
        await controller.get_loan_by_id_or_raise(loan_id)
        
        # Eliminar el préstamo
        await LoanService.delete_loan(loan_id, session)
        
        return None
    except Exception as e:
        raise e
