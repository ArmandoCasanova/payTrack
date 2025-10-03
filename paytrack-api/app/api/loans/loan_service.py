from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

from sqlmodel import Session, select
from sqlalchemy import or_, and_

from app.models.loans.loan_model import LoanModel, LoanStatus
from app.models.clients.client_model import ClientModel
from app.models.users.user_model import UserModel
from .loan_schema import LoanCreateSchema, LoanUpdateSchema

from app.core.http_response import PayTrackHttpResponse


class LoanService:
    @staticmethod
    async def create_loan(
        loan_data: LoanCreateSchema, authorizer_id: UUID, session: Session
    ) -> LoanModel:
        try:
            loan_dump = loan_data.model_dump()

            new_loan = LoanModel(
                client_id=loan_dump["client_id"],
                authorizer_id=authorizer_id,
                amount=loan_dump["amount"],
                payment_count=loan_dump["payment_count"],
                interest_rate=loan_dump["interest_rate"],
                payment_start_date=loan_dump["payment_start_date"],
                late_interest=loan_dump["late_interest"],
                status=LoanStatus.pending_approval
            )

            # Calcular montos
            total_with_interest = new_loan.amount * (1 + new_loan.interest_rate)
            new_loan.total_amount = total_with_interest
            new_loan.remaining_amount = total_with_interest

            session.add(new_loan)
            session.commit()
            session.refresh(new_loan)

            return new_loan
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_loan_by_id(loan_id: UUID, session: Session) -> Optional[LoanModel]:
        try:
            statement = select(LoanModel).where(
                and_(
                    LoanModel.loan_id == loan_id,
                    LoanModel.deleted_at.is_(None)
                )
            )
            loan = session.exec(statement).first()
            return loan
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_loans(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[LoanStatus] = None,
        client_id: Optional[UUID] = None,
        authorizer_id: Optional[UUID] = None
    ) -> tuple[List[dict], int]:
        try:
            # Query con JOINs para obtener información adicional
            query = select(
                LoanModel,
                ClientModel.name.label("client_name"),
                ClientModel.paternal_surname.label("client_paternal"),
                ClientModel.maternal_surname.label("client_maternal"),
                UserModel.name.label("authorizer_name")
            ).join(
                ClientModel, LoanModel.client_id == ClientModel.client_id
            ).join(
                UserModel, LoanModel.authorizer_id == UserModel.user_id
            ).where(LoanModel.deleted_at.is_(None))
            
            # Aplicar filtros
            if search:
                search_filter = or_(
                    ClientModel.name.ilike(f"%{search}%"),
                    ClientModel.paternal_surname.ilike(f"%{search}%"),
                    ClientModel.maternal_surname.ilike(f"%{search}%"),
                    ClientModel.national_id.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if status:
                query = query.where(LoanModel.status == status)
                
            if client_id:
                query = query.where(LoanModel.client_id == client_id)
                
            if authorizer_id:
                query = query.where(LoanModel.authorizer_id == authorizer_id)
            
            # Contar total
            total_query = query
            total = len(session.exec(total_query).all())
            
            # Aplicar paginación
            query = query.offset(skip).limit(limit)
            results = session.exec(query).all()
            
            # Formatear resultados
            loans_data = []
            for result in results:
                loan, client_name, client_paternal, client_maternal, authorizer_name = result
                loan_dict = {
                    **loan.model_dump(),
                    "client_name": f"{client_name} {client_paternal} {client_maternal}".strip(),
                    "authorizer_name": authorizer_name,
                    "payment_amount": loan.calculate_payment_amount(),
                    "is_active": loan.is_active,
                    "is_completed": loan.is_completed,
                    "is_overdue": loan.is_overdue
                }
                loans_data.append(loan_dict)
            
            return loans_data, total
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_loan(
        loan_id: UUID, 
        loan_data: LoanUpdateSchema, 
        session: Session
    ) -> Optional[LoanModel]:
        try:
            loan = await LoanService.get_loan_by_id(loan_id, session)
            if not loan:
                return None

            loan_dump = loan_data.model_dump(exclude_unset=True)
            
            for field, value in loan_dump.items():
                if hasattr(loan, field):
                    setattr(loan, field, value)
            
            # Recalcular montos si se actualizó el amount o interest_rate
            if 'amount' in loan_dump or 'interest_rate' in loan_dump:
                total_with_interest = loan.amount * (1 + loan.interest_rate)
                loan.total_amount = total_with_interest
                # Solo actualizar remaining_amount si el préstamo no ha iniciado pagos
                if loan.status == LoanStatus.pending_approval:
                    loan.remaining_amount = total_with_interest
            
            loan.updated_at = datetime.now(timezone.utc)
            session.add(loan)
            session.commit()
            session.refresh(loan)
            
            return loan
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def approve_loan(loan_id: UUID, session: Session) -> Optional[LoanModel]:
        try:
            loan = await LoanService.get_loan_by_id(loan_id, session)
            if not loan:
                return None
                
            if loan.status != LoanStatus.pending_approval:
                raise ValueError("Solo se pueden aprobar préstamos pendientes")
            
            loan.status = LoanStatus.active
            loan.updated_at = datetime.now(timezone.utc)
            session.add(loan)
            session.commit()
            session.refresh(loan)
            
            return loan
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def reject_loan(loan_id: UUID, session: Session) -> Optional[LoanModel]:
        try:
            loan = await LoanService.get_loan_by_id(loan_id, session)
            if not loan:
                return None
                
            if loan.status != LoanStatus.pending_approval:
                raise ValueError("Solo se pueden rechazar préstamos pendientes")
            
            loan.status = LoanStatus.cancelled
            loan.updated_at = datetime.now(timezone.utc)
            session.add(loan)
            session.commit()
            session.refresh(loan)
            
            return loan
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def delete_loan(loan_id: UUID, session: Session) -> bool:
        try:
            loan = await LoanService.get_loan_by_id(loan_id, session)
            if not loan:
                return False

            # Solo permitir eliminar préstamos pendientes o cancelados
            if loan.status in [LoanStatus.active, LoanStatus.completed]:
                raise ValueError("No se pueden eliminar préstamos activos o completados")

            loan.deleted_at = datetime.now(timezone.utc)
            session.add(loan)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e