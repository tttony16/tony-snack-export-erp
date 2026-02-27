import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.warehouse import (
    InventoryByOrderRead,
    InventoryByProductRead,
    InventoryListParams,
    ReadinessCheckResponse,
    ReceivingNoteCreate,
    ReceivingNoteListParams,
    ReceivingNoteListRead,
    ReceivingNoteRead,
    ReceivingNoteUpdate,
)
from app.services.warehouse_service import WarehouseService

router = APIRouter(prefix="/warehouse", tags=["仓储管理"])


# ==================== Receiving Notes ====================


@router.get("/receiving-notes", response_model=PaginatedResponse[ReceivingNoteListRead])
async def list_receiving_notes(
    purchase_order_id: uuid.UUID | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.WAREHOUSE_OPERATE)),
    db: AsyncSession = Depends(get_db),
):
    params = ReceivingNoteListParams(
        purchase_order_id=purchase_order_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = WarehouseService(db)
    data = await service.list_receiving_notes(params)
    return PaginatedResponse(data=data)


@router.post(
    "/receiving-notes",
    response_model=ApiResponse[ReceivingNoteRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_receiving_note(
    body: ReceivingNoteCreate,
    user: User = Depends(require_permission(Permission.WAREHOUSE_OPERATE)),
    db: AsyncSession = Depends(get_db),
):
    service = WarehouseService(db)
    note = await service.create_receiving_note(body, user.id)
    return ApiResponse(data=ReceivingNoteRead.model_validate(note))


@router.get("/receiving-notes/{id}", response_model=ApiResponse[ReceivingNoteRead])
async def get_receiving_note(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.WAREHOUSE_OPERATE)),
    db: AsyncSession = Depends(get_db),
):
    service = WarehouseService(db)
    note = await service.get_receiving_note(id)
    return ApiResponse(data=ReceivingNoteRead.model_validate(note))


@router.put("/receiving-notes/{id}", response_model=ApiResponse[ReceivingNoteRead])
async def update_receiving_note(
    id: uuid.UUID,
    body: ReceivingNoteUpdate,
    user: User = Depends(require_permission(Permission.WAREHOUSE_OPERATE)),
    db: AsyncSession = Depends(get_db),
):
    service = WarehouseService(db)
    note = await service.update_receiving_note(id, body, user.id)
    return ApiResponse(data=ReceivingNoteRead.model_validate(note))


# ==================== Inventory ====================


@router.get("/inventory", response_model=PaginatedResponse[InventoryByProductRead])
async def get_inventory(
    product_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.INVENTORY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    params = InventoryListParams(
        product_id=product_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = WarehouseService(db)
    data = await service.get_inventory_by_product(params)
    return PaginatedResponse(data=data)


@router.get("/inventory/by-order", response_model=ApiResponse[list[InventoryByOrderRead]])
async def get_inventory_by_order(
    sales_order_id: uuid.UUID = Query(...),
    user: User = Depends(require_permission(Permission.INVENTORY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = WarehouseService(db)
    data = await service.get_inventory_by_order(sales_order_id)
    return ApiResponse(data=data)


@router.get(
    "/inventory/readiness/{sales_order_id}",
    response_model=ApiResponse[ReadinessCheckResponse],
)
async def check_readiness(
    sales_order_id: uuid.UUID,
    user: User = Depends(require_permission(Permission.INVENTORY_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = WarehouseService(db)
    data = await service.check_readiness(sales_order_id)
    return ApiResponse(data=data)


@router.get("/inventory/export", response_model=ApiResponse)
async def export_inventory(
    user: User = Depends(require_super_admin),
):
    return ApiResponse(code=501, message="功能开发中")
