from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.database import get_db
from app.api.users.user_service import UserService
from app.api.users.user_controller import UserController
from app.api.users.user_schema import (
    UserCreateSchema, 
    UserUpdateSchema,
    UserResponseSchema, 
    UserListResponseSchema
)
from app.models.users.user_model import UserStatus
from app.core.http_response import PayTrackHttpResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=201)
async def create_user(
    user_data: UserCreateSchema,
    session: Session = Depends(get_db)
):
    """Crear un nuevo usuario"""
    try:
        print(f"🔍 DEBUG: Recibiendo datos: {user_data}")
        controller = UserController(session)
        
        print("🔍 DEBUG: Validando email...")
        # Validar que no exista un usuario con el mismo email
        await controller.validate_existing_user_email(user_data.email)
        
        print("🔍 DEBUG: Validando national_id...")
        # Validar que no exista un usuario con el mismo national_id
        await controller.validate_existing_user_national_id(user_data.national_id)
        
        print("🔍 DEBUG: Creando usuario...")
        # Crear el usuario
        new_user = await UserService.create_user(user_data, session)
        
        print("🔍 DEBUG: Usuario creado exitosamente")
        
        # Retornar directamente con FastAPI (maneja la serialización automáticamente)
        return new_user
    except Exception as e:
        print(f"❌ DEBUG ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/", response_model=UserListResponseSchema)
async def get_users(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a devolver"),
    search: Optional[str] = Query(None, description="Buscar por nombre, apellidos, identificación o email"),
    status: Optional[UserStatus] = Query(None, description="Filtrar por estado del usuario"),
    session: Session = Depends(get_db)
):
    """Obtener lista de usuarios con paginación y filtros"""
    try:
        users, total = await UserService.get_users(
            session=session,
            skip=skip,
            limit=limit,
            search=search,
            status=status
        )
        
        response_data = {
            "users": users,
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(users)
        }
        
        return response_data
    except Exception as e:
        raise e


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user_by_id(
    user_id: UUID,
    session: Session = Depends(get_db)
):
    """Obtener un usuario por su ID"""
    try:
        controller = UserController(session)
        user = await controller.get_user_by_id_or_raise(user_id)
        
        return user
    except Exception as e:
        raise e


@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateSchema,
    session: Session = Depends(get_db)
):
    """Actualizar un usuario"""
    try:
        controller = UserController(session)
        
        # Verificar que el usuario existe
        existing_user = await controller.get_user_by_id_or_raise(user_id)
        
        # Si se está actualizando el email, validar que no exista otro usuario con ese email
        if user_data.email and user_data.email != existing_user.email:
            await controller.validate_existing_user_email(user_data.email)
        
        # Si se está actualizando el national_id, validar que no exista otro usuario con ese ID
        if user_data.national_id and user_data.national_id != existing_user.national_id:
            await controller.validate_existing_user_national_id(user_data.national_id)
        
        # Actualizar el usuario
        updated_user = await UserService.update_user(user_id, user_data, session)
        
        return updated_user
    except Exception as e:
        raise e


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    session: Session = Depends(get_db)
):
    """Eliminar un usuario (soft delete)"""
    try:
        controller = UserController(session)
        
        # Verificar que el usuario existe
        await controller.get_user_by_id_or_raise(user_id)
        
        # Eliminar el usuario
        await UserService.delete_user(user_id, session)
        
        return None
    except Exception as e:
        raise e