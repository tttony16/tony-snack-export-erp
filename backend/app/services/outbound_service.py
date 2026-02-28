import math
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessError, NotFoundError
from app.models.container import ContainerPlan
from app.models.enums import ContainerPlanStatus, OutboundOrderStatus
from app.models.outbound import OutboundOrder, OutboundOrderItem
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.warehouse import InventoryRecord
from app.repositories.outbound_repo import OutboundOrderRepository
from app.repositories.warehouse_repo import InventoryRepository
from app.schemas.common import PaginatedData
from app.schemas.outbound import OutboundOrderListParams, OutboundOrderListRead
from app.utils.code_generator import generate_order_no


class OutboundService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OutboundOrderRepository(db)
        self.inventory_repo = InventoryRepository(db)

    async def create_from_container_plan(
        self, container_plan_id: uuid.UUID, user_id: uuid.UUID
    ) -> OutboundOrder:
        """Create an outbound order draft from a LOADED container plan."""
        # 1. Get container plan with items
        result = await self.db.execute(
            select(ContainerPlan)
            .options(selectinload(ContainerPlan.items))
            .where(ContainerPlan.id == container_plan_id)
        )
        plan = result.scalar_one_or_none()
        if not plan:
            raise NotFoundError("排柜计划", str(container_plan_id))

        if plan.status != ContainerPlanStatus.LOADED:
            raise BusinessError(
                code=42270,
                message=f"排柜计划状态为 {plan.status.value}，需为'已装柜'才可创建出库单",
            )

        # 2. Check no existing active outbound order for this plan
        existing = await self.repo.get_by_container_plan(container_plan_id)
        if existing:
            raise BusinessError(
                code=42271,
                message=f"排柜计划已有出库单 {existing.order_no}，不能重复创建",
            )

        # 3. Generate order number
        seq = await self.repo.count_by_date(date.today()) + 1
        order_no = generate_order_no("OUT", date.today(), seq)

        # 4. Create outbound order
        order = OutboundOrder(
            order_no=order_no,
            container_plan_id=container_plan_id,
            status=OutboundOrderStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id,
        )
        order = await self.repo.create(order)

        # 5. Copy items from container plan
        items = []
        for cp_item in plan.items:
            if cp_item.inventory_record_id:
                # Get inventory record for batch info
                inv = await self.inventory_repo.get_by_id(cp_item.inventory_record_id)
                if inv:
                    items.append(
                        OutboundOrderItem(
                            outbound_order_id=order.id,
                            container_plan_item_id=cp_item.id,
                            inventory_record_id=cp_item.inventory_record_id,
                            product_id=cp_item.product_id,
                            sales_order_id=cp_item.sales_order_id,
                            quantity=cp_item.quantity,
                            batch_no=inv.batch_no,
                            production_date=inv.production_date,
                        )
                    )
            else:
                # Legacy items without inventory_record_id - try to find matching inventory
                inv_result = await self.db.execute(
                    select(InventoryRecord)
                    .where(
                        InventoryRecord.product_id == cp_item.product_id,
                        InventoryRecord.sales_order_id == cp_item.sales_order_id,
                    )
                    .limit(1)
                )
                inv = inv_result.scalar_one_or_none()
                batch_no = inv.batch_no if inv else "UNKNOWN"
                prod_date = inv.production_date if inv else date.today()
                inv_id = inv.id if inv else None

                if inv_id:
                    items.append(
                        OutboundOrderItem(
                            outbound_order_id=order.id,
                            container_plan_item_id=cp_item.id,
                            inventory_record_id=inv_id,
                            product_id=cp_item.product_id,
                            sales_order_id=cp_item.sales_order_id,
                            quantity=cp_item.quantity,
                            batch_no=batch_no,
                            production_date=prod_date,
                        )
                    )

        if items:
            await self.repo.add_items(items)

        return await self.repo.get_with_items(order.id)

    async def confirm(
        self,
        order_id: uuid.UUID,
        outbound_date: date,
        operator: str,
        user_id: uuid.UUID,
    ) -> OutboundOrder:
        """Confirm outbound - actually deduct inventory."""
        order = await self.repo.get_with_items(order_id)
        if not order:
            raise NotFoundError("出库单", str(order_id))

        if order.status != OutboundOrderStatus.DRAFT:
            raise BusinessError(code=42272, message="只有草稿状态的出库单可以确认")

        # Deduct inventory for each item
        for item in order.items:
            # Deduct from inventory
            await self.inventory_repo.deduct(item.inventory_record_id, item.quantity)

            # Update SalesOrderItem.outbound_quantity
            if item.sales_order_id:
                so_result = await self.db.execute(
                    select(SalesOrderItem).where(
                        SalesOrderItem.sales_order_id == item.sales_order_id,
                        SalesOrderItem.product_id == item.product_id,
                    )
                )
                so_item = so_result.scalar_one_or_none()
                if so_item:
                    so_item.outbound_quantity += item.quantity
                    await self.db.flush()

        # Update order status
        order.status = OutboundOrderStatus.CONFIRMED
        order.outbound_date = outbound_date
        order.operator = operator
        order.updated_by = user_id
        await self.db.flush()

        return await self.repo.get_with_items(order_id)

    async def cancel(self, order_id: uuid.UUID, user_id: uuid.UUID) -> OutboundOrder:
        """Cancel outbound order (only DRAFT can be cancelled)."""
        order = await self.repo.get_with_items(order_id)
        if not order:
            raise NotFoundError("出库单", str(order_id))

        if order.status != OutboundOrderStatus.DRAFT:
            raise BusinessError(code=42273, message="只有草稿状态的出库单可以取消")

        order.status = OutboundOrderStatus.CANCELLED
        order.updated_by = user_id
        await self.db.flush()

        return await self.repo.get_with_items(order_id)

    async def get_by_id(self, order_id: uuid.UUID) -> OutboundOrder:
        order = await self.repo.get_with_items(order_id)
        if not order:
            raise NotFoundError("出库单", str(order_id))
        return order

    async def list_orders(
        self, params: OutboundOrderListParams
    ) -> PaginatedData[OutboundOrderListRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            status=params.status,
            keyword=params.keyword,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[OutboundOrderListRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )
