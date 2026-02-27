import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
from app.core.permissions import Permission
from app.database import get_db
from app.models.enums import AuditAction, UserRole
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.system import (
    AuditLogListParams,
    AuditLogRead,
    SystemConfigRead,
    SystemConfigUpdate,
    SystemUserCreate,
    SystemUserListParams,
    SystemUserRead,
    SystemUserUpdate,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.services.system_service import SystemService

router = APIRouter(prefix="/system", tags=["系统管理"])


@router.get("/users", response_model=PaginatedResponse[SystemUserRead])
async def list_users(
    keyword: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.USER_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    params = SystemUserListParams(
        keyword=keyword,
        role=role,
        is_active=is_active,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.list_users(params)
    return PaginatedResponse(data=data)


@router.post(
    "/users", response_model=ApiResponse[SystemUserRead], status_code=status.HTTP_201_CREATED
)
async def create_user(
    body: SystemUserCreate,
    user: User = Depends(require_permission(Permission.USER_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    new_user = await service.create_user(body)
    return ApiResponse(data=SystemUserRead.model_validate(new_user))


@router.get("/users/{id}", response_model=ApiResponse[SystemUserRead])
async def get_user(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.USER_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    target = await service.get_user(id)
    return ApiResponse(data=SystemUserRead.model_validate(target))


@router.put("/users/{id}", response_model=ApiResponse[SystemUserRead])
async def update_user(
    id: uuid.UUID,
    body: SystemUserUpdate,
    user: User = Depends(require_permission(Permission.USER_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    updated = await service.update_user(id, body)
    return ApiResponse(data=SystemUserRead.model_validate(updated))


@router.patch("/users/{id}/role", response_model=ApiResponse[SystemUserRead])
async def update_user_role(
    id: uuid.UUID,
    body: UserRoleUpdate,
    user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    updated = await service.update_user_role(id, body.role)
    return ApiResponse(data=SystemUserRead.model_validate(updated))


@router.patch("/users/{id}/status", response_model=ApiResponse[SystemUserRead])
async def update_user_status(
    id: uuid.UUID,
    body: UserStatusUpdate,
    user: User = Depends(require_permission(Permission.USER_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    updated = await service.update_user_status(id, body.is_active)
    return ApiResponse(data=SystemUserRead.model_validate(updated))


@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogRead])
async def list_audit_logs(
    user_id: uuid.UUID | None = None,
    action: AuditAction | None = None,
    resource_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.AUDIT_LOG_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    params = AuditLogListParams(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.list_audit_logs(params)
    return PaginatedResponse(data=data)


@router.get("/configs", response_model=ApiResponse[list[SystemConfigRead]])
async def list_configs(
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    data = await service.list_configs()
    return ApiResponse(data=data)


@router.put("/configs/{key}", response_model=ApiResponse[SystemConfigRead])
async def update_config(
    key: str,
    body: SystemConfigUpdate,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    db: AsyncSession = Depends(get_db),
):
    service = SystemService(db)
    data = await service.update_config(key, body, user.id)
    return ApiResponse(data=data)
