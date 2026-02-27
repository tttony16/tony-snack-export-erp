import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.enums import PurchaseOrderStatus, SalesOrderStatus
from app.models.warehouse import InventoryRecord, ReceivingNote, ReceivingNoteItem
from app.repositories.warehouse_repo import InventoryRepository, ReceivingNoteRepository
from app.schemas.common import PaginatedData
from app.schemas.warehouse import (
    InventoryByOrderRead,
    InventoryByProductRead,
    InventoryListParams,
    ReadinessCheckResponse,
    ReceivingNoteCreate,
    ReceivingNoteListParams,
    ReceivingNoteListRead,
    ReceivingNoteUpdate,
)
from app.utils.code_generator import generate_order_no


class WarehouseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.note_repo = ReceivingNoteRepository(db)
        self.inventory_repo = InventoryRepository(db)

    # ==================== Receiving Notes ====================

    async def create_receiving_note(
        self, data: ReceivingNoteCreate, user_id: uuid.UUID
    ) -> ReceivingNote:
        seq = await self.note_repo.count_by_date(data.receiving_date) + 1
        note_no = generate_order_no("RCV", data.receiving_date, seq)

        # R03: validate actual_quantity does not exceed remaining on PO item
        for item_data in data.items:
            po_item = await self.note_repo.get_purchase_order_item(item_data.purchase_order_item_id)
            if not po_item:
                raise NotFoundError("采购单明细", str(item_data.purchase_order_item_id))
            remaining = po_item.quantity - po_item.received_quantity
            if item_data.actual_quantity > remaining:
                raise BusinessError(
                    code=42240,
                    message=f"实收数量 {item_data.actual_quantity} 超过未到货数量 {remaining}",
                    detail={
                        "purchase_order_item_id": str(item_data.purchase_order_item_id),
                        "actual_quantity": item_data.actual_quantity,
                        "remaining": remaining,
                    },
                )

        note = ReceivingNote(
            note_no=note_no,
            purchase_order_id=data.purchase_order_id,
            receiving_date=data.receiving_date,
            receiver=data.receiver,
            remark=data.remark,
            created_by=user_id,
            updated_by=user_id,
        )

        # Build items + generate batch_no
        for item_data in data.items:
            batch_no = f"{note_no}-{item_data.product_id.hex[:8]}"
            note.items.append(
                ReceivingNoteItem(
                    purchase_order_item_id=item_data.purchase_order_item_id,
                    product_id=item_data.product_id,
                    expected_quantity=item_data.expected_quantity,
                    actual_quantity=item_data.actual_quantity,
                    inspection_result=item_data.inspection_result,
                    failed_quantity=item_data.failed_quantity,
                    failure_reason=item_data.failure_reason,
                    production_date=item_data.production_date,
                    batch_no=batch_no,
                    remark=item_data.remark,
                )
            )

        note = await self.note_repo.create(note)

        # Re-fetch with eager loading to access items
        note = await self.note_repo.get_with_items(note.id)

        # Post-create: update PO item received_quantity + create inventory records
        for item in note.items:
            await self._update_po_item_received(item)
            await self._create_inventory_record(item, data.purchase_order_id)

        # R11: check if all goods for related SOs are received
        await self._check_and_update_so_status(data.purchase_order_id)

        # Update PO status based on received quantities
        await self._update_po_status(data.purchase_order_id)

        return await self.get_receiving_note(note.id)

    async def get_receiving_note(self, id: uuid.UUID) -> ReceivingNote:
        note = await self.note_repo.get_with_items(id)
        if not note:
            raise NotFoundError("收货单", str(id))
        return note

    async def update_receiving_note(
        self, id: uuid.UUID, data: ReceivingNoteUpdate, user_id: uuid.UUID
    ) -> ReceivingNote:
        note = await self.get_receiving_note(id)

        update_fields = data.model_dump(exclude_unset=True, exclude={"items"})
        update_fields["updated_by"] = user_id
        for key, value in update_fields.items():
            if value is not None:
                setattr(note, key, value)

        await self.db.flush()
        await self.db.refresh(note)
        return await self.get_receiving_note(note.id)

    async def list_receiving_notes(
        self, params: ReceivingNoteListParams
    ) -> PaginatedData[ReceivingNoteListRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.note_repo.search(
            purchase_order_id=params.purchase_order_id,
            keyword=params.keyword,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[ReceivingNoteListRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    # ==================== Inventory ====================

    async def get_inventory_by_product(
        self, params: InventoryListParams
    ) -> PaginatedData[InventoryByProductRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.inventory_repo.get_by_product(
            product_id=params.product_id, offset=offset, limit=params.page_size
        )
        return PaginatedData(
            items=[InventoryByProductRead(**item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    async def get_inventory_by_order(self, sales_order_id: uuid.UUID) -> list[InventoryByOrderRead]:
        items = await self.inventory_repo.get_by_sales_order(sales_order_id)
        return [InventoryByOrderRead(**item) for item in items]

    async def check_readiness(self, sales_order_id: uuid.UUID) -> ReadinessCheckResponse:
        """Check if all goods for a sales order are received and passed inspection."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.models.sales_order import SalesOrder

        result = await self.db.execute(
            select(SalesOrder)
            .options(selectinload(SalesOrder.items))
            .where(SalesOrder.id == sales_order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError("销售订单", str(sales_order_id))

        item_statuses = []
        all_ready = True
        for so_item in order.items:
            received = so_item.received_quantity
            needed = so_item.quantity
            ready = received >= needed
            if not ready:
                all_ready = False
            item_statuses.append(
                {
                    "product_id": str(so_item.product_id),
                    "needed": needed,
                    "received": received,
                    "is_ready": ready,
                }
            )

        return ReadinessCheckResponse(
            sales_order_id=sales_order_id,
            is_ready=all_ready,
            items=item_statuses,
        )

    # ==================== Internal Helpers ====================

    async def _update_po_item_received(self, note_item: ReceivingNoteItem) -> None:
        """Update PO item's received_quantity."""
        po_item = await self.note_repo.get_purchase_order_item(note_item.purchase_order_item_id)
        if po_item:
            po_item.received_quantity += note_item.actual_quantity
            await self.db.flush()

    async def _create_inventory_record(
        self, note_item: ReceivingNoteItem, purchase_order_id: uuid.UUID
    ) -> None:
        """Create inventory record for passed/partial-passed items."""
        from app.models.enums import InspectionResult

        if note_item.inspection_result == InspectionResult.FAILED:
            return  # no inventory for fully failed items

        # Determine the sales_order_id via PO item -> SO item chain
        sales_order_id = None
        po_item = await self.note_repo.get_purchase_order_item(note_item.purchase_order_item_id)
        if po_item and po_item.sales_order_item_id:
            from sqlalchemy import select

            from app.models.sales_order import SalesOrderItem

            result = await self.db.execute(
                select(SalesOrderItem).where(SalesOrderItem.id == po_item.sales_order_item_id)
            )
            so_item = result.scalar_one_or_none()
            if so_item:
                sales_order_id = so_item.sales_order_id
                # Update SO item received_quantity
                qualified_qty = note_item.actual_quantity - note_item.failed_quantity
                so_item.received_quantity += qualified_qty
                await self.db.flush()

        qualified_qty = note_item.actual_quantity - note_item.failed_quantity
        if qualified_qty <= 0:
            return

        record = InventoryRecord(
            product_id=note_item.product_id,
            sales_order_id=sales_order_id,
            receiving_note_item_id=note_item.id,
            batch_no=note_item.batch_no,
            production_date=note_item.production_date,
            quantity=qualified_qty,
            available_quantity=qualified_qty,
        )
        self.db.add(record)
        await self.db.flush()

    async def _check_and_update_so_status(self, purchase_order_id: uuid.UUID) -> None:
        """R11: If all goods for a sales order are received, update SO to goods_ready."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.models.purchase_order import purchase_order_sales_orders
        from app.models.sales_order import SalesOrder

        # Get linked sales order IDs
        result = await self.db.execute(
            select(purchase_order_sales_orders.c.sales_order_id).where(
                purchase_order_sales_orders.c.purchase_order_id == purchase_order_id
            )
        )
        so_ids = [row[0] for row in result.all()]

        for so_id in so_ids:
            result = await self.db.execute(
                select(SalesOrder)
                .options(selectinload(SalesOrder.items))
                .where(SalesOrder.id == so_id)
            )
            order = result.scalar_one_or_none()
            if not order or order.status != SalesOrderStatus.PURCHASING:
                continue

            # Check if all items have received_quantity >= quantity
            all_received = all(item.received_quantity >= item.quantity for item in order.items)
            if all_received:
                order.status = SalesOrderStatus.GOODS_READY
                await self.db.flush()

    async def _update_po_status(self, purchase_order_id: uuid.UUID) -> None:
        """Update PO status based on received quantities."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.models.purchase_order import PurchaseOrder

        result = await self.db.execute(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(PurchaseOrder.id == purchase_order_id)
        )
        po = result.scalar_one_or_none()
        if not po or po.status not in (
            PurchaseOrderStatus.ORDERED,
            PurchaseOrderStatus.PARTIAL_RECEIVED,
        ):
            return

        all_received = all(item.received_quantity >= item.quantity for item in po.items)
        some_received = any(item.received_quantity > 0 for item in po.items)

        if all_received:
            po.status = PurchaseOrderStatus.FULLY_RECEIVED
        elif some_received:
            po.status = PurchaseOrderStatus.PARTIAL_RECEIVED
        await self.db.flush()
