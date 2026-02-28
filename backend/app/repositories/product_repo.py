import uuid

from sqlalchemy import distinct, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_sku_code(self, sku_code: str) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.sku_code == sku_code))
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        keyword: str | None = None,
        category_ids: list[uuid.UUID] | None = None,
        brand: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Product], int]:
        filters = []
        if keyword:
            filters.append(
                or_(
                    Product.sku_code.ilike(f"%{keyword}%"),
                    Product.name_cn.ilike(f"%{keyword}%"),
                    Product.name_en.ilike(f"%{keyword}%"),
                    Product.brand.ilike(f"%{keyword}%"),
                )
            )
        if category_ids:
            filters.append(Product.category_id.in_(category_ids))
        if brand:
            filters.append(Product.brand == brand)
        if status:
            filters.append(Product.status == status)

        return await self.get_list(
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            filters=filters,
        )

    async def get_distinct_brands(self) -> list[str]:
        result = await self.db.execute(
            select(distinct(Product.brand))
            .where(Product.brand.isnot(None), Product.brand != "")
            .order_by(Product.brand)
        )
        return list(result.scalars().all())
