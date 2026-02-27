import uuid

from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.repo = UserRepository(db)
        self.redis = redis

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise AppError(code=40101, message="用户名或密码错误")
        if not user.is_active:
            raise AppError(code=40102, message="用户已被停用")

        await self.repo.update_last_login(user)

        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id, user.role.value)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def logout(self, token: str) -> None:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            exp = payload.get("exp", 0)
            if jti:
                # Add to blacklist with TTL = remaining token lifetime
                import time

                ttl = max(int(exp - time.time()), 1)
                await self.redis.setex(f"token_blacklist:{jti}", ttl, "1")
        except JWTError:
            pass

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise AppError(code=40101, message="Refresh token 无效或已过期")

        if payload.get("type") != "refresh":
            raise AppError(code=40102, message="Token 类型错误")

        user_id = uuid.UUID(payload["sub"])
        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AppError(code=40102, message="用户不存在或已停用")

        new_access = create_access_token(user.id, user.role.value)
        new_refresh = create_refresh_token(user.id, user.role.value)

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)

    async def get_current_user(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    async def is_token_blacklisted(self, jti: str) -> bool:
        result = await self.redis.get(f"token_blacklist:{jti}")
        return result is not None
