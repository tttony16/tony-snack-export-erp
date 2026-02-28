import uuid
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.outbound import OutboundOrder, OutboundOrderItem
from app.repositories.base import BaseRepository


class OutboundOrderRepository(BaseRepository[OutboundOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(OutboundOrder, db)

    async def get_with_items(self, id: uuid.UUID) -> OutboundOrder | None:
        result = await self.db.execute(
            select(OutboundOrder)
            .options(selectinload(OutboundOrder.items))
            .where(OutboundOrder.id == id)
        )
        return result.scalar_one_or_none()

    async def count_by_date(self, d: date) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(OutboundOrder)
            .where(func.date(OutboundOrder.created_at) == d)
        )
        return result.scalar_one()

    async def get_by_container_plan(self, container_plan_id: uuid.UUID) -> OutboundOrder | None:
        result = await self.db.execute(
            select(OutboundOrder)
            .options(selectinload(OutboundOrder.items))
            .where(
                OutboundOrder.container_plan_id == container_plan_id,
                OutboundOrder.status != "cancelled",
            )
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        *,
        status=None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[OutboundOrder], int]:
        filters = []
        if status:
            filters.append(OutboundOrder.status == status)
        if keyword:
            filters.append(
                or_(
                    OutboundOrder.order_no.ilike(f"%{keyword}%"),
                    OutboundOrder.operator.ilike(f"%{keyword}%"),
                )
            )
        return await self.get_list(
            offset=offset, limit=limit, order_by=order_by, order_desc=order_desc, filters=filters
        )

    async def add_items(self, items: list[OutboundOrderItem]) -> None:
        self.db.add_all(items)
        await self.db.flush()
