from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.users.user_model import UserModel
from .user_schema import UserCreateSchema

from app.constants.user_constants import UserRoles
from app.utils.security import get_password_hash
from app.core.http_response import PayTrackHttpResponse


class UserService:
    @staticmethod
    async def create_user(
        user_data: UserCreateSchema, role: str, session: Session
    ) -> UserModel:
        try:
            hashed_password = get_password_hash(user_data.password)

            user_dump = user_data.model_dump()

            new_user = UserModel(
                role=role,
                name=user_dump["name"],
                last_name=user_dump["last_name"],
                birth_date=user_dump.get("birth_date"),
                email=user_dump["email"],
                password=hashed_password,
                points=user_dump.get("points", 0.0),
                is_verified=user_dump.get("is_verified", False)
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user
        except Exception as e:
            raise e

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: Session) -> UserModel:
        try:
            statement = select(UserModel).where(UserModel.user_id == user_id)
            user = session.exec(statement).first()
            return user
        except Exception:
            PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_user_by_email(email: str, session: Session) -> UserModel | bool:
        try:
            statement = select(UserModel).where(UserModel.email == email)
            user = session.exec(statement).first()
            return user if user else False
        except Exception as e:
            PayTrackHttpResponse.internal_error()

    @staticmethod
    async def verify_user(user_id: UUID, session: Session):
        try:
            statement = select(UserModel).where(UserModel.user_id == user_id)
            user = session.exec(statement).first()
            if user:
                user.is_verified = True
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
        except Exception:
            PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_user_password(user_id: UUID, password: str, session: Session):
        try:
            hashed_password = get_password_hash(password)
            statement = select(UserModel).where(UserModel.user_id == user_id)
            user = session.exec(statement).first()
            if user:
                user.password = hashed_password
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
        except Exception:
            PayTrackHttpResponse.internal_error()
