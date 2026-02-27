import math
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.enums import SalesOrderStatus
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.repositories.sales_order_repo import SalesOrderRepository
from app.schemas.common import PaginatedData
from app.schemas.sales_order import (
    KanbanItem,
    KanbanResponse,
    SalesOrderCreate,
    SalesOrderListParams,
    SalesOrderListRead,
    SalesOrderUpdate,
)
from app.utils.code_generator import generate_order_no

# R10: confirm goes directly to purchasing (skip confirmed)
VALID_TRANSITIONS: dict[SalesOrderStatus, set[SalesOrderStatus]] = {
    SalesOrderStatus.DRAFT: {SalesOrderStatus.PURCHASING, SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.PURCHASING: {SalesOrderStatus.GOODS_READY, SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.GOODS_READY: {SalesOrderStatus.CONTAINER_PLANNED, SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.CONTAINER_PLANNED: {
        SalesOrderStatus.CONTAINER_LOADED,
        SalesOrderStatus.ABNORMAL,
    },
    SalesOrderStatus.CONTAINER_LOADED: {SalesOrderStatus.SHIPPED, SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.SHIPPED: {SalesOrderStatus.DELIVERED, SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.DELIVERED: {SalesOrderStatus.COMPLETED, SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.COMPLETED: {SalesOrderStatus.ABNORMAL},
    SalesOrderStatus.ABNORMAL: set(),
}


class SalesOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SalesOrderRepository(db)

    async def create(self, data: SalesOrderCreate, user_id: uuid.UUID) -> SalesOrder:
        seq = await self.repo.count_by_date(data.order_date) + 1
        order_no = generate_order_no("SO", data.order_date, seq)

        order = SalesOrder(
            order_no=order_no,
            customer_id=data.customer_id,
            order_date=data.order_date,
            required_delivery_date=data.required_delivery_date,
            destination_port=data.destination_port,
            trade_term=data.trade_term,
            currency=data.currency,
            payment_method=data.payment_method,
            payment_terms=data.payment_terms,
            estimated_volume_cbm=data.estimated_volume_cbm,
            estimated_weight_kg=data.estimated_weight_kg,
            remark=data.remark,
            status=SalesOrderStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id,
        )

        # Build items
        for item_data in data.items:
            amount = Decimal(str(item_data.quantity)) * item_data.unit_price
            order.items.append(
                SalesOrderItem(
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    unit=item_data.unit,
                    unit_price=item_data.unit_price,
                    amount=amount,
                )
            )

        self._calculate_totals(order)
        order = await self.repo.create(order)
        return await self.get_by_id(order.id)

    async def get_by_id(self, id: uuid.UUID) -> SalesOrder:
        order = await self.repo.get_with_items(id)
        if not order:
            raise NotFoundError("销售订单", str(id))
        return order

    async def update(self, id: uuid.UUID, data: SalesOrderUpdate, user_id: uuid.UUID) -> SalesOrder:
        order = await self.get_by_id(id)

        if order.status not in (SalesOrderStatus.DRAFT, SalesOrderStatus.PURCHASING):
            raise BusinessError(code=42210, message="只有草稿或采购中状态的订单可以编辑")

        update_fields = data.model_dump(exclude_unset=True, exclude={"items"})
        update_fields["updated_by"] = user_id

        for key, value in update_fields.items():
            if value is not None:
                setattr(order, key, value)

        # Replace items if provided
        if data.items is not None:
            await self.repo.delete_items(order.id)
            order.items = []
            for item_data in data.items:
                amount = Decimal(str(item_data.quantity)) * item_data.unit_price
                order.items.append(
                    SalesOrderItem(
                        sales_order_id=order.id,
                        product_id=item_data.product_id,
                        quantity=item_data.quantity,
                        unit=item_data.unit,
                        unit_price=item_data.unit_price,
                        amount=amount,
                    )
                )
            self._calculate_totals(order)

        await self.db.flush()
        await self.db.refresh(order)
        return await self.get_by_id(order.id)

    async def confirm(self, id: uuid.UUID, user_id: uuid.UUID) -> SalesOrder:
        """R10: confirm directly sets status to purchasing (skip confirmed)."""
        order = await self.get_by_id(id)
        if order.status != SalesOrderStatus.DRAFT:
            raise BusinessError(code=42211, message="只有草稿状态的订单可以确认")

        order.status = SalesOrderStatus.PURCHASING
        order.updated_by = user_id
        await self.db.flush()
        await self.db.refresh(order)
        return await self.get_by_id(order.id)

    async def update_status(
        self, id: uuid.UUID, new_status: SalesOrderStatus, user_id: uuid.UUID
    ) -> SalesOrder:
        order = await self.get_by_id(id)
        valid = VALID_TRANSITIONS.get(order.status, set())
        if new_status not in valid:
            raise BusinessError(
                code=42212,
                message=f"不允许从 {order.status.value} 转为 {new_status.value}",
            )

        order.status = new_status
        order.updated_by = user_id
        await self.db.flush()
        await self.db.refresh(order)
        return await self.get_by_id(order.id)

    async def list_orders(self, params: SalesOrderListParams) -> PaginatedData[SalesOrderListRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            keyword=params.keyword,
            status=params.status,
            customer_id=params.customer_id,
            date_from=params.date_from,
            date_to=params.date_to,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[SalesOrderListRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    async def get_kanban(self) -> KanbanResponse:
        stats = await self.repo.get_kanban_stats()
        return KanbanResponse(
            items=[KanbanItem(**s) for s in stats],
        )

    def _calculate_totals(self, order: SalesOrder) -> None:
        order.total_amount = (
            sum(item.amount for item in order.items) if order.items else Decimal("0")
        )
        order.total_quantity = sum(item.quantity for item in order.items) if order.items else 0
