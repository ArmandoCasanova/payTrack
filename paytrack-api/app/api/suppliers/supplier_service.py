from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import Session, select
from sqlalchemy import or_, and_

from app.models.suppliers.supplier_model import SupplierModel, SupplierStatus, SupplierType
from .supplier_schema import SupplierCreateSchema, SupplierUpdateSchema

from app.core.http_response import PayTrackHttpResponse


class SupplierService:
    @staticmethod
    async def create_supplier(
        supplier_data: SupplierCreateSchema, session: Session
    ) -> SupplierModel:
        try:
            supplier_dump = supplier_data.model_dump()

            new_supplier = SupplierModel(
                name=supplier_dump["name"],
                phone=supplier_dump["phone"],
                contact=supplier_dump["contact"],
                description=supplier_dump.get("description"),
                folio=supplier_dump.get("folio"),
                address=supplier_dump["address"],
                supplier_type=supplier_dump["supplier_type"],
                status=SupplierStatus.active,
                email=supplier_dump.get("email"),
                website=supplier_dump.get("website"),
                tax_id=supplier_dump.get("tax_id")
            )

            session.add(new_supplier)
            session.commit()
            session.refresh(new_supplier)

            return new_supplier
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_supplier_by_id(supplier_id: UUID, session: Session) -> Optional[SupplierModel]:
        try:
            statement = select(SupplierModel).where(
                and_(
                    SupplierModel.supplier_id == supplier_id,
                    SupplierModel.deleted_at.is_(None)
                )
            )
            supplier = session.exec(statement).first()
            return supplier
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def get_suppliers(
        session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        supplier_type: Optional[SupplierType] = None,
        status: Optional[SupplierStatus] = None
    ) -> tuple[List[SupplierModel], int]:
        try:
            query = select(SupplierModel).where(SupplierModel.deleted_at.is_(None))
            
            # Aplicar filtros
            if search:
                search_filter = or_(
                    SupplierModel.name.ilike(f"%{search}%"),
                    SupplierModel.contact.ilike(f"%{search}%"),
                    SupplierModel.email.ilike(f"%{search}%"),
                    SupplierModel.folio.ilike(f"%{search}%"),
                    SupplierModel.tax_id.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if supplier_type:
                query = query.where(SupplierModel.supplier_type == supplier_type)
                
            if status:
                query = query.where(SupplierModel.status == status)
            
            # Contar total
            total_query = query
            total = len(session.exec(total_query).all())
            
            # Aplicar paginación
            query = query.offset(skip).limit(limit)
            suppliers = session.exec(query).all()
            
            return suppliers, total
        except Exception:
            raise PayTrackHttpResponse.internal_error()

    @staticmethod
    async def update_supplier(
        supplier_id: UUID, 
        supplier_data: SupplierUpdateSchema, 
        session: Session
    ) -> Optional[SupplierModel]:
        try:
            supplier = await SupplierService.get_supplier_by_id(supplier_id, session)
            if not supplier:
                return None

            supplier_dump = supplier_data.model_dump(exclude_unset=True)
            
            for field, value in supplier_dump.items():
                if hasattr(supplier, field):
                    setattr(supplier, field, value)
            
            supplier.updated_at = datetime.now(timezone.utc)
            session.add(supplier)
            session.commit()
            session.refresh(supplier)
            
            return supplier
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def delete_supplier(supplier_id: UUID, session: Session) -> bool:
        try:
            supplier = await SupplierService.get_supplier_by_id(supplier_id, session)
            if not supplier:
                return False

            supplier.deleted_at = datetime.now(timezone.utc)
            session.add(supplier)
            session.commit()
            
            return True
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    async def get_supplier_by_tax_id(tax_id: str, session: Session) -> Optional[SupplierModel]:
        try:
            statement = select(SupplierModel).where(
                and_(
                    SupplierModel.tax_id == tax_id,
                    SupplierModel.deleted_at.is_(None)
                )
            )
            supplier = session.exec(statement).first()
            return supplier
        except Exception:
            raise PayTrackHttpResponse.internal_error()