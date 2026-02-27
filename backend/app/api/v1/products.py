import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission, require_super_admin
from app.core.permissions import Permission
from app.database import get_db
from app.models.enums import ProductCategory, ProductStatus
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductListParams,
    ProductRead,
    ProductStatusUpdate,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["商品管理"])


@router.get("", response_model=PaginatedResponse[ProductRead])
async def list_products(
    keyword: str | None = None,
    category: ProductCategory | None = None,
    product_status: ProductStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    params = ProductListParams(
        keyword=keyword,
        category=category,
        status=product_status,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.list_products(params)
    return PaginatedResponse(data=data)


@router.post("", response_model=ApiResponse[ProductRead], status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    user: User = Depends(require_permission(Permission.PRODUCT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.create(body, user.id)
    return ApiResponse(data=ProductRead.model_validate(product))


@router.get("/{id}", response_model=ApiResponse[ProductRead])
async def get_product(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_by_id(id)
    return ApiResponse(data=ProductRead.model_validate(product))


@router.put("/{id}", response_model=ApiResponse[ProductRead])
async def update_product(
    id: uuid.UUID,
    body: ProductUpdate,
    user: User = Depends(require_permission(Permission.PRODUCT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.update(id, body, user.id)
    return ApiResponse(data=ProductRead.model_validate(product))


@router.patch("/{id}/status", response_model=ApiResponse[ProductRead])
async def update_product_status(
    id: uuid.UUID,
    body: ProductStatusUpdate,
    user: User = Depends(require_permission(Permission.PRODUCT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.update_status(id, body.status, user.id)
    return ApiResponse(data=ProductRead.model_validate(product))


@router.post("/import", response_model=ApiResponse)
async def import_products(
    user: User = Depends(require_permission(Permission.PRODUCT_IMPORT)),
):
    return ApiResponse(code=501, message="功能开发中")


@router.get("/export", response_model=ApiResponse)
async def export_products(
    user: User = Depends(require_super_admin),
):
    return ApiResponse(code=501, message="功能开发中")


@router.get("/template", response_model=ApiResponse)
async def download_template(
    user: User = Depends(require_permission(Permission.PRODUCT_IMPORT)),
):
    return ApiResponse(code=501, message="功能开发中")
