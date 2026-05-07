from fastapi import APIRouter, HTTPException, status

from app.core.security import verify_password, create_access_token
from app.core.config import get_settings
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    if (
        data.username != settings.admin_username
        or not verify_password(data.password, settings.admin_password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    access_token = create_access_token(data={"sub": data.username})
    return TokenResponse(access_token=access_token)