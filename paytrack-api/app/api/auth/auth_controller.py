from datetime import datetime, timezone
from uuid import uuid4
from sqlmodel import Session
from fastapi import HTTPException

from app.constants.user_constants import UserRoles
from app.models.users.user_model import UserModel
from app.api.users.user_service import UserService
from app.api.auth.auth_schema import SignupSchema, AuthResponseSchema
from app.utils.security import get_user_token, verify_password

class AuthController:
    def __init__(self, session: Session):
        self.session = session

    async def signup(self, data: SignupSchema) -> AuthResponseSchema:
        try:
            # Verificar si el usuario ya existe
            existing_user = await UserService.get_user_by_email(data.email, self.session)
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="User with this email already exists"
                )
            
            # Crear nuevo usuario - user_id se genera automáticamente
            user = await UserService.create_user(
                user_data=data,
                role=UserRoles.CUSTOMER.value,
                session=self.session
            )
            
            # Generar tokens
            access_token = get_user_token(user, is_refresh=False)
            refresh_token = get_user_token(user, is_refresh=True)
            
            return AuthResponseSchema(
                user_id=user.user_id,
                email=user.email,
                name=user.name,
                last_name=user.last_name,
                role=user.role,
                access_token=access_token,
                refresh_token=refresh_token,
                is_verified=user.is_verified
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_current_user_from_login(self, email: str) -> UserModel:
        try:
            user = await UserService.get_user_by_email(
                email=email, session=self.session
            )
            if user is False:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def verify_user_password(self, user: UserModel, password: str) -> bool:
        is_valid_password = verify_password(
            plain_password=password, hashed_password=user.password
        )
        if not is_valid_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return True

    async def is_user_verified(self, user: UserModel):
        if not user.is_verified:
            raise HTTPException(
                status_code=403, 
                detail="User is not verified"
            )

    async def login(self, user: UserModel, password: str) -> AuthResponseSchema:
        try:
            access_token = get_user_token(user, is_refresh=False)
            refresh_token = get_user_token(user, is_refresh=True)
            
            return AuthResponseSchema(
                user_id=user.user_id,
                email=user.email,
                name=user.name,
                last_name=user.last_name,
                role=user.role,
                access_token=access_token,
                refresh_token=refresh_token,
                is_verified=user.is_verified
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
