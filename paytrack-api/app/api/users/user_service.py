from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import Session, select
from sqlalchemy import or_, and_

from app.models.users.user_model import UserModel, UserStatus
from .user_schema import UserCreateSchema, UserUpdateSchema

from app.utils.security import get_password_hash
from app.core.http_response import PayTrackHttpResponse


class UserService:
    @staticmethod
    async def create_user(
        user_data: UserCreateSchema, session: Session
    ) -> UserModel:
        try:
            hashed_password = get_password_hash(user_data.password)

            user_dump = user_data.model_dump()

            new_user = UserModel(
                role=user_dump["role"],
                name=user_dump["name"],
                paternal_surname=user_dump["paternal_surname"],
                maternal_surname=user_dump["maternal_surname"],
                national_id=user_dump["national_id"],
                phone=user_dump["phone"],
                address=user_dump["address"],
                salary=user_dump.get("salary"),
                email=user_dump["email"],
                password=hashed_password,
                status=UserStatus.active,
                is_verified=False
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: Session) -> Optional[UserModel]:
        try:
            statement = select(UserModel).where(
                and_(
                    UserModel.user_id == user_id,
                    UserModel.deleted_at.is_(None)
                )
            )
            user = session.exec(statement).first()
            return user
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_users(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> tuple[List[UserModel], int]:
        try:
            query = select(UserModel).where(UserModel.deleted_at.is_(None))
            
            # Aplicar filtros
            if search:
                search_filter = or_(
                    UserModel.name.ilike(f"%{search}%"),
                    UserModel.paternal_surname.ilike(f"%{search}%"),
                    UserModel.maternal_surname.ilike(f"%{search}%"),
                    UserModel.national_id.ilike(f"%{search}%"),
                    UserModel.email.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if status:
                query = query.where(UserModel.status == status)
            
            # Contar total
            total_query = query
            total = len(session.exec(total_query).all())
            
            # Aplicar paginación
            query = query.offset(skip).limit(limit)
            users = session.exec(query).all()
            
            return users, total
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_user_by_email(email: str, session: Session) -> Optional[UserModel]:
        try:
            statement = select(UserModel).where(
                and_(
                    UserModel.email == email,
                    UserModel.deleted_at.is_(None)
                )
            )
            user = session.exec(statement).first()
            return user
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_user_by_national_id(national_id: str, session: Session) -> Optional[UserModel]:
        try:
            statement = select(UserModel).where(
                and_(
                    UserModel.national_id == national_id,
                    UserModel.deleted_at.is_(None)
                )
            )
            user = session.exec(statement).first()
            return user
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_user(
        user_id: UUID, 
        user_data: UserUpdateSchema, 
        session: Session
    ) -> Optional[UserModel]:
        try:
            user = await UserService.get_user_by_id(user_id, session)
            if not user:
                return None

            user_dump = user_data.model_dump(exclude_unset=True)
            
            for field, value in user_dump.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.now(timezone.utc)
            session.add(user)
            session.commit()
            session.refresh(user)
            
            return user
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def delete_user(user_id: UUID, session: Session) -> bool:
        try:
            user = await UserService.get_user_by_id(user_id, session)
            if not user:
                return False

            user.deleted_at = datetime.now(timezone.utc)
            session.add(user)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def verify_user(user_id: UUID, session: Session):
        try:
            user = await UserService.get_user_by_id(user_id, session)
            if user:
                user.is_verified = True
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def update_user_password(user_id: UUID, password: str, session: Session):
        try:
            hashed_password = get_password_hash(password)
            user = await UserService.get_user_by_id(user_id, session)
            if user:
                user.password = hashed_password
                user.updated_at = datetime.now(timezone.utc)
                session.add(user)
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
