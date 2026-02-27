import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.sales_order import (
    KanbanResponse,
    SalesOrderCreate,
    SalesOrderListParams,
    SalesOrderListRead,
    SalesOrderRead,
    SalesOrderStatusUpdate,
    SalesOrderUpdate,
)
from app.services.sales_order_service import SalesOrderService
from app.utils.excel import create_workbook

router = APIRouter(prefix="/sales-orders", tags=["销售订单"])

SO_EXPORT_HEADERS = [
    "订单号",
    "客户ID",
    "订单日期",
    "目的港",
    "贸易条款",
    "币种",
    "状态",
    "总金额",
    "总数量",
]


@router.get("", response_model=PaginatedResponse[SalesOrderListRead])
async def list_sales_orders(
    keyword: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    customer_id: uuid.UUID | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.enums import SalesOrderStatus

    params = SalesOrderListParams(
        keyword=keyword,
        status=SalesOrderStatus(status_filter) if status_filter else None,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = SalesOrderService(db)
    data = await service.list_orders(params)
    return PaginatedResponse(data=data)


@router.post("", response_model=ApiResponse[SalesOrderRead], status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    body: SalesOrderCreate,
    user: User = Depends(require_permission(Permission.SALES_ORDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    order = await service.create(body, user.id)
    return ApiResponse(data=SalesOrderRead.model_validate(order))


@router.get("/export")
async def export_sales_orders(
    user: User = Depends(require_permission(Permission.SALES_ORDER_EXPORT)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    params = SalesOrderListParams(page=1, page_size=100)
    data = await service.list_orders(params)
    rows = []
    for o in data.items:
        rows.append(
            [
                o.order_no,
                str(o.customer_id),
                str(o.order_date),
                o.destination_port,
                o.trade_term.value if hasattr(o.trade_term, "value") else str(o.trade_term),
                o.currency.value if hasattr(o.currency, "value") else str(o.currency),
                o.status.value if hasattr(o.status, "value") else str(o.status),
                str(o.total_amount),
                o.total_quantity,
            ]
        )
    output = create_workbook("销售订单", SO_EXPORT_HEADERS, rows)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sales_orders.xlsx"},
    )


@router.get("/kanban", response_model=ApiResponse[KanbanResponse])
async def get_kanban(
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    data = await service.get_kanban()
    return ApiResponse(data=data)


@router.get("/{id}", response_model=ApiResponse[SalesOrderRead])
async def get_sales_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    order = await service.get_by_id(id)
    return ApiResponse(data=SalesOrderRead.model_validate(order))


@router.put("/{id}", response_model=ApiResponse[SalesOrderRead])
async def update_sales_order(
    id: uuid.UUID,
    body: SalesOrderUpdate,
    user: User = Depends(require_permission(Permission.SALES_ORDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    order = await service.update(id, body, user.id)
    return ApiResponse(data=SalesOrderRead.model_validate(order))


@router.post("/{id}/confirm", response_model=ApiResponse[SalesOrderRead])
async def confirm_sales_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SALES_ORDER_CONFIRM)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    order = await service.confirm(id, user.id)
    return ApiResponse(data=SalesOrderRead.model_validate(order))


@router.post("/{id}/generate-purchase", response_model=ApiResponse)
async def generate_purchase_order(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PURCHASE_ORDER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    result = await service.generate_purchase_orders(id, user.id)
    return ApiResponse(data=result)


@router.get("/{id}/fulfillment", response_model=ApiResponse)
async def get_fulfillment(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    data = await service.get_fulfillment(id)
    return ApiResponse(data=data)


@router.patch("/{id}/status", response_model=ApiResponse[SalesOrderRead])
async def update_status(
    id: uuid.UUID,
    body: SalesOrderStatusUpdate,
    user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SalesOrderService(db)
    order = await service.update_status(id, body.status, user.id)
    return ApiResponse(data=SalesOrderRead.model_validate(order))
