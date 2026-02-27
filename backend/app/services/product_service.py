import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.enums import ProductStatus
from app.models.product import Product
from app.repositories.product_repo import ProductRepository
from app.schemas.common import PaginatedData
from app.schemas.product import ProductCreate, ProductListParams, ProductRead, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def create(self, data: ProductCreate, user_id: uuid.UUID) -> Product:
        existing = await self.repo.get_by_sku_code(data.sku_code)
        if existing:
            raise ConflictError(code=40910, message=f"SKU 编码 {data.sku_code} 已存在")

        product = Product(
            **data.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        return await self.repo.create(product)

    async def get_by_id(self, id: uuid.UUID) -> Product:
        product = await self.repo.get_by_id(id)
        if not product:
            raise NotFoundError("商品", str(id))
        return product

    async def update(self, id: uuid.UUID, data: ProductUpdate, user_id: uuid.UUID) -> Product:
        product = await self.get_by_id(id)
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        return await self.repo.update(product, update_data)

    async def update_status(
        self, id: uuid.UUID, status: ProductStatus, user_id: uuid.UUID
    ) -> Product:
        product = await self.get_by_id(id)
        return await self.repo.update(product, {"status": status, "updated_by": user_id})

    async def list_products(self, params: ProductListParams) -> PaginatedData[ProductRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            keyword=params.keyword,
            category=params.category.value if params.category else None,
            status=params.status.value if params.status else None,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[ProductRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    async def delete(self, id: uuid.UUID) -> None:
        product = await self.get_by_id(id)
        await self.repo.delete(product)
