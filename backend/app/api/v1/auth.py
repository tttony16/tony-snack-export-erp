from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import LoginRequest, RefreshRequest, TokenResponse, UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])
security_scheme = HTTPBearer()


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    service = AuthService(db, redis)
    token = await service.login(body.username, body.password)
    return ApiResponse(data=token)


@router.post("/logout", response_model=ApiResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    service = AuthService(db, redis)
    await service.logout(credentials.credentials)
    return ApiResponse(message="已登出")


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    service = AuthService(db, redis)
    token = await service.refresh(body.refresh_token)
    return ApiResponse(data=token)


@router.get("/me", response_model=ApiResponse[UserRead])
async def me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserRead.model_validate(current_user))
