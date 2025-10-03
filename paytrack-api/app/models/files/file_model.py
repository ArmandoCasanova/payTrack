from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship
from app.core.base_model import BasePayTrackModel
from datetime import datetime
from uuid import UUID, uuid4
import enum

if TYPE_CHECKING:
    from app.models.clients.client_model import ClientModel
    from app.models.users.user_model import UserModel

class FileType(str, enum.Enum):
    identification = "identification"  # INE, identificación
    income_proof = "income_proof"  # Comprobante de ingresos
    address_proof = "address_proof"  # Comprobante de domicilio
    contract = "contract"  # Contrato
    payment_receipt = "payment_receipt"  # Comprobante de pago
    other = "other"  # Otros

class FileModel(BasePayTrackModel, table=True):
    __tablename__ = "files"

    file_id: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Relación con cliente
    client_id: UUID = Field(foreign_key="clients.client_id", description="ID del cliente")
    
    # Información del archivo
    file_name: str = Field(description="Nombre original del archivo")
    file_path: str = Field(description="Ruta donde se almacena el archivo")
    file_type: FileType = Field(default=FileType.other, description="Tipo de archivo")
    file_size: Optional[int] = Field(default=None, description="Tamaño del archivo en bytes")
    mime_type: Optional[str] = Field(default=None, description="Tipo MIME del archivo")
    
    # Metadata
    description: Optional[str] = Field(default=None, description="Descripción del archivo")
    uploaded_by: Optional[UUID] = Field(default=None, foreign_key="users.user_id", description="Usuario que subió el archivo")
    
    # Soft delete

    # Relaciones
    client: "ClientModel" = Relationship(back_populates="files")
    # uploader: Optional["UserModel"] = Relationship(back_populates="uploaded_files")
    
    @property
    def is_image(self) -> bool:
        """Verifica si el archivo es una imagen"""
        if self.mime_type:
            return self.mime_type.startswith('image/')
        return False
    
    @property
    def is_pdf(self) -> bool:
        """Verifica si el archivo es un PDF"""
        return self.mime_type == 'application/pdf'
    
    @property
    def file_extension(self) -> str:
        """Obtiene la extensión del archivo"""
        return self.file_name.split('.')[-1].lower() if '.' in self.file_name else ''