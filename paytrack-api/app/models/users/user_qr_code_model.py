from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.base_model import BasePayTrackModel
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .user_model import UserModel

class UserQRCodeModel(BasePayTrackModel, table=True):
    __tablename__ = "user_qr_codes"

    qr_code_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.user_id")
    qr_code_string: str
    is_alive: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: "UserModel" = Relationship(back_populates="qr_codes")
