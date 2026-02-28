import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, ConflictError, NotFoundError
from app.models.enums import ProductStatus
from app.models.product import Product
from app.models.product_category import ProductCategoryModel
from app.repositories.product_category_repo import ProductCategoryRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.common import PaginatedData
from app.schemas.product import ProductCreate, ProductListParams, ProductRead, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)
        self.category_repo = ProductCategoryRepository(db)

    async def create(self, data: ProductCreate, user_id: uuid.UUID) -> Product:
        existing = await self.repo.get_by_sku_code(data.sku_code)
        if existing:
            raise ConflictError(code=40910, message=f"SKU 编码 {data.sku_code} 已存在")

        # Validate category_id points to a level-3 category
        await self._validate_category_id(data.category_id)

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

        if "category_id" in update_data and update_data["category_id"] is not None:
            await self._validate_category_id(update_data["category_id"])

        update_data["updated_by"] = user_id
        return await self.repo.update(product, update_data)

    async def update_status(
        self, id: uuid.UUID, status: ProductStatus, user_id: uuid.UUID
    ) -> Product:
        product = await self.get_by_id(id)
        return await self.repo.update(product, {"status": status, "updated_by": user_id})

    async def list_products(self, params: ProductListParams) -> PaginatedData[ProductRead]:
        offset = (params.page - 1) * params.page_size

        # If category_id is specified, find all descendant leaf IDs
        category_ids = None
        if params.category_id:
            category_ids = await self.category_repo.get_descendant_leaf_ids(
                params.category_id
            )
            if not category_ids:
                # Also include the ID itself in case it's a leaf
                category_ids = [params.category_id]

        items, total = await self.repo.search(
            keyword=params.keyword,
            category_ids=category_ids,
            brand=params.brand,
            status=params.status.value if params.status else None,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )

        # Load all categories once for efficient name resolution
        cat_map = await self._load_category_map()

        product_reads = []
        for item in items:
            pr = ProductRead.model_validate(item)
            self._fill_category_names_from_map(pr, cat_map)
            product_reads.append(pr)

        return PaginatedData(
            items=product_reads,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    async def get_brands(self) -> list[str]:
        return await self.repo.get_distinct_brands()

    async def delete(self, id: uuid.UUID) -> None:
        product = await self.get_by_id(id)
        await self.repo.delete(product)

    async def _validate_category_id(self, category_id: uuid.UUID) -> None:
        """Validate that category_id points to a valid leaf category (no children)."""
        cat = await self.category_repo.get_by_id(category_id)
        if not cat:
            raise BusinessError(code=42203, message="品类不存在")
        children = await self.category_repo.get_by_parent_id(cat.id)
        if children:
            raise BusinessError(code=42204, message="请选择最末级品类")

    async def _load_category_map(self) -> dict[uuid.UUID, "ProductCategoryModel"]:
        """Load all categories into a dict keyed by ID."""
        all_cats = await self.category_repo.get_all_ordered()
        return {cat.id: cat for cat in all_cats}

    def _fill_category_names_from_map(
        self,
        read: ProductRead,
        cat_map: dict[uuid.UUID, "ProductCategoryModel"],
    ) -> None:
        """Fill category level names by walking the parent chain via in-memory map."""
        cat = cat_map.get(read.category_id)
        if not cat:
            return

        names: dict[int, str] = {}
        current = cat
        while current:
            names[current.level] = current.name
            current = cat_map.get(current.parent_id) if current.parent_id else None

        read.category_level1_name = names.get(1)
        read.category_level2_name = names.get(2)
        read.category_level3_name = names.get(3)

    async def fill_category_names(self, read: ProductRead) -> None:
        """Fill category names for a single ProductRead (used by API endpoints)."""
        cat_map = await self._load_category_map()
        self._fill_category_names_from_map(read, cat_map)
