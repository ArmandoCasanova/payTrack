

from uuid import UUID
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Session

from app.api.users.user_service import UserService
from app.core.http_response import PayTrackHttpResponse


class UserController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_existing_user_email(self, user_email: EmailStr) -> bool:
        user_by_email = await UserService.get_user_by_email(
            email=user_email, session=self.session
        )
        if user_by_email:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Ya existe un usuario con este email",
                    "providedValue": user_email,
                },
                error_id="USER_EMAIL_EXISTS",
            )
        return True

    async def validate_existing_user_national_id(self, national_id: str) -> bool:
        user_by_national_id = await UserService.get_user_by_national_id(
            national_id=national_id, session=self.session
        )
        if user_by_national_id:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Ya existe un usuario con este número de identificación",
                    "providedValue": national_id,
                },
                error_id="USER_NATIONAL_ID_EXISTS",
            )
        return True

    async def get_user_by_id_or_raise(self, user_id: UUID):
        """Obtiene un usuario por ID o lanza excepción si no existe"""
        user = await UserService.get_user_by_id(
            user_id=user_id, session=self.session
        )
        if not user:
            raise PayTrackHttpResponse.not_found(
                data={
                    "message": "Usuario no encontrado",
                    "user_id": str(user_id),
                },
                error_id="USER_NOT_FOUND",
            )
        return user