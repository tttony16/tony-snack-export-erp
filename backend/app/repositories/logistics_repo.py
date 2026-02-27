import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import LogisticsStatus
from app.models.logistics import LogisticsCost, LogisticsRecord
from app.repositories.base import BaseRepository


class LogisticsRecordRepository(BaseRepository[LogisticsRecord]):
    def __init__(self, db: AsyncSession):
        super().__init__(LogisticsRecord, db)

    async def get_with_costs(self, id: uuid.UUID) -> LogisticsRecord | None:
        result = await self.db.execute(
            select(LogisticsRecord)
            .options(selectinload(LogisticsRecord.costs))
            .where(LogisticsRecord.id == id)
        )
        return result.scalar_one_or_none()

    async def count_by_date(self, d: date) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(LogisticsRecord)
            .where(func.date(LogisticsRecord.created_at) == d)
        )
        return result.scalar_one()

    async def search(
        self,
        *,
        status: LogisticsStatus | None = None,
        container_plan_id: uuid.UUID | None = None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[LogisticsRecord], int]:
        filters = []
        if status:
            filters.append(LogisticsRecord.status == status)
        if container_plan_id:
            filters.append(LogisticsRecord.container_plan_id == container_plan_id)
        if keyword:
            filters.append(
                or_(
                    LogisticsRecord.logistics_no.ilike(f"%{keyword}%"),
                    LogisticsRecord.bl_no.ilike(f"%{keyword}%"),
                    LogisticsRecord.vessel_voyage.ilike(f"%{keyword}%"),
                )
            )
        return await self.get_list(
            offset=offset, limit=limit, order_by=order_by, order_desc=order_desc, filters=filters
        )

    async def get_kanban_stats(self) -> list[dict]:
        result = await self.db.execute(
            select(
                LogisticsRecord.status,
                func.count().label("count"),
                func.coalesce(func.sum(LogisticsRecord.total_cost), 0).label("total_cost"),
            ).group_by(LogisticsRecord.status)
        )
        rows = result.all()
        return [
            {
                "status": row.status,
                "count": row.count,
                "total_cost": Decimal(str(row.total_cost)),
            }
            for row in rows
        ]

    # --- Costs ---
    async def get_cost_by_id(self, cost_id: uuid.UUID) -> LogisticsCost | None:
        result = await self.db.execute(select(LogisticsCost).where(LogisticsCost.id == cost_id))
        return result.scalar_one_or_none()

    async def add_cost(self, cost: LogisticsCost) -> LogisticsCost:
        self.db.add(cost)
        await self.db.flush()
        await self.db.refresh(cost)
        return cost

    async def delete_cost(self, cost: LogisticsCost) -> None:
        await self.db.delete(cost)
        await self.db.flush()
