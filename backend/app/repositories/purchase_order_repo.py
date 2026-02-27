import uuid
from datetime import date

from sqlalchemy import func, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import PurchaseOrderStatus
from app.models.purchase_order import (
    PurchaseOrder,
    PurchaseOrderItem,
    purchase_order_sales_orders,
)
from app.models.sales_order import SalesOrderItem
from app.repositories.base import BaseRepository


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(PurchaseOrder, db)

    async def get_with_items(self, id: uuid.UUID) -> PurchaseOrder | None:
        result = await self.db.execute(
            select(PurchaseOrder)
            .options(
                selectinload(PurchaseOrder.items),
                selectinload(PurchaseOrder.sales_orders),
            )
            .where(PurchaseOrder.id == id)
        )
        return result.scalar_one_or_none()

    async def count_by_date(self, order_date: date) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(PurchaseOrder)
            .where(PurchaseOrder.order_date == order_date)
        )
        return result.scalar_one()

    async def search(
        self,
        *,
        keyword: str | None = None,
        status: PurchaseOrderStatus | None = None,
        supplier_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[PurchaseOrder], int]:
        filters = []
        if keyword:
            filters.append(
                or_(
                    PurchaseOrder.order_no.ilike(f"%{keyword}%"),
                )
            )
        if status:
            filters.append(PurchaseOrder.status == status)
        if supplier_id:
            filters.append(PurchaseOrder.supplier_id == supplier_id)

        return await self.get_list(
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            filters=filters,
        )

    async def link_sales_orders(self, po_id: uuid.UUID, so_ids: list[uuid.UUID]) -> None:
        for so_id in so_ids:
            # Check if already linked
            existing = await self.db.execute(
                select(purchase_order_sales_orders).where(
                    purchase_order_sales_orders.c.purchase_order_id == po_id,
                    purchase_order_sales_orders.c.sales_order_id == so_id,
                )
            )
            if not existing.first():
                await self.db.execute(
                    insert(purchase_order_sales_orders).values(
                        purchase_order_id=po_id, sales_order_id=so_id
                    )
                )
        await self.db.flush()

    async def get_linked_so_ids(self, po_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.db.execute(
            select(purchase_order_sales_orders.c.sales_order_id).where(
                purchase_order_sales_orders.c.purchase_order_id == po_id
            )
        )
        return [row[0] for row in result.all()]

    async def get_sales_order_item(self, item_id: uuid.UUID) -> SalesOrderItem | None:
        result = await self.db.execute(select(SalesOrderItem).where(SalesOrderItem.id == item_id))
        return result.scalar_one_or_none()

    async def delete_items(self, order_id: uuid.UUID) -> list[PurchaseOrderItem]:
        """Delete all items for an order, returning them first for rollback logic."""
        result = await self.db.execute(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == order_id)
        )
        old_items = list(result.scalars().all())
        for item in old_items:
            await self.db.delete(item)
        await self.db.flush()
        return old_items

    async def add_items(self, items: list[PurchaseOrderItem]) -> None:
        self.db.add_all(items)
        await self.db.flush()
