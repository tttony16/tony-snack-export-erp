import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier, SupplierProduct
from app.repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession):
        super().__init__(Supplier, db)

    async def get_by_code(self, supplier_code: str) -> Supplier | None:
        result = await self.db.execute(
            select(Supplier).where(Supplier.supplier_code == supplier_code)
        )
        return result.scalar_one_or_none()

    async def get_next_sequence(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Supplier))
        count = result.scalar_one()
        return count + 1

    async def search(
        self,
        *,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Supplier], int]:
        filters = []
        if keyword:
            filters.append(
                or_(
                    Supplier.supplier_code.ilike(f"%{keyword}%"),
                    Supplier.name.ilike(f"%{keyword}%"),
                    Supplier.contact_person.ilike(f"%{keyword}%"),
                )
            )

        return await self.get_list(
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            filters=filters,
        )

    async def add_product(self, supplier_product: SupplierProduct) -> SupplierProduct:
        self.db.add(supplier_product)
        await self.db.flush()
        await self.db.refresh(supplier_product)
        return supplier_product

    async def get_supplier_product(
        self, supplier_id: uuid.UUID, product_id: uuid.UUID
    ) -> SupplierProduct | None:
        result = await self.db.execute(
            select(SupplierProduct).where(
                SupplierProduct.supplier_id == supplier_id,
                SupplierProduct.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def remove_product(self, supplier_product: SupplierProduct) -> None:
        await self.db.delete(supplier_product)
        await self.db.flush()

    async def get_supplier_products(self, supplier_id: uuid.UUID) -> list[SupplierProduct]:
        result = await self.db.execute(
            select(SupplierProduct).where(SupplierProduct.supplier_id == supplier_id)
        )
        return list(result.scalars().all())
