import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.supplier import (
    SupplierCreate,
    SupplierListParams,
    SupplierProductCreate,
    SupplierProductRead,
    SupplierRead,
    SupplierUpdate,
)
from app.services.supplier_service import SupplierService

router = APIRouter(prefix="/suppliers", tags=["供应商管理"])


@router.get("", response_model=PaginatedResponse[SupplierRead])
async def list_suppliers(
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.SUPPLIER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    params = SupplierListParams(
        keyword=keyword,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.list_suppliers(params)
    return PaginatedResponse(data=data)


@router.post("", response_model=ApiResponse[SupplierRead], status_code=status.HTTP_201_CREATED)
async def create_supplier(
    body: SupplierCreate,
    user: User = Depends(require_permission(Permission.SUPPLIER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    supplier = await service.create(body, user.id)
    return ApiResponse(data=SupplierRead.model_validate(supplier))


@router.get("/{id}", response_model=ApiResponse[SupplierRead])
async def get_supplier(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SUPPLIER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    supplier = await service.get_by_id(id)
    return ApiResponse(data=SupplierRead.model_validate(supplier))


@router.put("/{id}", response_model=ApiResponse[SupplierRead])
async def update_supplier(
    id: uuid.UUID,
    body: SupplierUpdate,
    user: User = Depends(require_permission(Permission.SUPPLIER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    supplier = await service.update(id, body, user.id)
    return ApiResponse(data=SupplierRead.model_validate(supplier))


@router.get("/export", response_model=ApiResponse)
async def export_suppliers(
    user: User = Depends(require_super_admin),
):
    return ApiResponse(code=501, message="功能开发中")


@router.get("/{id}/purchase-orders", response_model=ApiResponse)
async def get_supplier_purchase_orders(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SUPPLIER_VIEW)),
):
    return ApiResponse(code=501, message="功能开发中（Phase 2）")


@router.post(
    "/{id}/products",
    response_model=ApiResponse[SupplierProductRead],
    status_code=status.HTTP_201_CREATED,
)
async def add_supplier_product(
    id: uuid.UUID,
    body: SupplierProductCreate,
    user: User = Depends(require_permission(Permission.SUPPLIER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    sp = await service.add_product(id, body)
    return ApiResponse(data=SupplierProductRead.model_validate(sp))


@router.delete("/{id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_supplier_product(
    id: uuid.UUID,
    product_id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SUPPLIER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    await service.remove_product(id, product_id)
