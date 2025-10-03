from uuid import UUID
from typing import Optional

from sqlmodel import Session

from app.api.expenses.expense_service import ExpenseService
from app.api.suppliers.supplier_service import SupplierService
from app.constants.response_codes import PayTrackResponseCodes
from app.core.http_response import PayTrackHttpResponse
from app.models.expenses.expense_model import ExpenseStatus


class ExpenseController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_supplier_exists_if_provided(self, supplier_id: Optional[UUID]) -> bool:
        """Valida que el proveedor exista si se proporciona"""
        if supplier_id:
            supplier = await SupplierService.get_supplier_by_id(
                supplier_id=supplier_id, session=self.session
            )
            if not supplier:
                raise PayTrackHttpResponse.not_found(
                    data={
                        "message": "Proveedor no encontrado",
                        "supplier_id": str(supplier_id),
                    },
                    error_id="SUPPLIER_NOT_FOUND",
                )
            
            if not supplier.is_active:
                raise PayTrackHttpResponse.forbidden(
                    data={
                        "message": "El proveedor debe estar activo",
                        "supplier_id": str(supplier_id),
                        "supplier_status": supplier.status.value,
                    },
                    error_id="SUPPLIER_NOT_ACTIVE",
                )
        return True

    async def get_expense_by_id_or_raise(self, expense_id: UUID):
        """Obtiene un gasto por ID o lanza excepción si no existe"""
        expense = await ExpenseService.get_expense_by_id(
            expense_id=expense_id, session=self.session
        )
        if not expense:
            raise PayTrackHttpResponse.not_found(
                data={
                    "message": "Gasto no encontrado",
                    "expense_id": str(expense_id),
                },
                error_id="EXPENSE_NOT_FOUND",
            )
        return expense

    async def validate_expense_modification(self, expense_id: UUID) -> bool:
        """Valida que el gasto se pueda modificar"""
        expense = await self.get_expense_by_id_or_raise(expense_id)
        
        # Solo se pueden modificar gastos pendientes
        if expense.status not in [ExpenseStatus.pending, ExpenseStatus.rejected]:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Solo se pueden modificar gastos pendientes o rechazados",
                    "expense_id": str(expense_id),
                    "current_status": expense.status.value,
                },
                error_id="EXPENSE_NOT_MODIFIABLE",
            )
        return True

    async def validate_expense_approval_action(self, expense_id: UUID, action: str) -> bool:
        """Valida que se pueda realizar la acción de aprobación"""
        expense = await self.get_expense_by_id_or_raise(expense_id)
        
        if action == "approve" and expense.status != ExpenseStatus.pending:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Solo se pueden aprobar gastos pendientes",
                    "expense_id": str(expense_id),
                    "current_status": expense.status.value,
                },
                error_id="EXPENSE_NOT_APPROVABLE",
            )
            
        elif action == "reject" and expense.status not in [ExpenseStatus.pending, ExpenseStatus.approved]:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Solo se pueden rechazar gastos pendientes o aprobados",
                    "expense_id": str(expense_id),
                    "current_status": expense.status.value,
                },
                error_id="EXPENSE_NOT_REJECTABLE",
            )
            
        elif action == "pay" and expense.status != ExpenseStatus.approved:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Solo se pueden pagar gastos aprobados",
                    "expense_id": str(expense_id),
                    "current_status": expense.status.value,
                },
                error_id="EXPENSE_NOT_PAYABLE",
            )
        return True