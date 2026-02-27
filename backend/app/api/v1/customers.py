import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.customer import (
    CustomerCreate,
    CustomerListParams,
    CustomerRead,
    CustomerUpdate,
)
from app.schemas.sales_order import SalesOrderListParams, SalesOrderListRead
from app.services.customer_service import CustomerService
from app.services.sales_order_service import SalesOrderService
from app.utils.excel import create_workbook

router = APIRouter(prefix="/customers", tags=["客户管理"])

CUSTOMER_EXPORT_HEADERS = [
    "客户编码",
    "客户名称",
    "国家",
    "联系人",
    "联系电话",
    "邮箱",
    "币种",
    "付款方式",
]


@router.get("", response_model=PaginatedResponse[CustomerRead])
async def list_customers(
    keyword: str | None = None,
    country: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.CUSTOMER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    params = CustomerListParams(
        keyword=keyword,
        country=country,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.list_customers(params)
    return PaginatedResponse(data=data)


@router.post("", response_model=ApiResponse[CustomerRead], status_code=status.HTTP_201_CREATED)
async def create_customer(
    body: CustomerCreate,
    user: User = Depends(require_permission(Permission.CUSTOMER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customer = await service.create(body, user.id)
    return ApiResponse(data=CustomerRead.model_validate(customer))


@router.get("/export")
async def export_customers(
    user: User = Depends(require_permission(Permission.CUSTOMER_EXPORT)),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    params = CustomerListParams(page=1, page_size=100)
    data = await service.list_customers(params)
    rows = []
    for c in data.items:
        rows.append(
            [
                c.customer_code,
                c.name,
                c.country,
                c.contact_person,
                c.phone or "",
                c.email or "",
                c.currency.value if hasattr(c.currency, "value") else str(c.currency),
                (
                    c.payment_method.value
                    if hasattr(c.payment_method, "value")
                    else str(c.payment_method)
                ),
            ]
        )
    output = create_workbook("客户列表", CUSTOMER_EXPORT_HEADERS, rows)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=customers.xlsx"},
    )


@router.get("/{id}", response_model=ApiResponse[CustomerRead])
async def get_customer(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CUSTOMER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customer = await service.get_by_id(id)
    return ApiResponse(data=CustomerRead.model_validate(customer))


@router.put("/{id}", response_model=ApiResponse[CustomerRead])
async def update_customer(
    id: uuid.UUID,
    body: CustomerUpdate,
    user: User = Depends(require_permission(Permission.CUSTOMER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    customer = await service.update(id, body, user.id)
    return ApiResponse(data=CustomerRead.model_validate(customer))


@router.get("/{id}/orders", response_model=PaginatedResponse[SalesOrderListRead])
async def get_customer_orders(
    id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.CUSTOMER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    # Verify customer exists
    customer_service = CustomerService(db)
    await customer_service.get_by_id(id)

    so_service = SalesOrderService(db)
    params = SalesOrderListParams(
        customer_id=id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await so_service.list_orders(params)
    return PaginatedResponse(data=data)
