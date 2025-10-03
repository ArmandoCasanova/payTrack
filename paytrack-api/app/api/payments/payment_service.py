from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

from sqlmodel import Session, select, func
from sqlalchemy import or_, and_

from app.models.payments.payment_model import PaymentModel, PaymentStatus, PaymentMethod
from app.models.clients.client_model import ClientModel
from app.models.users.user_model import UserModel
from .payment_schema import PaymentCreateSchema, PaymentUpdateSchema

from app.core.http_response import PayTrackHttpResponse


class PaymentService:
    @staticmethod
    async def create_payment(
        payment_data: PaymentCreateSchema, responsible_id: UUID, session: Session
    ) -> PaymentModel:
        try:
            payment_dump = payment_data.model_dump()

            new_payment = PaymentModel(
                client_id=payment_dump["client_id"],
                responsible_id=responsible_id,
                amount=payment_dump["amount"],
                interest_amount=payment_dump.get("interest_amount", Decimal("0.00")),
                payment_method=payment_dump["payment_method"],
                status=PaymentStatus.pending,
                due_date=payment_dump.get("due_date"),
                notes=payment_dump.get("notes"),
                reference=payment_dump.get("reference")
            )

            session.add(new_payment)
            session.commit()
            session.refresh(new_payment)

            return new_payment
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_payment_by_id(payment_id: UUID, session: Session) -> Optional[PaymentModel]:
        try:
            statement = select(PaymentModel).where(
                and_(
                    PaymentModel.payment_id == payment_id,
                    PaymentModel.deleted_at.is_(None)
                )
            )
            payment = session.exec(statement).first()
            return payment
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_payments(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[PaymentStatus] = None,
        client_id: Optional[UUID] = None,
        responsible_id: Optional[UUID] = None,
        payment_method: Optional[PaymentMethod] = None
    ) -> tuple[List[dict], int]:
        try:
            # Query con JOINs para obtener información adicional
            query = select(
                PaymentModel,
                ClientModel.name.label("client_name"),
                ClientModel.paternal_surname.label("client_paternal"),
                ClientModel.maternal_surname.label("client_maternal"),
                UserModel.name.label("responsible_name")
            ).join(
                ClientModel, PaymentModel.client_id == ClientModel.client_id
            ).join(
                UserModel, PaymentModel.responsible_id == UserModel.user_id
            ).where(PaymentModel.deleted_at.is_(None))
            
            # Aplicar filtros
            if search:
                search_filter = or_(
                    ClientModel.name.ilike(f"%{search}%"),
                    ClientModel.paternal_surname.ilike(f"%{search}%"),
                    ClientModel.maternal_surname.ilike(f"%{search}%"),
                    ClientModel.national_id.ilike(f"%{search}%"),
                    PaymentModel.reference.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if status:
                query = query.where(PaymentModel.status == status)
                
            if client_id:
                query = query.where(PaymentModel.client_id == client_id)
                
            if responsible_id:
                query = query.where(PaymentModel.responsible_id == responsible_id)
                
            if payment_method:
                query = query.where(PaymentModel.payment_method == payment_method)
            
            # Contar total
            total_query = query
            total = len(session.exec(total_query).all())
            
            # Aplicar paginación
            query = query.offset(skip).limit(limit)
            results = session.exec(query).all()
            
            # Formatear resultados
            payments_data = []
            for result in results:
                payment, client_name, client_paternal, client_maternal, responsible_name = result
                payment_dict = {
                    **payment.model_dump(),
                    "client_name": f"{client_name} {client_paternal} {client_maternal}".strip(),
                    "responsible_name": responsible_name,
                    "total_amount": payment.total_amount,
                    "is_paid": payment.is_paid,
                    "is_overdue": payment.is_overdue,
                    "days_overdue": payment.days_overdue
                }
                payments_data.append(payment_dict)
            
            return payments_data, total
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_payment(
        payment_id: UUID, 
        payment_data: PaymentUpdateSchema, 
        session: Session
    ) -> Optional[PaymentModel]:
        try:
            payment = await PaymentService.get_payment_by_id(payment_id, session)
            if not payment:
                return None

            payment_dump = payment_data.model_dump(exclude_unset=True)
            
            for field, value in payment_dump.items():
                if hasattr(payment, field):
                    setattr(payment, field, value)
            
            payment.updated_at = datetime.now(timezone.utc)
            session.add(payment)
            session.commit()
            session.refresh(payment)
            
            return payment
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def process_payment(payment_id: UUID, payment_date: datetime, session: Session) -> Optional[PaymentModel]:
        try:
            payment = await PaymentService.get_payment_by_id(payment_id, session)
            if not payment:
                return None
                
            if payment.status == PaymentStatus.paid:
                raise ValueError("El pago ya está procesado")
            
            payment.status = PaymentStatus.paid
            payment.payment_date = payment_date
            payment.updated_at = datetime.now(timezone.utc)
            session.add(payment)
            session.commit()
            session.refresh(payment)
            
            return payment
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def cancel_payment(payment_id: UUID, session: Session) -> Optional[PaymentModel]:
        try:
            payment = await PaymentService.get_payment_by_id(payment_id, session)
            if not payment:
                return None
                
            if payment.status == PaymentStatus.paid:
                raise ValueError("No se puede cancelar un pago ya procesado")
            
            payment.status = PaymentStatus.cancelled
            payment.updated_at = datetime.now(timezone.utc)
            session.add(payment)
            session.commit()
            session.refresh(payment)
            
            return payment
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def mark_payment_overdue(payment_id: UUID, session: Session) -> Optional[PaymentModel]:
        try:
            payment = await PaymentService.get_payment_by_id(payment_id, session)
            if not payment:
                return None
                
            if payment.status == PaymentStatus.paid:
                raise ValueError("No se puede marcar como vencido un pago ya procesado")
            
            payment.status = PaymentStatus.overdue
            payment.updated_at = datetime.now(timezone.utc)
            session.add(payment)
            session.commit()
            session.refresh(payment)
            
            return payment
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def delete_payment(payment_id: UUID, session: Session) -> bool:
        try:
            payment = await PaymentService.get_payment_by_id(payment_id, session)
            if not payment:
                return False

            # Solo permitir eliminar pagos pendientes o cancelados
            if payment.status == PaymentStatus.paid:
                raise ValueError("No se pueden eliminar pagos ya procesados")

            payment.deleted_at = datetime.now(timezone.utc)
            session.add(payment)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_payments_summary(session: Session) -> dict:
        try:
            # Obtener resumen de pagos
            pending_sum = session.exec(
                select(func.coalesce(func.sum(PaymentModel.amount + PaymentModel.interest_amount), 0))
                .where(and_(PaymentModel.status == PaymentStatus.pending, PaymentModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            paid_sum = session.exec(
                select(func.coalesce(func.sum(PaymentModel.amount + PaymentModel.interest_amount), 0))
                .where(and_(PaymentModel.status == PaymentStatus.paid, PaymentModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            overdue_sum = session.exec(
                select(func.coalesce(func.sum(PaymentModel.amount + PaymentModel.interest_amount), 0))
                .where(and_(PaymentModel.status == PaymentStatus.overdue, PaymentModel.deleted_at.is_(None)))
            ).first() or Decimal("0.00")
            
            # Contar pagos por estado
            pending_count = session.exec(
                select(func.count(PaymentModel.payment_id))
                .where(and_(PaymentModel.status == PaymentStatus.pending, PaymentModel.deleted_at.is_(None)))
            ).first() or 0
            
            paid_count = session.exec(
                select(func.count(PaymentModel.payment_id))
                .where(and_(PaymentModel.status == PaymentStatus.paid, PaymentModel.deleted_at.is_(None)))
            ).first() or 0
            
            overdue_count = session.exec(
                select(func.count(PaymentModel.payment_id))
                .where(and_(PaymentModel.status == PaymentStatus.overdue, PaymentModel.deleted_at.is_(None)))
            ).first() or 0
            
            return {
                "total_pending": pending_sum,
                "total_paid": paid_sum,
                "total_overdue": overdue_sum,
                "count_pending": pending_count,
                "count_paid": paid_count,
                "count_overdue": overdue_count
            }
        except Exception:
            raise PayTrackHttpResponse.internal_error()