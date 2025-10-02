from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, Relationship, Column, Enum
from app.core.base_model import BasePayTrackModel
from datetime import datetime, date
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from .user_qr_code_model import UserQRCodeModel
    from .verification_code_model import VerificationCodeModel
    from .verification_code_password_reset_model import VerificationCodePasswordResetModel

class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    customer = "customer"

class UserModel(BasePayTrackModel, table=True):
    __tablename__ = "users"

    user_id: UUID = Field(default_factory=uuid4, primary_key=True)
    role: UserRole = Field(default=UserRole.customer, sa_column=Column(Enum(UserRole), nullable=False))
    name: str
    last_name: str
    birth_date: date
    email: str = Field(index=True, unique=True)
    password: str
    points: float = Field(default=0.0)
    is_verified: bool = Field(default=False)

    qr_codes: List["UserQRCodeModel"] = Relationship(back_populates="user")
    verification_codes: List["VerificationCodeModel"] = Relationship(back_populates="user")
    verification_codes_password_reset: List["VerificationCodePasswordResetModel"] = Relationship(back_populates="user")
