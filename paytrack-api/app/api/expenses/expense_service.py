from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

from sqlmodel import Session, select, func
from sqlalchemy import or_, and_

from app.models.expenses.expense_model import ExpenseModel, ExpenseStatus, ExpenseCategory
from app.models.suppliers.supplier_model import SupplierModel
from app.models.users.user_model import UserModel
from .expense_schema import ExpenseCreateSchema, ExpenseUpdateSchema

from app.core.http_response import PayTrackHttpResponse


class ExpenseService:
    @staticmethod
    async def create_expense(
        expense_data: ExpenseCreateSchema, responsible_id: UUID, session: Session
    ) -> ExpenseModel:
        try:
            expense_dump = expense_data.model_dump()

            new_expense = ExpenseModel(
                responsible_id=responsible_id,
                supplier_id=expense_dump.get("supplier_id"),
                expense_date=expense_dump["expense_date"],
                payment_method=expense_dump["payment_method"],
                description=expense_dump["description"],
                amount=expense_dump["amount"],
                category=expense_dump.get("category", ExpenseCategory.other),
                status=ExpenseStatus.pending,
                invoice_number=expense_dump.get("invoice_number"),
                receipt_path=expense_dump.get("receipt_path"),
                notes=expense_dump.get("notes")
            )

            session.add(new_expense)
            session.commit()
            session.refresh(new_expense)

            return new_expense
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_expense_by_id(expense_id: UUID, session: Session) -> Optional[ExpenseModel]:
        try:
            statement = select(ExpenseModel).where(
                and_(
                    ExpenseModel.expense_id == expense_id,
                    ExpenseModel.deleted_at.is_(None)
                )
            )
            expense = session.exec(statement).first()
            return expense
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_expenses(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[ExpenseStatus] = None,
        category: Optional[ExpenseCategory] = None,
        supplier_id: Optional[UUID] = None,
        responsible_id: Optional[UUID] = None
    ) -> tuple[List[dict], int]:
        try:
            # Query con JOINs para obtener información adicional
            query = select(
                ExpenseModel,
                UserModel.name.label("responsible_name"),
                SupplierModel.name.label("supplier_name")
            ).join(
                UserModel, ExpenseModel.responsible_id == UserModel.user_id
            ).outerjoin(
                SupplierModel, ExpenseModel.supplier_id == SupplierModel.supplier_id
            ).where(ExpenseModel.deleted_at.is_(None))
            
            # Aplicar filtros
            if search:
                search_filter = or_(
                    ExpenseModel.description.ilike(f"%{search}%"),
                    ExpenseModel.invoice_number.ilike(f"%{search}%"),
                    UserModel.name.ilike(f"%{search}%"),
                    SupplierModel.name.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if status:
                query = query.where(ExpenseModel.status == status)
                
            if category:
                query = query.where(ExpenseModel.category == category)
                
            if supplier_id:
                query = query.where(ExpenseModel.supplier_id == supplier_id)
                
            if responsible_id:
                query = query.where(ExpenseModel.responsible_id == responsible_id)
            
            # Contar total
            total_query = query
            total = len(session.exec(total_query).all())
            
            # Aplicar paginación
            query = query.offset(skip).limit(limit)
            results = session.exec(query).all()
            
            # Formatear resultados
            expenses_data = []
            for result in results:
                expense, responsible_name, supplier_name = result
                expense_dict = {
                    **expense.model_dump(),
                    "responsible_name": responsible_name,
                    "supplier_name": supplier_name,
                    "is_paid": expense.is_paid,
                    "is_pending": expense.is_pending
                }
                expenses_data.append(expense_dict)
            
            return expenses_data, total
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_expense(
        expense_id: UUID, 
        expense_data: ExpenseUpdateSchema, 
        session: Session
    ) -> Optional[ExpenseModel]:
        try:
            expense = await ExpenseService.get_expense_by_id(expense_id, session)
            if not expense:
                return None

            expense_dump = expense_data.model_dump(exclude_unset=True)
            
            for field, value in expense_dump.items():
                if hasattr(expense, field):
                    setattr(expense, field, value)
            
            expense.updated_at = datetime.now(timezone.utc)
            session.add(expense)
            session.commit()
            session.refresh(expense)
            
            return expense
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def approve_expense(expense_id: UUID, session: Session) -> Optional[ExpenseModel]:
        try:
            expense = await ExpenseService.get_expense_by_id(expense_id, session)
            if not expense:
                return None
                
            if expense.status != ExpenseStatus.pending:
                raise ValueError("Solo se pueden aprobar gastos pendientes")
            
            expense.status = ExpenseStatus.approved
            expense.updated_at = datetime.now(timezone.utc)
            session.add(expense)
            session.commit()
            session.refresh(expense)
            
            return expense
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def reject_expense(expense_id: UUID, session: Session) -> Optional[ExpenseModel]:
        try:
            expense = await ExpenseService.get_expense_by_id(expense_id, session)
            if not expense:
                return None
                
            if expense.status not in [ExpenseStatus.pending, ExpenseStatus.approved]:
                raise ValueError("Solo se pueden rechazar gastos pendientes o aprobados")
            
            expense.status = ExpenseStatus.rejected
            expense.updated_at = datetime.now(timezone.utc)
            session.add(expense)
            session.commit()
            session.refresh(expense)
            
            return expense
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def pay_expense(expense_id: UUID, session: Session) -> Optional[ExpenseModel]:
        try:
            expense = await ExpenseService.get_expense_by_id(expense_id, session)
            if not expense:
                return None
                
            if expense.status != ExpenseStatus.approved:
                raise ValueError("Solo se pueden pagar gastos aprobados")
            
            expense.status = ExpenseStatus.paid
            expense.updated_at = datetime.now(timezone.utc)
            session.add(expense)
            session.commit()
            session.refresh(expense)
            
            return expense
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def delete_expense(expense_id: UUID, session: Session) -> bool:
        try:
            expense = await ExpenseService.get_expense_by_id(expense_id, session)
            if not expense:
                return False

            # Solo permitir eliminar gastos pendientes o rechazados
            if expense.status in [ExpenseStatus.approved, ExpenseStatus.paid]:
                raise ValueError("No se pueden eliminar gastos aprobados o pagados")

            expense.deleted_at = datetime.now(timezone.utc)
            session.add(expense)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_expenses_summary(session: Session) -> dict:
        try:
            # Obtener resumen de gastos por estado
            pending_sum = session.exec(
                select(func.coalesce(func.sum(ExpenseModel.amount), 0))
                .where(and_(ExpenseModel.status == ExpenseStatus.pending, ExpenseModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            approved_sum = session.exec(
                select(func.coalesce(func.sum(ExpenseModel.amount), 0))
                .where(and_(ExpenseModel.status == ExpenseStatus.approved, ExpenseModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            paid_sum = session.exec(
                select(func.coalesce(func.sum(ExpenseModel.amount), 0))
                .where(and_(ExpenseModel.status == ExpenseStatus.paid, ExpenseModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            rejected_sum = session.exec(
                select(func.coalesce(func.sum(ExpenseModel.amount), 0))
                .where(and_(ExpenseModel.status == ExpenseStatus.rejected, ExpenseModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            # Contar gastos por estado
            pending_count = session.exec(
                select(func.count(ExpenseModel.expense_id))
                .where(and_(ExpenseModel.status == ExpenseStatus.pending, ExpenseModel.deleted_at.is_(None)))
            ).first() or 0
            
            approved_count = session.exec(
                select(func.count(ExpenseModel.expense_id))
                .where(and_(ExpenseModel.status == ExpenseStatus.approved, ExpenseModel.deleted_at.is_(None)))
            ).first() or 0
            
            paid_count = session.exec(
                select(func.count(ExpenseModel.expense_id))
                .where(and_(ExpenseModel.status == ExpenseStatus.paid, ExpenseModel.deleted_at.is_(None)))
            ).first() or 0
            
            rejected_count = session.exec(
                select(func.count(ExpenseModel.expense_id))
                .where(and_(ExpenseModel.status == ExpenseStatus.rejected, ExpenseModel.deleted_at.is_(None)))
            ).first() or 0
            
            # Gastos por categoría
            category_results = session.exec(
                select(ExpenseModel.category, func.sum(ExpenseModel.amount))
                .where(and_(ExpenseModel.status == ExpenseStatus.paid, ExpenseModel.deleted_at.is_(None)))
                .group_by(ExpenseModel.category)
            ).all()
            
            by_category = {category.value: amount for category, amount in category_results}
            
            return {
                "total_pending": pending_sum,
                "total_approved": approved_sum,
                "total_paid": paid_sum,
                "total_rejected": rejected_sum,
                "count_pending": pending_count,
                "count_approved": approved_count,
                "count_paid": paid_count,
                "count_rejected": rejected_count,
                "by_category": by_category
            }
        except Exception:
            raise PayTrackHttpResponse.internal_error()