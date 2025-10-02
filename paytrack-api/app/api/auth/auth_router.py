from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.database import get_db
from app.api.auth.auth_controller import AuthController
from app.api.auth.auth_schema import SignupSchema, AuthResponseSchema, LoginSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=AuthResponseSchema)
async def signup(
    data: SignupSchema,
    session: Session = Depends(get_db)
):
    """Registrar un nuevo usuario"""
    try:
        controller = AuthController(session)
        return await controller.signup(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signin", response_model=AuthResponseSchema) 
async def signin(
    data: LoginSchema,
    session: Session = Depends(get_db)
):
    """Iniciar sesión"""
    try:
        controller = AuthController(session)
        user = await controller.get_current_user_from_login(data.email)
        controller.verify_user_password(user, data.password)
        await controller.is_user_verified(user)
        return await controller.login(user, data.password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
