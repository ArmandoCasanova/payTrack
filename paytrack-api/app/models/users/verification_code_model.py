from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.base_model import BasePayTrackModel
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .user_model import UserModel

class VerificationCodeModel(BasePayTrackModel, table=True):
    __tablename__ = "verification_codes"

    verification_code_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id")
    code: str
    is_alive: bool = Field(default=True)

    user: "UserModel" = Relationship(back_populates="verification_codes")
