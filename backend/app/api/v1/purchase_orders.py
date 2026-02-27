import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.purchase_order import (
    LinkSalesOrdersRequest,
    PurchaseOrderCreate,
    PurchaseOrderListParams,
    PurchaseOrderListRead,
    PurchaseOrderRead,
    PurchaseOrderUpdate,
)
from app.schemas.warehouse import ReceivingNoteListParams, ReceivingNoteListRead
from app.services.purchase_order_service import PurchaseOrderService
from app.services.warehouse_service import WarehouseService

router = APIRouter(prefix="/purchase-orders", tags=["采购单"])


@router.get("", response_model=PaginatedResponse[PurchaseOrderListRead])
async def list_purchase_orders(
    keyword: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    supplier_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.enums import PurchaseOrderStatus

    params = PurchaseOrderListParams(
        keyword=keyword,
        status=PurchaseOrderStatus(status_filter) if status_filter else None,
        supplier_id=supplier_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = PurchaseOrderService(db)
    data = await service.list_orders(params)
    return PaginatedResponse(data=data)


@router.post("", response_model=ApiResponse[PurchaseOrderRead], status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    body: PurchaseOrderCreate,
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = PurchaseOrderService(db)
    order = await service.create(body, user.id)
    read = _build_po_read(order)
    return ApiResponse(data=read)


@router.get("/{id}", response_model=ApiResponse[PurchaseOrderRead])
async def get_purchase_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = PurchaseOrderService(db)
    order = await service.get_by_id(id)
    read = _build_po_read(order)
    return ApiResponse(data=read)


@router.put("/{id}", response_model=ApiResponse[PurchaseOrderRead])
async def update_purchase_order(
    id: uuid.UUID,
    body: PurchaseOrderUpdate,
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = PurchaseOrderService(db)
    order = await service.update(id, body, user.id)
    read = _build_po_read(order)
    return ApiResponse(data=read)


@router.post("/{id}/confirm", response_model=ApiResponse[PurchaseOrderRead])
async def confirm_purchase_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_CONFIRM)),
    db: AsyncSession = Depends(get_db),
):
    service = PurchaseOrderService(db)
    order = await service.confirm(id, user.id)
    read = _build_po_read(order)
    return ApiResponse(data=read)


@router.post("/{id}/cancel", response_model=ApiResponse[PurchaseOrderRead])
async def cancel_purchase_order(
    id: uuid.UUID,
    user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = PurchaseOrderService(db)
    order = await service.cancel(id, user.id)
    read = _build_po_read(order)
    return ApiResponse(data=read)


@router.post("/{id}/link-sales-orders", response_model=ApiResponse[PurchaseOrderRead])
async def link_sales_orders(
    id: uuid.UUID,
    body: LinkSalesOrdersRequest,
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = PurchaseOrderService(db)
    order = await service.link_sales_orders(id, body.sales_order_ids)
    read = _build_po_read(order)
    return ApiResponse(data=read)


@router.get("/{id}/receiving-notes", response_model=PaginatedResponse[ReceivingNoteListRead])
async def get_receiving_notes(
    id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    # Verify PO exists
    po_service = PurchaseOrderService(db)
    await po_service.get_by_id(id)

    wh_service = WarehouseService(db)
    params = ReceivingNoteListParams(
        purchase_order_id=id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await wh_service.list_receiving_notes(params)
    return PaginatedResponse(data=data)


def _build_po_read(order) -> PurchaseOrderRead:
    """Build PurchaseOrderRead with linked_sales_order_ids from relationship."""
    data = PurchaseOrderRead.model_validate(order)
    sos = order.sales_orders
    if sos is None:
        data.linked_sales_order_ids = []
    elif isinstance(sos, list):
        data.linked_sales_order_ids = [so.id for so in sos]
    else:
        data.linked_sales_order_ids = [sos.id]
    return data
