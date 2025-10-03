from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import Session, select
from sqlalchemy import or_, and_

from app.models.clients.client_model import ClientModel, ClientStatus
from .client_schema import ClientCreateSchema, ClientUpdateSchema

from app.core.http_response import PayTrackHttpResponse


class ClientService:
    @staticmethod
    async def create_client(
        client_data: ClientCreateSchema, session: Session
    ) -> ClientModel:
        try:
            client_dump = client_data.model_dump()

            new_client = ClientModel(
                name=client_dump["name"],
                paternal_surname=client_dump["paternal_surname"],
                maternal_surname=client_dump["maternal_surname"],
                occupation=client_dump["occupation"],
                national_id=client_dump["national_id"],
                address=client_dump["address"],
                phone=client_dump["phone"],
                birth_date=client_dump["birth_date"],
                status=ClientStatus.active,
                notes=client_dump.get("notes")
            )

            session.add(new_client)
            session.commit()
            session.refresh(new_client)

            return new_client
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_client_by_id(client_id: UUID, session: Session) -> Optional[ClientModel]:
        try:
            statement = select(ClientModel).where(
                and_(
                    ClientModel.client_id == client_id,
                    ClientModel.deleted_at.is_(None)
                )
            )
            client = session.exec(statement).first()
            return client
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_clients(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[ClientStatus] = None
    ) -> tuple[List[ClientModel], int]:
        try:
            query = select(ClientModel).where(ClientModel.deleted_at.is_(None))
            
            # Aplicar filtros
            if search:
                search_filter = or_(
                    ClientModel.name.ilike(f"%{search}%"),
                    ClientModel.paternal_surname.ilike(f"%{search}%"),
                    ClientModel.maternal_surname.ilike(f"%{search}%"),
                    ClientModel.national_id.ilike(f"%{search}%"),
                    ClientModel.phone.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if status:
                query = query.where(ClientModel.status == status)
            
            # Contar total
            total_query = query
            total = len(session.exec(total_query).all())
            
            # Aplicar paginación
            query = query.offset(skip).limit(limit)
            clients = session.exec(query).all()
            
            return clients, total
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_client(
        client_id: UUID, 
        client_data: ClientUpdateSchema, 
        session: Session
    ) -> Optional[ClientModel]:
        try:
            client = await ClientService.get_client_by_id(client_id, session)
            if not client:
                return None

            client_dump = client_data.model_dump(exclude_unset=True)
            
            for field, value in client_dump.items():
                if hasattr(client, field):
                    setattr(client, field, value)
            
            client.updated_at = datetime.now(timezone.utc)
            session.add(client)
            session.commit()
            session.refresh(client)
            
            return client
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def delete_client(client_id: UUID, session: Session) -> bool:
        try:
            client = await ClientService.get_client_by_id(client_id, session)
            if not client:
                return False

            client.deleted_at = datetime.now(timezone.utc)
            session.add(client)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_client_by_national_id(national_id: str, session: Session) -> Optional[ClientModel]:
        try:
            statement = select(ClientModel).where(
                and_(
                    ClientModel.national_id == national_id,
                    ClientModel.deleted_at.is_(None)
                )
            )
            client = session.exec(statement).first()
            return client
        except Exception:
            raise PayTrackHttpResponse.internal_error()