from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_db
from app.api.suppliers.supplier_service import SupplierService
from app.api.suppliers.supplier_controller import SupplierController
from app.api.suppliers.supplier_schema import (
    SupplierCreateSchema, 
    SupplierUpdateSchema,
    SupplierResponseSchema, 
    SupplierListResponseSchema
)
from app.models.suppliers.supplier_model import SupplierStatus, SupplierType
from app.core.http_response import PayTrackHttpResponse

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.post("/", response_model=SupplierResponseSchema, status_code=201)
async def create_supplier(
    supplier_data: SupplierCreateSchema,
    session: Session = Depends(get_db)
):
    """Crear un nuevo proveedor"""
    try:
        controller = SupplierController(session)
        
        # Validar que no exista un proveedor con el mismo tax_id si se proporciona
        if supplier_data.tax_id:
            await controller.validate_existing_supplier_tax_id(supplier_data.tax_id)
        
        # Crear el proveedor
        new_supplier = await SupplierService.create_supplier(supplier_data, session)
        
        return new_supplier
    except Exception as e:
        raise e


@router.get("/", response_model=SupplierListResponseSchema)
async def get_suppliers(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por nombre, contacto, email, folio o tax_id"),
    supplier_type: Optional[SupplierType] = Query(None, description="Filtrar por tipo de proveedor"),
    status: Optional[SupplierStatus] = Query(None, description="Filtrar por estado del proveedor"),
    session: Session = Depends(get_db)
):
    """Obtener lista de proveedores con paginación y filtros"""
    try:
        suppliers, total = await SupplierService.get_suppliers(
            session=session,
            skip=skip,
            limit=limit,
            search=search,
            supplier_type=supplier_type,
            status=status
        )
        
        response_data = {
            "suppliers": suppliers,
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(suppliers)
        }
        
        return response_data
    except Exception as e:
        raise e


@router.get("/{supplier_id}", response_model=SupplierResponseSchema)
async def get_supplier_by_id(
    supplier_id: UUID,
    session: Session = Depends(get_db)
):
    """Obtener un proveedor por su ID"""
    try:
        controller = SupplierController(session)
        supplier = await controller.get_supplier_by_id_or_raise(supplier_id)
        
        return supplier
    except Exception as e:
        raise e


@router.put("/{supplier_id}", response_model=SupplierResponseSchema)
async def update_supplier(
    supplier_id: UUID,
    supplier_data: SupplierUpdateSchema,
    session: Session = Depends(get_db)
):
    """Actualizar un proveedor"""
    try:
        controller = SupplierController(session)
        
        # Verificar que el proveedor existe
        existing_supplier = await controller.get_supplier_by_id_or_raise(supplier_id)
        
        # Si se está actualizando el tax_id, validar que no exista otro proveedor con ese ID
        if supplier_data.tax_id and supplier_data.tax_id != existing_supplier.tax_id:
            await controller.validate_existing_supplier_tax_id(supplier_data.tax_id)
        
        # Actualizar el proveedor
        updated_supplier = await SupplierService.update_supplier(supplier_id, supplier_data, session)
        
        return updated_supplier
    except Exception as e:
        raise e


@router.delete("/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: UUID,
    session: Session = Depends(get_db)
):
    """Eliminar un proveedor (soft delete)"""
    try:
        controller = SupplierController(session)
        
        # Verificar que el proveedor existe
        await controller.get_supplier_by_id_or_raise(supplier_id)
        
        # Eliminar el proveedor
        await SupplierService.delete_supplier(supplier_id, session)
        
        return None
    except Exception as e:
        raise e
