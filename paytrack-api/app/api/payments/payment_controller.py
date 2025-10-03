from uuid import UUID
from typing import Optional

from sqlmodel import Session

from app.api.payments.payment_service import PaymentService
from app.api.clients.client_service import ClientService
from app.constants.response_codes import PayTrackResponseCodes
from app.core.http_response import PayTrackHttpResponse
from app.models.payments.payment_model import PaymentStatus


class PaymentController:
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
                    "message": "El cliente debe estar activo para crear un pago",
                    "client_id": str(client_id),
                    "client_status": client.status.value,
                },
                error_id="CLIENT_NOT_ACTIVE",
            )
        return True

    async def get_payment_by_id_or_raise(self, payment_id: UUID):
        """Obtiene un pago por ID o lanza excepción si no existe"""
        payment = await PaymentService.get_payment_by_id(
            payment_id=payment_id, session=self.session
        )
        if not payment:
            raise PayTrackHttpResponse.not_found(
                data={
                    "message": "Pago no encontrado",
                    "payment_id": str(payment_id),
                },
                error_id="PAYMENT_NOT_FOUND",
            )
        return payment

    async def validate_payment_modification(self, payment_id: UUID) -> bool:
        """Valida que el pago se pueda modificar"""
        payment = await self.get_payment_by_id_or_raise(payment_id)
        
        # No se pueden modificar pagos ya procesados
        if payment.status == PaymentStatus.paid:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "No se pueden modificar pagos ya procesados",
                    "payment_id": str(payment_id),
                    "current_status": payment.status.value,
                },
                error_id="PAYMENT_ALREADY_PROCESSED",
            )
        return True

    async def validate_payment_processing(self, payment_id: UUID) -> bool:
        """Valida que el pago se pueda procesar"""
        payment = await self.get_payment_by_id_or_raise(payment_id)
        
        if payment.status == PaymentStatus.paid:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "El pago ya está procesado",
                    "payment_id": str(payment_id),
                    "current_status": payment.status.value,
                },
                error_id="PAYMENT_ALREADY_PROCESSED",
            )
            
        if payment.status == PaymentStatus.cancelled:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "No se puede procesar un pago cancelado",
                    "payment_id": str(payment_id),
                    "current_status": payment.status.value,
                },
                error_id="PAYMENT_CANCELLED",
            )
        return True