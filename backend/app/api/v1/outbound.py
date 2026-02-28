import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.outbound import (
    OutboundOrderConfirm,
    OutboundOrderCreate,
    OutboundOrderListParams,
    OutboundOrderListRead,
    OutboundOrderRead,
)
from app.services.outbound_service import OutboundService

router = APIRouter(prefix="/outbound-orders", tags=["出库管理"])


@router.get("", response_model=PaginatedResponse[OutboundOrderListRead])
async def list_outbound_orders(
    status_filter: str | None = Query(None, alias="status"),
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.OUTBOUND_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.enums import OutboundOrderStatus

    params = OutboundOrderListParams(
        status=OutboundOrderStatus(status_filter) if status_filter else None,
        keyword=keyword,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = OutboundService(db)
    data = await service.list_orders(params)
    return PaginatedResponse(data=data)


@router.get("/{id}", response_model=ApiResponse[OutboundOrderRead])
async def get_outbound_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.OUTBOUND_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = OutboundService(db)
    order = await service.get_by_id(id)
    return ApiResponse(data=OutboundOrderRead.model_validate(order))


@router.post(
    "",
    response_model=ApiResponse[OutboundOrderRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_outbound_order(
    body: OutboundOrderCreate,
    user: User = Depends(require_permission(Permission.OUTBOUND_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = OutboundService(db)
    order = await service.create_from_container_plan(body.container_plan_id, user.id)
    return ApiResponse(data=OutboundOrderRead.model_validate(order))


@router.post("/{id}/confirm", response_model=ApiResponse[OutboundOrderRead])
async def confirm_outbound_order(
    id: uuid.UUID,
    body: OutboundOrderConfirm,
    user: User = Depends(require_permission(Permission.OUTBOUND_CONFIRM)),
    db: AsyncSession = Depends(get_db),
):
    service = OutboundService(db)
    order = await service.confirm(id, body.outbound_date, body.operator, user.id)
    return ApiResponse(data=OutboundOrderRead.model_validate(order))


@router.post("/{id}/cancel", response_model=ApiResponse[OutboundOrderRead])
async def cancel_outbound_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.OUTBOUND_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = OutboundService(db)
    order = await service.cancel(id, user.id)
    return ApiResponse(data=OutboundOrderRead.model_validate(order))
