from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from datetime import date, datetime, timezone
from app.models.daily_cutoff.daily_cutoff_model import DailyCutoffModel
from app.api.daily_cutoff.daily_cutoff_schema import (
    DailyCutoffCreate, 
    DailyCutoffUpdate
)


class DailyCutoffController:
    def __init__(self, db: Session):
        self.db = db

    def create_daily_cutoff(self, cutoff_data: DailyCutoffCreate) -> DailyCutoffModel:
        """Crear un nuevo corte diario"""
        cutoff = DailyCutoffModel(**cutoff_data.model_dump())
        self.db.add(cutoff)
        self.db.commit()
        self.db.refresh(cutoff)
        return cutoff

    def get_daily_cutoff_by_id(self, cutoff_id: UUID) -> Optional[DailyCutoffModel]:
        """Obtener corte diario por ID"""
        statement = select(DailyCutoffModel).where(
            DailyCutoffModel.cutoff_id == cutoff_id,
            DailyCutoffModel.deleted_at.is_(None)
        )
        return self.db.exec(statement).first()

    def get_daily_cutoffs(
        self, 
        skip: int = 0, 
        limit: int = 100,
        employee_id: Optional[UUID] = None,
        cutoff_date: Optional[date] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> tuple[List[DailyCutoffModel], int]:
        """Obtener lista de cortes diarios con filtros"""
        statement = select(DailyCutoffModel).where(
            DailyCutoffModel.deleted_at.is_(None)
        )
        
        if employee_id:
            statement = statement.where(DailyCutoffModel.employee_id == employee_id)
        if cutoff_date:
            statement = statement.where(DailyCutoffModel.cutoff_date == cutoff_date)
        if status:
            statement = statement.where(DailyCutoffModel.status == status)
        if date_from:
            statement = statement.where(DailyCutoffModel.cutoff_date >= date_from)
        if date_to:
            statement = statement.where(DailyCutoffModel.cutoff_date <= date_to)
            
        # Contar total
        count_statement = select(DailyCutoffModel).where(
            DailyCutoffModel.deleted_at.is_(None)
        )
        if employee_id:
            count_statement = count_statement.where(DailyCutoffModel.employee_id == employee_id)
        if cutoff_date:
            count_statement = count_statement.where(DailyCutoffModel.cutoff_date == cutoff_date)
        if status:
            count_statement = count_statement.where(DailyCutoffModel.status == status)
        if date_from:
            count_statement = count_statement.where(DailyCutoffModel.cutoff_date >= date_from)
        if date_to:
            count_statement = count_statement.where(DailyCutoffModel.cutoff_date <= date_to)
            
        total = len(self.db.exec(count_statement).all())
        
        # Obtener datos paginados ordenados por fecha descendente
        statement = statement.order_by(DailyCutoffModel.cutoff_date.desc()).offset(skip).limit(limit)
        cutoffs = self.db.exec(statement).all()
        
        return cutoffs, total

    def update_daily_cutoff(
        self, 
        cutoff_id: UUID, 
        cutoff_data: DailyCutoffUpdate
    ) -> Optional[DailyCutoffModel]:
        """Actualizar corte diario"""
        cutoff = self.get_daily_cutoff_by_id(cutoff_id)
        if not cutoff:
            return None
            
        update_data = cutoff_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cutoff, field, value)
            
        self.db.commit()
        self.db.refresh(cutoff)
        return cutoff

    def delete_daily_cutoff(self, cutoff_id: UUID) -> bool:
        """Eliminación lógica de corte diario"""
        cutoff = self.get_daily_cutoff_by_id(cutoff_id)
        if not cutoff:
            return False
            
        cutoff.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def get_cutoff_by_date_and_employee(
        self, 
        cutoff_date: date, 
        employee_id: UUID
    ) -> Optional[DailyCutoffModel]:
        """Obtener corte por fecha y empleado específico"""
        statement = select(DailyCutoffModel).where(
            DailyCutoffModel.cutoff_date == cutoff_date,
            DailyCutoffModel.employee_id == employee_id,
            DailyCutoffModel.deleted_at.is_(None)
        )
        return self.db.exec(statement).first()

    def get_cutoffs_by_employee(
        self, 
        employee_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[DailyCutoffModel]:
        """Obtener cortes de un empleado en un rango de fechas"""
        statement = select(DailyCutoffModel).where(
            DailyCutoffModel.employee_id == employee_id,
            DailyCutoffModel.deleted_at.is_(None)
        )
        
        if date_from:
            statement = statement.where(DailyCutoffModel.cutoff_date >= date_from)
        if date_to:
            statement = statement.where(DailyCutoffModel.cutoff_date <= date_to)
            
        statement = statement.order_by(DailyCutoffModel.cutoff_date.desc())
        return self.db.exec(statement).all()

    def approve_cutoff(self, cutoff_id: UUID) -> Optional[DailyCutoffModel]:
        """Aprobar un corte diario"""
        cutoff = self.get_daily_cutoff_by_id(cutoff_id)
        if not cutoff:
            return None
            
        cutoff.status = "approved"
        self.db.commit()
        self.db.refresh(cutoff)
        return cutoff

    def reject_cutoff(self, cutoff_id: UUID) -> Optional[DailyCutoffModel]:
        """Rechazar un corte diario"""
        cutoff = self.get_daily_cutoff_by_id(cutoff_id)
        if not cutoff:
            return None
            
        cutoff.status = "rejected"
        self.db.commit()
        self.db.refresh(cutoff)
        return cutoff