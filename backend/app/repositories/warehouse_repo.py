import uuid
from datetime import date

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase_order import PurchaseOrderItem
from app.models.warehouse import InventoryRecord, ReceivingNote, ReceivingNoteItem
from app.repositories.base import BaseRepository


class ReceivingNoteRepository(BaseRepository[ReceivingNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(ReceivingNote, db)

    async def get_with_items(self, id: uuid.UUID) -> ReceivingNote | None:
        result = await self.db.execute(
            select(ReceivingNote)
            .options(selectinload(ReceivingNote.items))
            .where(ReceivingNote.id == id)
        )
        return result.scalar_one_or_none()

    async def count_by_date(self, receiving_date: date) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(ReceivingNote)
            .where(ReceivingNote.receiving_date == receiving_date)
        )
        return result.scalar_one()

    async def search(
        self,
        *,
        purchase_order_id: uuid.UUID | None = None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[ReceivingNote], int]:
        filters = []
        if purchase_order_id:
            filters.append(ReceivingNote.purchase_order_id == purchase_order_id)
        if keyword:
            filters.append(
                or_(
                    ReceivingNote.note_no.ilike(f"%{keyword}%"),
                    ReceivingNote.receiver.ilike(f"%{keyword}%"),
                )
            )
        return await self.get_list(
            offset=offset, limit=limit, order_by=order_by, order_desc=order_desc, filters=filters
        )

    async def delete_items(self, note_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(ReceivingNoteItem).where(ReceivingNoteItem.receiving_note_id == note_id)
        )

    async def add_items(self, items: list[ReceivingNoteItem]) -> None:
        self.db.add_all(items)
        await self.db.flush()

    async def get_purchase_order_item(self, item_id: uuid.UUID) -> PurchaseOrderItem | None:
        result = await self.db.execute(
            select(PurchaseOrderItem).where(PurchaseOrderItem.id == item_id)
        )
        return result.scalar_one_or_none()


class InventoryRepository(BaseRepository[InventoryRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(InventoryRecord, db)

    async def get_by_product(
        self,
        *,
        product_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        """Group inventory by product."""
        query = select(
            InventoryRecord.product_id,
            func.sum(InventoryRecord.quantity).label("total_quantity"),
            func.sum(InventoryRecord.available_quantity).label("available_quantity"),
        ).group_by(InventoryRecord.product_id)
        count_query = select(func.count()).select_from(
            select(InventoryRecord.product_id).group_by(InventoryRecord.product_id).subquery()
        )
        if product_id:
            query = query.where(InventoryRecord.product_id == product_id)
            count_query = select(func.literal(1))  # single product

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        rows = result.all()
        items = [
            {
                "product_id": row.product_id,
                "total_quantity": row.total_quantity,
                "available_quantity": row.available_quantity,
            }
            for row in rows
        ]
        return items, total

    async def get_by_sales_order(
        self,
        sales_order_id: uuid.UUID,
    ) -> list[dict]:
        """Group inventory by sales_order + product."""
        result = await self.db.execute(
            select(
                InventoryRecord.sales_order_id,
                InventoryRecord.product_id,
                func.sum(InventoryRecord.quantity).label("total_quantity"),
                func.sum(InventoryRecord.available_quantity).label("available_quantity"),
            )
            .where(InventoryRecord.sales_order_id == sales_order_id)
            .group_by(InventoryRecord.sales_order_id, InventoryRecord.product_id)
        )
        rows = result.all()
        return [
            {
                "sales_order_id": row.sales_order_id,
                "product_id": row.product_id,
                "total_quantity": row.total_quantity,
                "available_quantity": row.available_quantity,
            }
            for row in rows
        ]

    async def get_available_quantity(self, product_id: uuid.UUID, sales_order_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.coalesce(func.sum(InventoryRecord.available_quantity), 0)).where(
                InventoryRecord.product_id == product_id,
                InventoryRecord.sales_order_id == sales_order_id,
            )
        )
        return result.scalar_one()

    async def search(
        self,
        *,
        product_id: uuid.UUID | None = None,
        sales_order_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[InventoryRecord], int]:
        filters = []
        if product_id:
            filters.append(InventoryRecord.product_id == product_id)
        if sales_order_id:
            filters.append(InventoryRecord.sales_order_id == sales_order_id)
        return await self.get_list(
            offset=offset, limit=limit, order_by=order_by, order_desc=order_desc, filters=filters
        )
