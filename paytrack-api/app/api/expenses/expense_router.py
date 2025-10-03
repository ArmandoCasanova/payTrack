from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_db
from app.api.expenses.expense_service import ExpenseService
from app.api.expenses.expense_controller import ExpenseController
from app.api.expenses.expense_schema import (
    ExpenseSchema,
    ExpenseCreateSchema, 
    ExpenseUpdateSchema,
    ExpenseApprovalSchema,
    ExpenseResponseSchema, 
    ExpenseListResponseSchema,
    ExpenseSummarySchema
)
from app.models.expenses.expense_model import ExpenseStatus, ExpenseCategory
from app.core.http_response import PayTrackHttpResponse

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseSchema, status_code=201)
async def create_expense(
    expense_data: ExpenseCreateSchema,
    # TODO: Obtener el responsible_id del token JWT del usuario autenticado
    responsible_id: UUID = Query(description="ID del usuario responsable (temporal)"),
    session: Session = Depends(get_db)
):
    """Crear un nuevo gasto"""
    try:
        controller = ExpenseController(session)
        
        # Validar que el proveedor exista si se proporciona
        await controller.validate_supplier_exists_if_provided(expense_data.supplier_id)
        
        # Crear el gasto
        new_expense = await ExpenseService.create_expense(expense_data, responsible_id, session)
        
        return new_expense
    except Exception as e:
        raise e


@router.get("/")
async def get_expenses(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por descripción, factura, responsable o proveedor"),
    status: Optional[ExpenseStatus] = Query(None, description="Filtrar por estado del gasto"),
    category: Optional[ExpenseCategory] = Query(None, description="Filtrar por categoría del gasto"),
    supplier_id: Optional[UUID] = Query(None, description="Filtrar por proveedor específico"),
    responsible_id: Optional[UUID] = Query(None, description="Filtrar por responsable específico"),
    session: Session = Depends(get_db)
):
    """Obtener lista de gastos con paginación y filtros"""
    try:
        expenses, total = await ExpenseService.get_expenses(
            session=session,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            category=category,
            supplier_id=supplier_id,
            responsible_id=responsible_id
        )
        
        response_data = {
            "expenses": expenses,
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(expenses)
        }
        
        return response_data
    except Exception as e:
        raise e


@router.get("/summary")
async def get_expenses_summary(
    session: Session = Depends(get_db)
):
    """Obtener resumen de gastos por estado y categoría"""
    try:
        summary = await ExpenseService.get_expenses_summary(session)
        
        return summary
    except Exception as e:
        raise e


@router.get("/{expense_id}")
async def get_expense_by_id(
    expense_id: UUID,
    session: Session = Depends(get_db)
):
    """Obtener un gasto por su ID"""
    try:
        controller = ExpenseController(session)
        expense = await controller.get_expense_by_id_or_raise(expense_id)
        
        return expense
    except Exception as e:
        raise e


@router.put("/{expense_id}")
async def update_expense(
    expense_id: UUID,
    expense_data: ExpenseUpdateSchema,
    session: Session = Depends(get_db)
):
    """Actualizar un gasto (solo si está pendiente o rechazado)"""
    try:
        controller = ExpenseController(session)
        
        # Validar que se pueda modificar
        await controller.validate_expense_modification(expense_id)
        
        # Si se actualiza el supplier_id, validar que el proveedor exista
        if expense_data.supplier_id:
            await controller.validate_supplier_exists_if_provided(expense_data.supplier_id)
        
        # Actualizar el gasto
        updated_expense = await ExpenseService.update_expense(expense_id, expense_data, session)
        
        return updated_expense
    except Exception as e:
        raise e


@router.post("/{expense_id}/approval")
async def handle_expense_approval(
    expense_id: UUID,
    approval_data: ExpenseApprovalSchema,
    session: Session = Depends(get_db)
):
    """Aprobar, rechazar o pagar un gasto"""
    try:
        controller = ExpenseController(session)
        
        # Validar que se pueda realizar la acción
        await controller.validate_expense_approval_action(expense_id, approval_data.action)
        
        if approval_data.action == "approve":
            updated_expense = await ExpenseService.approve_expense(expense_id, session)
            message = "Gasto aprobado exitosamente"
            
        elif approval_data.action == "reject":
            updated_expense = await ExpenseService.reject_expense(expense_id, session)
            message = "Gasto rechazado exitosamente"
            
        else:  # pay
            updated_expense = await ExpenseService.pay_expense(expense_id, session)
            message = "Gasto marcado como pagado exitosamente"
        
        return updated_expense
    except Exception as e:
        raise e


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: UUID,
    session: Session = Depends(get_db)
):
    """Eliminar un gasto (soft delete) - solo gastos pendientes o rechazados"""
    try:
        controller = ExpenseController(session)
        
        # Verificar que el gasto existe
        await controller.get_expense_by_id_or_raise(expense_id)
        
        # Eliminar el gasto
        await ExpenseService.delete_expense(expense_id, session)
        
        return None
    except Exception as e:
        raise e
