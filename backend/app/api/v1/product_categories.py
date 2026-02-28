import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryRead,
    ProductCategoryTreeNode,
    ProductCategoryUpdate,
)
from app.services.product_category_service import ProductCategoryService

router = APIRouter(prefix="/product-categories", tags=["品类管理"])


@router.get("/tree", response_model=ApiResponse[list[ProductCategoryTreeNode]])
async def get_category_tree(
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductCategoryService(db)
    tree = await service.get_tree()
    return ApiResponse(data=tree)


@router.get("/{id}/children", response_model=ApiResponse[list[ProductCategoryRead]])
async def get_category_children(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductCategoryService(db)
    children = await service.get_children(id)
    return ApiResponse(data=children)


@router.post(
    "",
    response_model=ApiResponse[ProductCategoryRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    body: ProductCategoryCreate,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductCategoryService(db)
    cat = await service.create(body)
    return ApiResponse(data=ProductCategoryRead.model_validate(cat))


@router.put("/{id}", response_model=ApiResponse[ProductCategoryRead])
async def update_category(
    id: uuid.UUID,
    body: ProductCategoryUpdate,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductCategoryService(db)
    cat = await service.update(id, body)
    return ApiResponse(data=ProductCategoryRead.model_validate(cat))


@router.delete("/{id}", response_model=ApiResponse)
async def delete_category(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.SYSTEM_CONFIG)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductCategoryService(db)
    await service.delete(id)
    return ApiResponse(message="删除成功")
