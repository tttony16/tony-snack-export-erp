import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.supplier import Supplier, SupplierProduct
from app.repositories.supplier_repo import SupplierRepository
from app.schemas.common import PaginatedData
from app.schemas.supplier import (
    SupplierCreate,
    SupplierListParams,
    SupplierProductCreate,
    SupplierProductRead,
    SupplierRead,
    SupplierUpdate,
)
from app.utils.code_generator import generate_entity_code


class SupplierService:
    def __init__(self, db: AsyncSession):
        self.repo = SupplierRepository(db)

    async def create(self, data: SupplierCreate, user_id: uuid.UUID) -> Supplier:
        seq = await self.repo.get_next_sequence()
        supplier_code = generate_entity_code("SUP", seq)

        supplier = Supplier(
            supplier_code=supplier_code,
            **data.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        return await self.repo.create(supplier)

    async def get_by_id(self, id: uuid.UUID) -> Supplier:
        supplier = await self.repo.get_by_id(id)
        if not supplier:
            raise NotFoundError("供应商", str(id))
        return supplier

    async def update(self, id: uuid.UUID, data: SupplierUpdate, user_id: uuid.UUID) -> Supplier:
        supplier = await self.get_by_id(id)
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        return await self.repo.update(supplier, update_data)

    async def list_suppliers(self, params: SupplierListParams) -> PaginatedData[SupplierRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            keyword=params.keyword,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[SupplierRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    async def add_product(
        self, supplier_id: uuid.UUID, data: SupplierProductCreate
    ) -> SupplierProduct:
        await self.get_by_id(supplier_id)

        existing = await self.repo.get_supplier_product(supplier_id, data.product_id)
        if existing:
            raise ConflictError(code=40912, message="该供应商已关联此商品")

        sp = SupplierProduct(
            supplier_id=supplier_id,
            product_id=data.product_id,
            supply_price=data.supply_price,
            remark=data.remark,
        )
        return await self.repo.add_product(sp)

    async def remove_product(self, supplier_id: uuid.UUID, product_id: uuid.UUID) -> None:
        sp = await self.repo.get_supplier_product(supplier_id, product_id)
        if not sp:
            raise NotFoundError("供应商商品关联", f"{supplier_id}/{product_id}")
        await self.repo.remove_product(sp)

    async def get_products(self, supplier_id: uuid.UUID) -> list[SupplierProductRead]:
        await self.get_by_id(supplier_id)
        items = await self.repo.get_supplier_products(supplier_id)
        return [SupplierProductRead.model_validate(item) for item in items]
