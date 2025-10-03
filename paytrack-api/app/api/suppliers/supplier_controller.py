from uuid import UUID
from typing import Optional

from sqlmodel import Session

from app.api.suppliers.supplier_service import SupplierService
from app.constants.response_codes import PayTrackResponseCodes
from app.core.http_response import PayTrackHttpResponse


class SupplierController:
    def __init__(self, session: Session):
        self.session = session

    async def validate_existing_supplier_tax_id(self, tax_id: str) -> bool:
        """Valida que no exista un proveedor con el mismo tax_id"""
        supplier_by_tax_id = await SupplierService.get_supplier_by_tax_id(
            tax_id=tax_id, session=self.session
        )
        if supplier_by_tax_id:
            raise PayTrackHttpResponse.forbidden(
                data={
                    "message": "Ya existe un proveedor con este ID fiscal",
                    "providedValue": tax_id,
                },
                error_id="SUPPLIER_TAX_ID_EXISTS",
            )
        return True

    async def get_supplier_by_id_or_raise(self, supplier_id: UUID):
        """Obtiene un proveedor por ID o lanza excepción si no existe"""
        supplier = await SupplierService.get_supplier_by_id(
            supplier_id=supplier_id, session=self.session
        )
        if not supplier:
            raise PayTrackHttpResponse.not_found(
                data={
                    "message": "Proveedor no encontrado",
                    "supplier_id": str(supplier_id),
                },
                error_id="SUPPLIER_NOT_FOUND",
            )
        return supplier