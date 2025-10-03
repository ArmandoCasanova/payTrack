from uuid import UUID
from typing import Optional

from sqlmodel import Session

from app.api.loans.loan_service import LoanService
from app.api.clients.client_service import ClientService
from app.constants.response_codes import PayTrackResponseCodes
from app.core.http_response import PayTrackHttpResponse
from app.models.loans.loan_model import LoanStatus


class LoanController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_client_exists(self, client_id: UUID) -> bool:
        """Valida que el cliente exista y esté activo"""
        client = await ClientService.get_client_by_id(
            client_id=client_id, session=self.session
        )
        if not client:
            raise PayTrackHttpResponse.not_found(
                data={
                    "message": "Cliente no encontrado",
                    "client_id": str(client_id),
                },
                error_id="CLIENT_NOT_FOUND",
            )
        
        if not client.is_active:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "El cliente debe estar activo para crear un préstamo",
                    "client_id": str(client_id),
                    "client_status": client.status.value,
                },
                error_id="CLIENT_NOT_ACTIVE",
            )
        return True

    async def get_loan_by_id_or_raise(self, loan_id: UUID):
        """Obtiene un préstamo por ID o lanza excepción si no existe"""
        loan = await LoanService.get_loan_by_id(
            loan_id=loan_id, session=self.session
        )
        if not loan:
            raise PayTrackHttpResponse.not_found(
                data={
                    "message": "Préstamo no encontrado",
                    "loan_id": str(loan_id),
                },
                error_id="LOAN_NOT_FOUND",
            )
        return loan

    async def validate_loan_modification(self, loan_id: UUID) -> bool:
        """Valida que el préstamo se pueda modificar"""
        loan = await self.get_loan_by_id_or_raise(loan_id)
        
        # Solo se pueden modificar préstamos pendientes
        if loan.status != LoanStatus.pending_approval:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Solo se pueden modificar préstamos pendientes de aprobación",
                    "loan_id": str(loan_id),
                    "current_status": loan.status.value,
                },
                error_id="LOAN_NOT_MODIFIABLE",
            )
        return True

    async def validate_loan_approval_action(self, loan_id: UUID) -> bool:
        """Valida que el préstamo se pueda aprobar/rechazar"""
        loan = await self.get_loan_by_id_or_raise(loan_id)
        
        if loan.status != LoanStatus.pending_approval:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Solo se pueden aprobar/rechazar préstamos pendientes",
                    "loan_id": str(loan_id),
                    "current_status": loan.status.value,
                },
                error_id="LOAN_NOT_PENDING",
            )
        return True