import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import ROLE_PERMISSIONS, Permission
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

security_scheme = HTTPBearer()


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 40101, "message": "Token 无效或已过期"},
        )

    # Check blacklist
    jti = payload.get("jti")
    if jti:
        blacklisted = await redis.get(f"token_blacklist:{jti}")
        if blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": 40101, "message": "Token 已失效"},
            )

    user_id = uuid.UUID(payload["sub"])
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 40102, "message": "用户不存在或已停用"},
        )

    return user


def require_permission(permission: Permission):
    """Permission check dependency factory."""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role.value, set())
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "无权限执行此操作"},
            )
        return current_user

    return checker


def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40390, "message": "仅超级管理员可操作"},
        )
    return current_user
