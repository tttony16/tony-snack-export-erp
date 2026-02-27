import math
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.enums import ContainerPlanStatus, LogisticsStatus, SalesOrderStatus
from app.models.logistics import LogisticsCost, LogisticsRecord
from app.models.sales_order import SalesOrder
from app.repositories.container_repo import ContainerPlanRepository
from app.repositories.logistics_repo import LogisticsRecordRepository
from app.schemas.common import PaginatedData
from app.schemas.logistics import (
    LogisticsCostCreate,
    LogisticsCostUpdate,
    LogisticsKanbanItem,
    LogisticsKanbanResponse,
    LogisticsRecordCreate,
    LogisticsRecordListParams,
    LogisticsRecordListRead,
    LogisticsRecordUpdate,
)
from app.utils.code_generator import generate_order_no

# Logistics statuses must progress in order, no skipping or going back
LOGISTICS_STATUS_ORDER = [
    LogisticsStatus.BOOKED,
    LogisticsStatus.CUSTOMS_CLEARED,
    LogisticsStatus.LOADED_ON_SHIP,
    LogisticsStatus.IN_TRANSIT,
    LogisticsStatus.ARRIVED,
    LogisticsStatus.PICKED_UP,
    LogisticsStatus.DELIVERED,
]


class LogisticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LogisticsRecordRepository(db)
        self.container_repo = ContainerPlanRepository(db)

    # ==================== CRUD ====================

    async def create(self, data: LogisticsRecordCreate, user_id: uuid.UUID) -> LogisticsRecord:
        # Get container plan to auto-fill port_of_discharge
        plan = await self.container_repo.get_with_items(data.container_plan_id)
        if not plan:
            raise NotFoundError("排柜计划", str(data.container_plan_id))

        port_of_discharge = data.port_of_discharge or plan.destination_port

        seq = await self.repo.count_by_date(date.today()) + 1
        logistics_no = generate_order_no("LOG", date.today(), seq)

        record = LogisticsRecord(
            logistics_no=logistics_no,
            container_plan_id=data.container_plan_id,
            shipping_company=data.shipping_company,
            vessel_voyage=data.vessel_voyage,
            bl_no=data.bl_no,
            port_of_loading=data.port_of_loading,
            port_of_discharge=port_of_discharge,
            etd=data.etd,
            eta=data.eta,
            actual_departure_date=data.actual_departure_date,
            actual_arrival_date=data.actual_arrival_date,
            status=LogisticsStatus.BOOKED,
            customs_declaration_no=data.customs_declaration_no,
            remark=data.remark,
            created_by=user_id,
            updated_by=user_id,
        )
        record = await self.repo.create(record)
        return await self.get_by_id(record.id)

    async def get_by_id(self, id: uuid.UUID) -> LogisticsRecord:
        record = await self.repo.get_with_costs(id)
        if not record:
            raise NotFoundError("物流记录", str(id))
        return record

    async def update(
        self, id: uuid.UUID, data: LogisticsRecordUpdate, user_id: uuid.UUID
    ) -> LogisticsRecord:
        record = await self.get_by_id(id)

        update_fields = data.model_dump(exclude_unset=True)
        update_fields["updated_by"] = user_id
        for key, value in update_fields.items():
            if value is not None:
                setattr(record, key, value)

        await self.db.flush()
        record_id = record.id
        self.db.expire(record)
        return await self.get_by_id(record_id)

    async def list_records(
        self, params: LogisticsRecordListParams
    ) -> PaginatedData[LogisticsRecordListRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            status=params.status,
            container_plan_id=params.container_plan_id,
            keyword=params.keyword,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[LogisticsRecordListRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    # ==================== Status ====================

    async def update_status(
        self, id: uuid.UUID, new_status: LogisticsStatus, user_id: uuid.UUID
    ) -> LogisticsRecord:
        """R14 & R15: Update logistics status with cascading SO updates."""
        record = await self.get_by_id(id)

        # Validate status transition (must be sequential, forward only)
        current_idx = LOGISTICS_STATUS_ORDER.index(record.status)
        try:
            new_idx = LOGISTICS_STATUS_ORDER.index(new_status)
        except ValueError:
            raise BusinessError(code=42260, message=f"无效的物流状态: {new_status.value}")

        if new_idx <= current_idx:
            raise BusinessError(
                code=42260,
                message=f"物流状态只能前进，不能从 {record.status.value} 退回到 {new_status.value}",
            )

        record.status = new_status
        record.updated_by = user_id
        await self.db.flush()

        # Get container plan and linked SOs
        plan = await self.container_repo.get_with_items(record.container_plan_id)
        if plan:
            so_ids = await self.container_repo.get_linked_so_ids(plan.id)

            # R14: loaded_on_ship → SO shipped, plan shipped
            if new_status == LogisticsStatus.LOADED_ON_SHIP:
                plan.status = ContainerPlanStatus.SHIPPED
                await self.db.flush()
                for so_id in so_ids:
                    result = await self.db.execute(select(SalesOrder).where(SalesOrder.id == so_id))
                    so = result.scalar_one_or_none()
                    if so and so.status == SalesOrderStatus.CONTAINER_LOADED:
                        so.status = SalesOrderStatus.SHIPPED
                        await self.db.flush()

            # R15: delivered → SO delivered
            elif new_status == LogisticsStatus.DELIVERED:
                for so_id in so_ids:
                    result = await self.db.execute(select(SalesOrder).where(SalesOrder.id == so_id))
                    so = result.scalar_one_or_none()
                    if so and so.status == SalesOrderStatus.SHIPPED:
                        so.status = SalesOrderStatus.DELIVERED
                        await self.db.flush()

        record_id = record.id
        self.db.expire(record)
        return await self.get_by_id(record_id)

    # ==================== Costs ====================

    async def add_cost(self, record_id: uuid.UUID, data: LogisticsCostCreate) -> LogisticsCost:
        await self.get_by_id(record_id)

        cost = LogisticsCost(
            logistics_record_id=record_id,
            cost_type=data.cost_type,
            amount=data.amount,
            currency=data.currency,
            remark=data.remark,
        )
        cost = await self.repo.add_cost(cost)

        # Update total_cost
        await self._recalculate_total_cost(record_id)
        return cost

    async def update_cost(
        self, record_id: uuid.UUID, cost_id: uuid.UUID, data: LogisticsCostUpdate
    ) -> LogisticsCost:
        cost = await self.repo.get_cost_by_id(cost_id)
        if not cost or cost.logistics_record_id != record_id:
            raise NotFoundError("费用明细", str(cost_id))

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(cost, key, value)

        await self.db.flush()
        await self.db.refresh(cost)

        await self._recalculate_total_cost(record_id)
        return cost

    async def delete_cost(self, record_id: uuid.UUID, cost_id: uuid.UUID) -> None:
        cost = await self.repo.get_cost_by_id(cost_id)
        if not cost or cost.logistics_record_id != record_id:
            raise NotFoundError("费用明细", str(cost_id))

        await self.repo.delete_cost(cost)
        await self._recalculate_total_cost(record_id)

    # ==================== Kanban ====================

    async def get_kanban(self) -> LogisticsKanbanResponse:
        stats = await self.repo.get_kanban_stats()
        return LogisticsKanbanResponse(
            items=[LogisticsKanbanItem(**s) for s in stats],
        )

    # ==================== Helpers ====================

    async def _recalculate_total_cost(self, record_id: uuid.UUID) -> None:
        # Compute total directly from DB to avoid stale identity map
        from sqlalchemy import func as sa_func

        result = await self.db.execute(
            select(sa_func.coalesce(sa_func.sum(LogisticsCost.amount), 0)).where(
                LogisticsCost.logistics_record_id == record_id
            )
        )
        total = Decimal(str(result.scalar_one()))

        # Use direct UPDATE to avoid identity map staleness
        from sqlalchemy import update

        await self.db.execute(
            update(LogisticsRecord).where(LogisticsRecord.id == record_id).values(total_cost=total)
        )
        await self.db.flush()
