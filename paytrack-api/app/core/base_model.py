from abc import ABC
from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field
from sqlalchemy import event
from sqlalchemy.orm import Session


class BasePayTrackModel(ABC, SQLModel):
    """
    Modelo base que proporciona campos de auditoría.
    No incluye 'id' para permitir que cada modelo defina su propia primary key.
    """
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data):
        super().__init__(**data)
        # Registrar el listener para updated_at solo una vez por clase
        if not hasattr(self.__class__, '_updated_at_listener_registered'):
            event.listen(self.__class__, 'before_update', self._update_timestamp)
            self.__class__._updated_at_listener_registered = True

    @staticmethod
    def _update_timestamp(mapper, connection, target):
        target.updated_at = datetime.now(timezone.utc)
