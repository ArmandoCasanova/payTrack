from uuid import UUID
from typing import Optional

from sqlmodel import Session

from app.api.clients.client_service import ClientService
from app.constants.response_codes import PayTrackResponseCodes
from app.core.http_response import PayTrackHttpResponse
from app.models.clients.client_model import ClientStatus


class ClientController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_existing_client_national_id(self, national_id: str) -> bool:
        """Valida que no exista un cliente con el mismo national_id"""
        client_by_national_id = await ClientService.get_client_by_national_id(
            national_id=national_id, session=self.session
        )
        if client_by_national_id:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Ya existe un cliente con este número de identificación",
                    "providedValue": national_id,
                },
                error_id="CLIENT_NATIONAL_ID_EXISTS",
            )
        return True

    async def get_client_by_id_or_raise(self, client_id: UUID):
        """Obtiene un cliente por ID o lanza excepción si no existe"""
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
        return client

    async def validate_client_status_change(self, current_status: ClientStatus, new_status: ClientStatus) -> bool:
        """Valida que el cambio de estado del cliente sea válido"""
        # Aquí puedes agregar lógica de negocio para validar cambios de estado
        # Por ejemplo, no permitir cambiar de bad_debtor a pays_on_time directamente
        if current_status == ClientStatus.bad_debtor and new_status == ClientStatus.pays_on_time:
            raise PayTrackHttpResponse.bad_request(
                data={
                    "message": "No se puede cambiar directamente de mal adeudor a paga a tiempo",
                    "current_status": current_status.value,
                    "requested_status": new_status.value,
                },
                error_id="INVALID_STATUS_CHANGE",
            )
        return True