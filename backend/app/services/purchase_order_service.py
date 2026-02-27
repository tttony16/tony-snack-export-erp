import math
import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.enums import PurchaseOrderStatus
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.schemas.common import PaginatedData
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderListParams,
    PurchaseOrderListRead,
    PurchaseOrderUpdate,
)
from app.utils.code_generator import generate_order_no


class PurchaseOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PurchaseOrderRepository(db)

    async def create(self, data: PurchaseOrderCreate, user_id: uuid.UUID) -> PurchaseOrder:
        seq = await self.repo.count_by_date(data.order_date) + 1
        order_no = generate_order_no("PO", data.order_date, seq)

        # R02: validate purchased quantity does not exceed demand
        for item_data in data.items:
            if item_data.sales_order_item_id:
                so_item = await self.repo.get_sales_order_item(item_data.sales_order_item_id)
                if not so_item:
                    raise NotFoundError("销售订单明细", str(item_data.sales_order_item_id))
                remaining = so_item.quantity - so_item.purchased_quantity
                if item_data.quantity > remaining:
                    raise BusinessError(
                        code=42230,
                        message=f"采购数量 {item_data.quantity} 超过未采购需求 {remaining}",
                        detail={
                            "sales_order_item_id": str(item_data.sales_order_item_id),
                            "requested": item_data.quantity,
                            "remaining": remaining,
                        },
                    )

        order = PurchaseOrder(
            order_no=order_no,
            supplier_id=data.supplier_id,
            order_date=data.order_date,
            required_date=data.required_date,
            remark=data.remark,
            status=PurchaseOrderStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id,
        )

        for item_data in data.items:
            amount = Decimal(str(item_data.quantity)) * item_data.unit_price
            order.items.append(
                PurchaseOrderItem(
                    product_id=item_data.product_id,
                    sales_order_item_id=item_data.sales_order_item_id,
                    quantity=item_data.quantity,
                    unit=item_data.unit,
                    unit_price=item_data.unit_price,
                    amount=amount,
                )
            )

        self._calculate_total(order)
        order = await self.repo.create(order)

        # R01: link to sales orders if provided
        if data.sales_order_ids:
            await self.repo.link_sales_orders(order.id, data.sales_order_ids)

        # Update SO items' purchased_quantity
        for item_data in data.items:
            if item_data.sales_order_item_id:
                so_item = await self.repo.get_sales_order_item(item_data.sales_order_item_id)
                if so_item:
                    so_item.purchased_quantity += item_data.quantity
                    await self.db.flush()

        # Save ID before expiring, then re-fetch with eager loads
        order_id = order.id
        self.db.expire(order)
        return await self.get_by_id(order_id)

    async def get_by_id(self, id: uuid.UUID) -> PurchaseOrder:
        order = await self.repo.get_with_items(id)
        if not order:
            raise NotFoundError("采购单", str(id))
        return order

    async def update(
        self, id: uuid.UUID, data: PurchaseOrderUpdate, user_id: uuid.UUID
    ) -> PurchaseOrder:
        order = await self.get_by_id(id)

        if order.status != PurchaseOrderStatus.DRAFT:
            raise BusinessError(code=42220, message="只有草稿状态的采购单可以编辑")

        update_fields = data.model_dump(exclude_unset=True, exclude={"items"})
        update_fields["updated_by"] = user_id

        for key, value in update_fields.items():
            if value is not None:
                setattr(order, key, value)

        if data.items is not None:
            # Rollback old purchased_quantity before replacing items
            old_items = await self.repo.delete_items(order.id)
            for old_item in old_items:
                if old_item.sales_order_item_id:
                    so_item = await self.repo.get_sales_order_item(old_item.sales_order_item_id)
                    if so_item:
                        so_item.purchased_quantity -= old_item.quantity
                        await self.db.flush()

            # R02 re-validate + create new items
            order.items = []
            for item_data in data.items:
                if item_data.sales_order_item_id:
                    so_item = await self.repo.get_sales_order_item(item_data.sales_order_item_id)
                    if not so_item:
                        raise NotFoundError("销售订单明细", str(item_data.sales_order_item_id))
                    remaining = so_item.quantity - so_item.purchased_quantity
                    if item_data.quantity > remaining:
                        raise BusinessError(
                            code=42230,
                            message=f"采购数量 {item_data.quantity} 超过未采购需求 {remaining}",
                        )

                amount = Decimal(str(item_data.quantity)) * item_data.unit_price
                order.items.append(
                    PurchaseOrderItem(
                        purchase_order_id=order.id,
                        product_id=item_data.product_id,
                        sales_order_item_id=item_data.sales_order_item_id,
                        quantity=item_data.quantity,
                        unit=item_data.unit,
                        unit_price=item_data.unit_price,
                        amount=amount,
                    )
                )

            # Update SO items' purchased_quantity for new items
            for item_data in data.items:
                if item_data.sales_order_item_id:
                    so_item = await self.repo.get_sales_order_item(item_data.sales_order_item_id)
                    if so_item:
                        so_item.purchased_quantity += item_data.quantity
                        await self.db.flush()

            self._calculate_total(order)

        await self.db.flush()
        await self.db.refresh(order)
        return await self.get_by_id(order.id)

    async def confirm(self, id: uuid.UUID, user_id: uuid.UUID) -> PurchaseOrder:
        order = await self.get_by_id(id)
        if order.status != PurchaseOrderStatus.DRAFT:
            raise BusinessError(code=42221, message="只有草稿状态的采购单可以确认")

        order.status = PurchaseOrderStatus.ORDERED
        order.updated_by = user_id
        await self.db.flush()
        order_id = order.id
        self.db.expire(order)
        return await self.get_by_id(order_id)

    async def cancel(self, id: uuid.UUID, user_id: uuid.UUID) -> PurchaseOrder:
        order = await self.get_by_id(id)
        if order.status not in (PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.ORDERED):
            raise BusinessError(code=42222, message="只有草稿或已下单状态的采购单可以取消")

        # Rollback purchased_quantity on SO items
        for item in order.items:
            if item.sales_order_item_id:
                so_item = await self.repo.get_sales_order_item(item.sales_order_item_id)
                if so_item:
                    so_item.purchased_quantity = max(0, so_item.purchased_quantity - item.quantity)
                    await self.db.flush()

        order.status = PurchaseOrderStatus.CANCELLED
        order.updated_by = user_id
        await self.db.flush()
        order_id = order.id
        self.db.expire(order)
        return await self.get_by_id(order_id)

    async def link_sales_orders(self, id: uuid.UUID, so_ids: list[uuid.UUID]) -> PurchaseOrder:
        order = await self.get_by_id(id)
        await self.repo.link_sales_orders(order.id, so_ids)
        # Expire cached state so get_by_id re-loads M2M relationships
        order_id = order.id
        self.db.expire(order)
        return await self.get_by_id(order_id)

    async def list_orders(
        self, params: PurchaseOrderListParams
    ) -> PaginatedData[PurchaseOrderListRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            keyword=params.keyword,
            status=params.status,
            supplier_id=params.supplier_id,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[PurchaseOrderListRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    def _calculate_total(self, order: PurchaseOrder) -> None:
        order.total_amount = (
            sum(item.amount for item in order.items) if order.items else Decimal("0")
        )
