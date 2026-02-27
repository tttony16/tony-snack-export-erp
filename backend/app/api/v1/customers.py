import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
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
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["客户管理"])


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


@router.get("/export", response_model=ApiResponse)
async def export_customers(
    user: User = Depends(require_super_admin),
):
    return ApiResponse(code=501, message="功能开发中")


@router.get("/{id}/orders", response_model=ApiResponse)
async def get_customer_orders(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CUSTOMER_VIEW)),
):
    return ApiResponse(code=501, message="功能开发中（Phase 2）")
