import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import SalesOrderStatus
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.repositories.base import BaseRepository


class SalesOrderRepository(BaseRepository[SalesOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(SalesOrder, db)

    async def get_with_items(self, id: uuid.UUID) -> SalesOrder | None:
        result = await self.db.execute(
            select(SalesOrder).options(selectinload(SalesOrder.items)).where(SalesOrder.id == id)
        )
        return result.scalar_one_or_none()

    async def count_by_date(self, order_date: date) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(SalesOrder).where(SalesOrder.order_date == order_date)
        )
        return result.scalar_one()

    async def search(
        self,
        *,
        keyword: str | None = None,
        status: SalesOrderStatus | None = None,
        customer_id: uuid.UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[SalesOrder], int]:
        filters = []
        if keyword:
            filters.append(
                or_(
                    SalesOrder.order_no.ilike(f"%{keyword}%"),
                    SalesOrder.destination_port.ilike(f"%{keyword}%"),
                )
            )
        if status:
            filters.append(SalesOrder.status == status)
        if customer_id:
            filters.append(SalesOrder.customer_id == customer_id)
        if date_from:
            filters.append(SalesOrder.order_date >= date_from)
        if date_to:
            filters.append(SalesOrder.order_date <= date_to)

        return await self.get_list(
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            filters=filters,
        )

    async def get_kanban_stats(self) -> list[dict]:
        result = await self.db.execute(
            select(
                SalesOrder.status,
                func.count().label("count"),
                func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_amount"),
            ).group_by(SalesOrder.status)
        )
        rows = result.all()
        return [
            {
                "status": row.status,
                "count": row.count,
                "total_amount": Decimal(str(row.total_amount)),
            }
            for row in rows
        ]

    async def delete_items(self, order_id: uuid.UUID) -> None:
        await self.db.execute(
            delete(SalesOrderItem).where(SalesOrderItem.sales_order_id == order_id)
        )

    async def add_items(self, items: list[SalesOrderItem]) -> None:
        self.db.add_all(items)
        await self.db.flush()

    async def get_item_by_id(self, item_id: uuid.UUID) -> SalesOrderItem | None:
        result = await self.db.execute(select(SalesOrderItem).where(SalesOrderItem.id == item_id))
        return result.scalar_one_or_none()
