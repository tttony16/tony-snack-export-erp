import uuid
from datetime import date

from sqlalchemy import func, insert, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.container import (
    ContainerPlan,
    ContainerPlanItem,
    ContainerStuffingPhoto,
    ContainerStuffingRecord,
    container_plan_sales_orders,
)
from app.repositories.base import BaseRepository


class ContainerPlanRepository(BaseRepository[ContainerPlan]):
    def __init__(self, db: AsyncSession):
        super().__init__(ContainerPlan, db)

    async def get_with_items(self, id: uuid.UUID) -> ContainerPlan | None:
        result = await self.db.execute(
            select(ContainerPlan)
            .options(
                selectinload(ContainerPlan.items),
                selectinload(ContainerPlan.sales_orders),
                selectinload(ContainerPlan.stuffing_records).selectinload(
                    ContainerStuffingRecord.photos
                ),
            )
            .where(ContainerPlan.id == id)
        )
        return result.scalar_one_or_none()

    async def count_by_date(self, d: date) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(ContainerPlan)
            .where(func.date(ContainerPlan.created_at) == d)
        )
        return result.scalar_one()

    async def search(
        self,
        *,
        status=None,
        keyword: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[ContainerPlan], int]:
        filters = []
        if status:
            filters.append(ContainerPlan.status == status)
        if keyword:
            filters.append(
                or_(
                    ContainerPlan.plan_no.ilike(f"%{keyword}%"),
                    ContainerPlan.destination_port.ilike(f"%{keyword}%"),
                )
            )
        return await self.get_list(
            offset=offset, limit=limit, order_by=order_by, order_desc=order_desc, filters=filters
        )

    async def link_sales_orders(self, plan_id: uuid.UUID, so_ids: list[uuid.UUID]) -> None:
        for so_id in so_ids:
            existing = await self.db.execute(
                select(container_plan_sales_orders).where(
                    container_plan_sales_orders.c.container_plan_id == plan_id,
                    container_plan_sales_orders.c.sales_order_id == so_id,
                )
            )
            if not existing.first():
                await self.db.execute(
                    insert(container_plan_sales_orders).values(
                        container_plan_id=plan_id, sales_order_id=so_id
                    )
                )
        await self.db.flush()

    async def get_linked_so_ids(self, plan_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.db.execute(
            select(container_plan_sales_orders.c.sales_order_id).where(
                container_plan_sales_orders.c.container_plan_id == plan_id
            )
        )
        return [row[0] for row in result.all()]

    # --- Items ---
    async def get_item_by_id(self, item_id: uuid.UUID) -> ContainerPlanItem | None:
        result = await self.db.execute(
            select(ContainerPlanItem).where(ContainerPlanItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_items_by_plan(self, plan_id: uuid.UUID) -> list[ContainerPlanItem]:
        result = await self.db.execute(
            select(ContainerPlanItem).where(ContainerPlanItem.container_plan_id == plan_id)
        )
        return list(result.scalars().all())

    async def get_items_by_seq(
        self, plan_id: uuid.UUID, container_seq: int
    ) -> list[ContainerPlanItem]:
        result = await self.db.execute(
            select(ContainerPlanItem).where(
                ContainerPlanItem.container_plan_id == plan_id,
                ContainerPlanItem.container_seq == container_seq,
            )
        )
        return list(result.scalars().all())

    async def get_loaded_quantity(
        self,
        product_id: uuid.UUID,
        sales_order_id: uuid.UUID,
        exclude_plan_id: uuid.UUID | None = None,
    ) -> int:
        query = select(func.coalesce(func.sum(ContainerPlanItem.quantity), 0)).where(
            ContainerPlanItem.product_id == product_id,
            ContainerPlanItem.sales_order_id == sales_order_id,
        )
        if exclude_plan_id:
            query = query.where(ContainerPlanItem.container_plan_id != exclude_plan_id)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def add_item(self, item: ContainerPlanItem) -> ContainerPlanItem:
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete_item(self, item: ContainerPlanItem) -> None:
        await self.db.delete(item)
        await self.db.flush()

    # --- Stuffing Records ---
    async def get_stuffing_records(self, plan_id: uuid.UUID) -> list[ContainerStuffingRecord]:
        result = await self.db.execute(
            select(ContainerStuffingRecord)
            .options(selectinload(ContainerStuffingRecord.photos))
            .where(ContainerStuffingRecord.container_plan_id == plan_id)
        )
        return list(result.scalars().all())

    async def get_stuffing_record_by_seq(
        self, plan_id: uuid.UUID, seq: int
    ) -> ContainerStuffingRecord | None:
        result = await self.db.execute(
            select(ContainerStuffingRecord).where(
                ContainerStuffingRecord.container_plan_id == plan_id,
                ContainerStuffingRecord.container_seq == seq,
            )
        )
        return result.scalar_one_or_none()

    async def add_stuffing_record(self, record: ContainerStuffingRecord) -> ContainerStuffingRecord:
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def add_stuffing_photo(self, photo: ContainerStuffingPhoto) -> ContainerStuffingPhoto:
        self.db.add(photo)
        await self.db.flush()
        await self.db.refresh(photo)
        return photo
