import math
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.audit_log_repo import AuditLogRepository
from app.repositories.system_config_repo import SystemConfigRepository
from app.schemas.common import PaginatedData
from app.schemas.system import (
    AuditLogListParams,
    AuditLogRead,
    SystemConfigRead,
    SystemConfigUpdate,
    SystemUserCreate,
    SystemUserListParams,
    SystemUserRead,
    SystemUserUpdate,
)


class SystemService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditLogRepository(db)
        self.config_repo = SystemConfigRepository(db)

    # ==================== User Management ====================

    async def list_users(self, params: SystemUserListParams) -> PaginatedData[SystemUserRead]:
        query = select(User)
        count_query = select(func.count()).select_from(User)

        filters = []
        if params.keyword:
            filters.append(
                or_(
                    User.username.ilike(f"%{params.keyword}%"),
                    User.display_name.ilike(f"%{params.keyword}%"),
                    User.email.ilike(f"%{params.keyword}%"),
                )
            )
        if params.role:
            filters.append(User.role == params.role)
        if params.is_active is not None:
            filters.append(User.is_active == params.is_active)

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        order_col = getattr(User, params.sort_by, User.created_at)
        if params.sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())

        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return PaginatedData(
            items=[SystemUserRead.model_validate(u) for u in users],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    async def create_user(self, data: SystemUserCreate) -> User:
        # Check unique username
        result = await self.db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise BusinessError(code=42260, message=f"用户名 {data.username} 已存在")

        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            display_name=data.display_name,
            email=data.email,
            phone=data.phone,
            role=data.role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("用户", str(user_id))
        return user

    async def update_user(self, user_id: uuid.UUID, data: SystemUserUpdate) -> User:
        user = await self.get_user(user_id)
        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user_role(self, user_id: uuid.UUID, role: UserRole) -> User:
        user = await self.get_user(user_id)
        if user.role == UserRole.SUPER_ADMIN:
            raise BusinessError(code=42261, message="不能修改超级管理员的角色")
        user.role = role
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_user_status(self, user_id: uuid.UUID, is_active: bool) -> User:
        user = await self.get_user(user_id)
        if user.role == UserRole.SUPER_ADMIN and not is_active:
            raise BusinessError(code=42262, message="不能禁用超级管理员")
        user.is_active = is_active
        await self.db.flush()
        await self.db.refresh(user)
        return user

    # ==================== Audit Logs ====================

    async def list_audit_logs(self, params: AuditLogListParams) -> PaginatedData[AuditLogRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.audit_repo.search(
            user_id=params.user_id,
            action=params.action,
            resource_type=params.resource_type,
            date_from=params.date_from,
            date_to=params.date_to,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[AuditLogRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    # ==================== System Configs ====================

    async def list_configs(self) -> list[SystemConfigRead]:
        configs = await self.config_repo.get_all()
        return [SystemConfigRead.model_validate(c) for c in configs]

    async def update_config(
        self, key: str, data: SystemConfigUpdate, user_id: uuid.UUID
    ) -> SystemConfigRead:
        config = await self.config_repo.upsert(
            key=key,
            value=data.config_value,
            description=data.description,
            user_id=user_id,
        )
        return SystemConfigRead.model_validate(config)
