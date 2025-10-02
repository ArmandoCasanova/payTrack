from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic.alias_generators import to_camel

from app.core.mixins.password_validation_mixin import PasswordValidationMixin

from app.utils.regex import Regex


from uuid import UUID
class UserSchema(BaseModel):
    user_id: UUID
    rol: str
    name: str = Field(min_length=4, max_length=20, pattern=Regex.USER_NAME)
    last_name: str = Field(min_length=2, max_length=30)
    email: EmailStr = Field(max_length=40)
    birth_date: datetime | None = None
    points: float = 0.0
    is_verified: bool = False

    class Config:
        alias_generator = to_camel
        populate_by_name = True
        from_attributes = True


class UserCreateSchema(UserSchema, PasswordValidationMixin):
    password: str

    class Config:
        extra = "forbid"


class UserResponseSchema(UserSchema):
    created_at: datetime
    updated_at: datetime
