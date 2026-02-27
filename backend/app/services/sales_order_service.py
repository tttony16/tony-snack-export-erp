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

    async def generate_purchase_orders(self, so_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """Generate purchase orders from a sales order, grouped by default_supplier_id."""
        from sqlalchemy import select

        from app.models.product import Product
        from app.services.purchase_order_service import PurchaseOrderService

        order = await self.get_by_id(so_id)
        if order.status not in (SalesOrderStatus.PURCHASING, SalesOrderStatus.DRAFT):
            raise BusinessError(code=42213, message="只有草稿或采购中状态的订单可以生成采购单")

        # Group items by supplier
        supplier_items: dict[uuid.UUID | None, list] = {}
        for item in order.items:
            result = await self.db.execute(select(Product).where(Product.id == item.product_id))
            product = result.scalar_one_or_none()
            supplier_id = product.default_supplier_id if product else None
            if supplier_id not in supplier_items:
                supplier_items[supplier_id] = []
            supplier_items[supplier_id].append((item, product))

        po_service = PurchaseOrderService(self.db)
        created_pos = []

        for supplier_id, items_with_products in supplier_items.items():
            if not supplier_id:
                continue  # Skip items without supplier

            from datetime import date

            from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderItemCreate

            po_items = []
            for so_item, product in items_with_products:
                remaining = so_item.quantity - so_item.purchased_quantity
                if remaining <= 0:
                    continue
                po_items.append(
                    PurchaseOrderItemCreate(
                        product_id=so_item.product_id,
                        sales_order_item_id=so_item.id,
                        quantity=remaining,
                        unit=so_item.unit,
                        unit_price=Decimal(
                            str(product.default_purchase_price or so_item.unit_price)
                        ),
                    )
                )

            if not po_items:
                continue

            po_data = PurchaseOrderCreate(
                supplier_id=supplier_id,
                order_date=date.today(),
                sales_order_ids=[so_id],
                items=po_items,
            )
            po = await po_service.create(po_data, user_id)
            created_pos.append(str(po.id))

        return {
            "sales_order_id": str(so_id),
            "created_purchase_orders": created_pos,
            "count": len(created_pos),
        }

    async def get_fulfillment(self, so_id: uuid.UUID) -> dict:
        """Get fulfillment chain: SO → PO → Receiving Notes → Inventory → Container → Logistics."""
        from sqlalchemy import select

        from app.models.container import (
            ContainerPlan,
            container_plan_sales_orders,
        )
        from app.models.logistics import LogisticsRecord
        from app.models.purchase_order import PurchaseOrder, purchase_order_sales_orders
        from app.models.warehouse import InventoryRecord, ReceivingNote

        order = await self.get_by_id(so_id)

        # Get linked POs
        po_result = await self.db.execute(
            select(PurchaseOrder)
            .join(
                purchase_order_sales_orders,
                PurchaseOrder.id == purchase_order_sales_orders.c.purchase_order_id,
            )
            .where(purchase_order_sales_orders.c.sales_order_id == so_id)
        )
        pos = list(po_result.scalars().all())

        # Get receiving notes for those POs
        receiving_notes = []
        for po in pos:
            rn_result = await self.db.execute(
                select(ReceivingNote).where(ReceivingNote.purchase_order_id == po.id)
            )
            for rn in rn_result.scalars().all():
                receiving_notes.append(
                    {
                        "id": str(rn.id),
                        "note_no": rn.note_no,
                        "purchase_order_id": str(po.id),
                        "receiving_date": str(rn.receiving_date),
                    }
                )

        # Get inventory records
        inv_result = await self.db.execute(
            select(InventoryRecord).where(InventoryRecord.sales_order_id == so_id)
        )
        inventory = [
            {
                "product_id": str(r.product_id),
                "batch_no": r.batch_no,
                "quantity": r.quantity,
                "available_quantity": r.available_quantity,
            }
            for r in inv_result.scalars().all()
        ]

        # Get container plans
        cp_result = await self.db.execute(
            select(ContainerPlan)
            .join(
                container_plan_sales_orders,
                ContainerPlan.id == container_plan_sales_orders.c.container_plan_id,
            )
            .where(container_plan_sales_orders.c.sales_order_id == so_id)
        )
        containers = [
            {
                "id": str(cp.id),
                "plan_no": cp.plan_no,
                "container_type": cp.container_type.value,
                "status": cp.status.value,
            }
            for cp in cp_result.scalars().all()
        ]

        # Get logistics for those containers
        logistics = []
        for cp_data in containers:
            lr_result = await self.db.execute(
                select(LogisticsRecord).where(LogisticsRecord.container_plan_id == cp_data["id"])
            )
            for lr in lr_result.scalars().all():
                logistics.append(
                    {
                        "id": str(lr.id),
                        "logistics_no": lr.logistics_no,
                        "container_plan_id": cp_data["id"],
                        "status": lr.status.value,
                        "eta": str(lr.eta) if lr.eta else None,
                    }
                )

        return {
            "sales_order_id": str(so_id),
            "order_no": order.order_no,
            "status": order.status.value,
            "purchase_orders": [
                {"id": str(po.id), "order_no": po.order_no, "status": po.status.value} for po in pos
            ],
            "receiving_notes": receiving_notes,
            "inventory": inventory,
            "containers": containers,
            "logistics": logistics,
        }

    def _calculate_totals(self, order: SalesOrder) -> None:
        order.total_amount = (
            sum(item.amount for item in order.items) if order.items else Decimal("0")
        )
        order.total_quantity = sum(item.quantity for item in order.items) if order.items else 0
