

from pydantic import EmailStr
from sqlmodel import Session

from app.api.users.user_service import UserService
from app.constants.response_codes import PayTrackResponseCodes
from app.core.http_response import PayTrackHttpResponse


class UserController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_existing_user(self, user_email: EmailStr) -> bool:
        user_by_email = await UserService.get_user_by_email(
            email=user_email, session=self.session
        )
        if user_by_email:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": PayTrackResponseCodes.EXISTING_EMAIL.detail,
                    "providedValue": user_email,
                },
                error_id=PayTrackResponseCodes.EXISTING_EMAIL.code,
            )
        return True