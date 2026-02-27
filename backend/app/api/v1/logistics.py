import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.logistics import (
    LogisticsCostCreate,
    LogisticsCostRead,
    LogisticsCostUpdate,
    LogisticsKanbanResponse,
    LogisticsRecordCreate,
    LogisticsRecordListParams,
    LogisticsRecordListRead,
    LogisticsRecordRead,
    LogisticsRecordUpdate,
    LogisticsStatusUpdate,
)
from app.services.logistics_service import LogisticsService

router = APIRouter(prefix="/logistics", tags=["物流管理"])


@router.get("", response_model=PaginatedResponse[LogisticsRecordListRead])
async def list_logistics_records(
    status_filter: str | None = Query(None, alias="status"),
    container_plan_id: uuid.UUID | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.LOGISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.enums import LogisticsStatus

    params = LogisticsRecordListParams(
        status=LogisticsStatus(status_filter) if status_filter else None,
        container_plan_id=container_plan_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = LogisticsService(db)
    data = await service.list_records(params)
    return PaginatedResponse(data=data)


@router.post(
    "",
    response_model=ApiResponse[LogisticsRecordRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_logistics_record(
    body: LogisticsRecordCreate,
    user: User = Depends(require_permission(Permission.LOGISTICS_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    record = await service.create(body, user.id)
    return ApiResponse(data=LogisticsRecordRead.model_validate(record))


@router.get("/kanban", response_model=ApiResponse[LogisticsKanbanResponse])
async def get_logistics_kanban(
    user: User = Depends(require_permission(Permission.LOGISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    data = await service.get_kanban()
    return ApiResponse(data=data)


@router.get("/{id}", response_model=ApiResponse[LogisticsRecordRead])
async def get_logistics_record(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.LOGISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    record = await service.get_by_id(id)
    return ApiResponse(data=LogisticsRecordRead.model_validate(record))


@router.put("/{id}", response_model=ApiResponse[LogisticsRecordRead])
async def update_logistics_record(
    id: uuid.UUID,
    body: LogisticsRecordUpdate,
    user: User = Depends(require_permission(Permission.LOGISTICS_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    record = await service.update(id, body, user.id)
    return ApiResponse(data=LogisticsRecordRead.model_validate(record))


@router.patch("/{id}/status", response_model=ApiResponse[LogisticsRecordRead])
async def update_logistics_status(
    id: uuid.UUID,
    body: LogisticsStatusUpdate,
    user: User = Depends(require_permission(Permission.LOGISTICS_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    record = await service.update_status(id, body.status, user.id)
    return ApiResponse(data=LogisticsRecordRead.model_validate(record))


@router.post(
    "/{id}/costs",
    response_model=ApiResponse[LogisticsCostRead],
    status_code=status.HTTP_201_CREATED,
)
async def add_logistics_cost(
    id: uuid.UUID,
    body: LogisticsCostCreate,
    user: User = Depends(require_permission(Permission.LOGISTICS_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    cost = await service.add_cost(id, body)
    return ApiResponse(data=LogisticsCostRead.model_validate(cost))


@router.put("/{id}/costs/{cost_id}", response_model=ApiResponse[LogisticsCostRead])
async def update_logistics_cost(
    id: uuid.UUID,
    cost_id: uuid.UUID,
    body: LogisticsCostUpdate,
    user: User = Depends(require_permission(Permission.LOGISTICS_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    cost = await service.update_cost(id, cost_id, body)
    return ApiResponse(data=LogisticsCostRead.model_validate(cost))


@router.delete("/{id}/costs/{cost_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logistics_cost(
    id: uuid.UUID,
    cost_id: uuid.UUID,
    user: User = Depends(require_permission(Permission.LOGISTICS_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = LogisticsService(db)
    await service.delete_cost(id, cost_id)
