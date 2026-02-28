import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, ConflictError, NotFoundError
from app.models.product_category import ProductCategoryModel
from app.repositories.product_category_repo import ProductCategoryRepository
from app.schemas.product_category import (
    ProductCategoryCreate,
    ProductCategoryRead,
    ProductCategoryTreeNode,
    ProductCategoryUpdate,
)


class ProductCategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductCategoryRepository(db)

    async def get_tree(self) -> list[ProductCategoryTreeNode]:
        all_cats = await self.repo.get_all_ordered()
        cat_map: dict[uuid.UUID, ProductCategoryTreeNode] = {}
        roots: list[ProductCategoryTreeNode] = []

        for cat in all_cats:
            node = ProductCategoryTreeNode(
                id=cat.id,
                name=cat.name,
                level=cat.level,
                parent_id=cat.parent_id,
                sort_order=cat.sort_order,
                created_at=cat.created_at,
                updated_at=cat.updated_at,
                children=[],
            )
            cat_map[cat.id] = node

        for cat in all_cats:
            node = cat_map[cat.id]
            if cat.parent_id and cat.parent_id in cat_map:
                cat_map[cat.parent_id].children.append(node)
            else:
                roots.append(node)

        return roots

    async def get_children(
        self, parent_id: uuid.UUID | None
    ) -> list[ProductCategoryRead]:
        items = await self.repo.get_by_parent_id(parent_id)
        return [ProductCategoryRead.model_validate(item) for item in items]

    async def create(self, data: ProductCategoryCreate) -> ProductCategoryModel:
        # Calculate level
        if data.parent_id is None:
            level = 1
        else:
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent:
                raise NotFoundError("父品类", str(data.parent_id))
            if parent.level >= 3:
                raise BusinessError(code=42201, message="品类最多支持三级")
            level = parent.level + 1

        # Check name uniqueness under same parent
        existing = await self.repo.get_by_name_and_parent(data.name, data.parent_id)
        if existing:
            raise ConflictError(code=40911, message=f"同级下品类名 '{data.name}' 已存在")

        cat = ProductCategoryModel(
            name=data.name,
            level=level,
            parent_id=data.parent_id,
            sort_order=data.sort_order,
        )
        return await self.repo.create(cat)

    async def update(
        self, id: uuid.UUID, data: ProductCategoryUpdate
    ) -> ProductCategoryModel:
        cat = await self.repo.get_by_id(id)
        if not cat:
            raise NotFoundError("品类", str(id))

        update_data = data.model_dump(exclude_unset=True)

        # Check name uniqueness if name is being changed
        if "name" in update_data and update_data["name"] != cat.name:
            existing = await self.repo.get_by_name_and_parent(
                update_data["name"], cat.parent_id
            )
            if existing:
                raise ConflictError(
                    code=40911,
                    message=f"同级下品类名 '{update_data['name']}' 已存在",
                )

        return await self.repo.update(cat, update_data)

    async def delete(self, id: uuid.UUID) -> None:
        cat = await self.repo.get_by_id(id)
        if not cat:
            raise NotFoundError("品类", str(id))

        # Check if any products reference this category or its descendants
        if await self.repo.has_products(id):
            raise BusinessError(
                code=42202,
                message="该品类或其子品类下存在商品，无法删除",
            )

        await self.repo.delete(cat)

    async def get_by_id(self, id: uuid.UUID) -> ProductCategoryModel:
        cat = await self.repo.get_by_id(id)
        if not cat:
            raise NotFoundError("品类", str(id))
        return cat
