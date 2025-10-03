from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_db
from app.api.payments.payment_service import PaymentService
from app.api.payments.payment_controller import PaymentController
from app.api.payments.payment_schema import (
    PaymentSchema,
    PaymentCreateSchema, 
    PaymentUpdateSchema,
    PaymentProcessSchema,
    PaymentResponseSchema, 
    PaymentListResponseSchema,
    PaymentSummarySchema
)
from app.models.payments.payment_model import PaymentStatus, PaymentMethod
from app.core.http_response import PayTrackHttpResponse

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentSchema, status_code=201)
async def create_payment(
    payment_data: PaymentCreateSchema,
    # TODO: Obtener el responsible_id del token JWT del usuario autenticado
    responsible_id: UUID = Query(description="ID del usuario responsable (temporal)"),
    session: Session = Depends(get_db)
):
    """Crear un nuevo pago"""
    try:
        controller = PaymentController(session)
        
        # Validar que el cliente exista y esté activo
        await controller.validate_client_exists(payment_data.client_id)
        
        # Crear el pago
        new_payment = await PaymentService.create_payment(payment_data, responsible_id, session)
        
        return new_payment
    except Exception as e:
        raise e


@router.get("/")
async def get_payments(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por cliente, identificación o referencia"),
    status: Optional[PaymentStatus] = Query(None, description="Filtrar por estado del pago"),
    client_id: Optional[UUID] = Query(None, description="Filtrar por cliente específico"),
    responsible_id: Optional[UUID] = Query(None, description="Filtrar por responsable específico"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filtrar por método de pago"),
    session: Session = Depends(get_db)
):
    """Obtener lista de pagos con paginación y filtros"""
    try:
        payments, total = await PaymentService.get_payments(
            session=session,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            client_id=client_id,
            responsible_id=responsible_id,
            payment_method=payment_method
        )
        
        response_data = {
            "payments": payments,
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(payments)
        }
        
        return response_data
    except Exception as e:
        raise e


@router.get("/summary")
async def get_payments_summary(
    session: Session = Depends(get_db)
):
    """Obtener resumen de pagos por estado"""
    try:
        summary = await PaymentService.get_payments_summary(session)
        
        return summary
    except Exception as e:
        raise e


@router.get("/{payment_id}")
async def get_payment_by_id(
    payment_id: UUID,
    session: Session = Depends(get_db)
):
    """Obtener un pago por su ID"""
    try:
        controller = PaymentController(session)
        payment = await controller.get_payment_by_id_or_raise(payment_id)
        
        return payment
    except Exception as e:
        raise e


@router.put("/{payment_id}")
async def update_payment(
    payment_id: UUID,
    payment_data: PaymentUpdateSchema,
    session: Session = Depends(get_db)
):
    """Actualizar un pago (solo si no está procesado)"""
    try:
        controller = PaymentController(session)
        
        # Validar que se pueda modificar
        await controller.validate_payment_modification(payment_id)
        
        # Si se actualiza el client_id, validar que el cliente exista
        if payment_data.client_id:
            await controller.validate_client_exists(payment_data.client_id)
        
        # Actualizar el pago
        updated_payment = await PaymentService.update_payment(payment_id, payment_data, session)
        
        return updated_payment
    except Exception as e:
        raise e


@router.post("/{payment_id}/process")
async def process_payment_action(
    payment_id: UUID,
    action_data: PaymentProcessSchema,
    session: Session = Depends(get_db)
):
    """Procesar, cancelar o marcar como vencido un pago"""
    try:
        controller = PaymentController(session)
        
        if action_data.action == "process":
            # Validar que se pueda procesar
            await controller.validate_payment_processing(payment_id)
            updated_payment = await PaymentService.process_payment(
                payment_id, action_data.payment_date, session
            )
            message = "Pago procesado exitosamente"
            
        elif action_data.action == "cancel":
            updated_payment = await PaymentService.cancel_payment(payment_id, session)
            message = "Pago cancelado exitosamente"
            
        else:  # mark_overdue
            updated_payment = await PaymentService.mark_payment_overdue(payment_id, session)
            message = "Pago marcado como vencido exitosamente"
        
        return updated_payment
    except Exception as e:
        raise e


@router.delete("/{payment_id}", status_code=204)
async def delete_payment(
    payment_id: UUID,
    session: Session = Depends(get_db)
):
    """Eliminar un pago (soft delete) - solo pagos pendientes o cancelados"""
    try:
        controller = PaymentController(session)
        
        # Verificar que el pago existe
        await controller.get_payment_by_id_or_raise(payment_id)
        
        # Eliminar el pago
        await PaymentService.delete_payment(payment_id, session)
        
        return None
    except Exception as e:
        raise e
