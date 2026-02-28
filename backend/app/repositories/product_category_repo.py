import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.product_category import ProductCategoryModel
from app.repositories.base import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategoryModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductCategoryModel, db)

    async def get_all_ordered(self) -> list[ProductCategoryModel]:
        result = await self.db.execute(
            select(ProductCategoryModel).order_by(
                ProductCategoryModel.level,
                ProductCategoryModel.sort_order,
                ProductCategoryModel.name,
            )
        )
        return list(result.scalars().all())

    async def get_by_parent_id(
        self, parent_id: uuid.UUID | None
    ) -> list[ProductCategoryModel]:
        query = select(ProductCategoryModel).where(
            ProductCategoryModel.parent_id == parent_id
        ).order_by(ProductCategoryModel.sort_order, ProductCategoryModel.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_name_and_parent(
        self, name: str, parent_id: uuid.UUID | None
    ) -> ProductCategoryModel | None:
        query = select(ProductCategoryModel).where(
            ProductCategoryModel.name == name,
            ProductCategoryModel.parent_id == parent_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def has_products(self, category_id: uuid.UUID) -> bool:
        """Check if this category or any of its descendants have associated products."""
        # Collect all descendant IDs (including self)
        ids = await self._collect_descendant_ids(category_id)
        result = await self.db.execute(
            select(exists().where(Product.category_id.in_(ids)))
        )
        return result.scalar_one()

    async def _collect_descendant_ids(self, category_id: uuid.UUID) -> list[uuid.UUID]:
        """Recursively collect this category's ID and all descendant IDs."""
        ids = [category_id]
        children = await self.get_by_parent_id(category_id)
        for child in children:
            ids.extend(await self._collect_descendant_ids(child.id))
        return ids

    async def get_descendant_leaf_ids(self, category_id: uuid.UUID) -> list[uuid.UUID]:
        """Get all level-3 (leaf) descendant IDs for a given category."""
        cat = await self.get_by_id(category_id)
        if not cat:
            return []
        if cat.level == 3:
            return [cat.id]
        children = await self.get_by_parent_id(category_id)
        leaf_ids: list[uuid.UUID] = []
        for child in children:
            if child.level == 3:
                leaf_ids.append(child.id)
            else:
                leaf_ids.extend(await self.get_descendant_leaf_ids(child.id))
        return leaf_ids
