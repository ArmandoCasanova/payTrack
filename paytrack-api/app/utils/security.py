import jwt
import time
import logging
from uuid import UUID
from datetime import datetime, timezone, timedelta

from typing import Optional
from passlib.context import CryptContext

from app.core.settings import settings

from app.models.users.user_model import UserModel, UserRole

ACCESS_TOKEN_EXPIRY = 3600

password_context = CryptContext(schemes=["bcrypt"])


def get_password_hash(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(
    user_data: dict, expires_delta: timedelta = None, refresh_token: bool = False
) -> str:
    payload = {
        "sub": user_data["id"],
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data["role"],
        },
        "exp": datetime.now(timezone.utc) + (
            expires_delta if expires_delta is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
        ),
        "iat": int(time.time()),
        "refresh": refresh_token,
    }
    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token


def decode_token(token: str) -> Optional[dict]:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return token_data

    except jwt.PyJWTError as e:
        logging.error(e)
        return None


def get_user_token(
    user: UserModel,
    is_refresh: bool = False,
) -> str:
    # Validar que el rol del usuario esté en UserRole
    if user.role not in [role.value for role in UserRole]:
        raise ValueError(f"Invalid user role: {user.role}")
    user_data = {
        "id": str(user.user_id),
        "email": user.email,
        "name": user.full_name,  # Usar la propiedad full_name del modelo
        "role": user.role.value,  # Convertir enum a string
    }
    return create_access_token(
        user_data=user_data,
        expires_delta=timedelta(days=2) if is_refresh else timedelta(hours=1),
        refresh_token=is_refresh,
    )
