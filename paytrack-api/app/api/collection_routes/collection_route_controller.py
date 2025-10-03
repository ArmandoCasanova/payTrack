from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from app.models.collection_routes.collection_route_model import CollectionRouteModel
from app.api.collection_routes.collection_route_schema import (
    CollectionRouteCreate, 
    CollectionRouteUpdate
)


class CollectionRouteController:
    def __init__(self, db: Session):
        self.db = db

    def create_collection_route(self, collection_route_data: CollectionRouteCreate) -> CollectionRouteModel:
        """Crear una nueva ruta de cobranza"""
        collection_route = CollectionRouteModel(**collection_route_data.model_dump())
        self.db.add(collection_route)
        self.db.commit()
        self.db.refresh(collection_route)
        return collection_route

    def get_collection_route_by_id(self, route_id: UUID) -> Optional[CollectionRouteModel]:
        """Obtener ruta de cobranza por ID"""
        statement = select(CollectionRouteModel).where(
            CollectionRouteModel.route_id == route_id,
            CollectionRouteModel.deleted_at.is_(None)
        )
        return self.db.exec(statement).first()

    def get_collection_routes(
        self, 
        skip: int = 0, 
        limit: int = 100,
        employee_id: Optional[UUID] = None,
        loan_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> tuple[List[CollectionRouteModel], int]:
        """Obtener lista de rutas de cobranza con filtros"""
        statement = select(CollectionRouteModel).where(
            CollectionRouteModel.deleted_at.is_(None)
        )
        
        if employee_id:
            statement = statement.where(CollectionRouteModel.employee_id == employee_id)
        if loan_id:
            statement = statement.where(CollectionRouteModel.loan_id == loan_id)
        if status:
            statement = statement.where(CollectionRouteModel.status == status)
            
        # Contar total
        count_statement = select(CollectionRouteModel).where(
            CollectionRouteModel.deleted_at.is_(None)
        )
        if employee_id:
            count_statement = count_statement.where(CollectionRouteModel.employee_id == employee_id)
        if loan_id:
            count_statement = count_statement.where(CollectionRouteModel.loan_id == loan_id)
        if status:
            count_statement = count_statement.where(CollectionRouteModel.status == status)
            
        total = len(self.db.exec(count_statement).all())
        
        # Obtener datos paginados
        statement = statement.offset(skip).limit(limit)
        collection_routes = self.db.exec(statement).all()
        
        return collection_routes, total

    def update_collection_route(
        self, 
        route_id: UUID, 
        collection_route_data: CollectionRouteUpdate
    ) -> Optional[CollectionRouteModel]:
        """Actualizar ruta de cobranza"""
        collection_route = self.get_collection_route_by_id(route_id)
        if not collection_route:
            return None
            
        update_data = collection_route_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collection_route, field, value)
            
        self.db.commit()
        self.db.refresh(collection_route)
        return collection_route

    def delete_collection_route(self, route_id: UUID) -> bool:
        """Eliminación lógica de ruta de cobranza"""
        collection_route = self.get_collection_route_by_id(route_id)
        if not collection_route:
            return False
            
        from datetime import datetime, timezone
        collection_route.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def get_routes_by_employee(self, employee_id: UUID) -> List[CollectionRouteModel]:
        """Obtener rutas asignadas a un empleado"""
        statement = select(CollectionRouteModel).where(
            CollectionRouteModel.employee_id == employee_id,
            CollectionRouteModel.deleted_at.is_(None)
        )
        return self.db.exec(statement).all()