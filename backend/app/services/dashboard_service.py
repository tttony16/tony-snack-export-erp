from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    LogisticsStatus,
    PurchaseOrderStatus,
    SalesOrderStatus,
)
from app.models.logistics import LogisticsRecord
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder
from app.models.warehouse import InventoryRecord
from app.repositories.system_config_repo import SystemConfigRepository
from app.schemas.dashboard import (
    ExpiryWarningItem,
    ExpiryWarningResponse,
    InTransitItem,
    InTransitResponse,
    OverviewItem,
    OverviewResponse,
    TodoResponse,
)


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_repo = SystemConfigRepository(db)

    async def get_overview(self) -> OverviewResponse:
        # Sales orders grouped by status
        so_result = await self.db.execute(
            select(
                SalesOrder.status,
                func.count().label("count"),
                func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_amount"),
            ).group_by(SalesOrder.status)
        )
        so_items = [
            OverviewItem(
                status=row.status.value if hasattr(row.status, "value") else str(row.status),
                count=row.count,
                total_amount=Decimal(str(row.total_amount)),
            )
            for row in so_result.all()
        ]

        # Purchase orders grouped by status
        po_result = await self.db.execute(
            select(
                PurchaseOrder.status,
                func.count().label("count"),
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label("total_amount"),
            ).group_by(PurchaseOrder.status)
        )
        po_items = [
            OverviewItem(
                status=row.status.value if hasattr(row.status, "value") else str(row.status),
                count=row.count,
                total_amount=Decimal(str(row.total_amount)),
            )
            for row in po_result.all()
        ]

        return OverviewResponse(sales_orders=so_items, purchase_orders=po_items)

    async def get_todos(self) -> TodoResponse:
        # Draft sales orders
        draft_so = await self.db.execute(
            select(func.count())
            .select_from(SalesOrder)
            .where(SalesOrder.status == SalesOrderStatus.DRAFT)
        )

        # Ordered purchase orders
        ordered_po = await self.db.execute(
            select(func.count())
            .select_from(PurchaseOrder)
            .where(PurchaseOrder.status == PurchaseOrderStatus.ORDERED)
        )

        # Goods ready sales orders
        goods_ready_so = await self.db.execute(
            select(func.count())
            .select_from(SalesOrder)
            .where(SalesOrder.status == SalesOrderStatus.GOODS_READY)
        )

        # Arriving soon: logistics with ETA within 7 days
        seven_days = date.today() + timedelta(days=7)
        arriving_soon = await self.db.execute(
            select(func.count())
            .select_from(LogisticsRecord)
            .where(
                LogisticsRecord.status.in_(
                    [LogisticsStatus.LOADED_ON_SHIP, LogisticsStatus.IN_TRANSIT]
                ),
                LogisticsRecord.eta <= seven_days,
                LogisticsRecord.eta >= date.today(),
            )
        )

        return TodoResponse(
            draft_sales_orders=draft_so.scalar_one(),
            ordered_purchase_orders=ordered_po.scalar_one(),
            goods_ready_sales_orders=goods_ready_so.scalar_one(),
            arriving_soon_containers=arriving_soon.scalar_one(),
        )

    async def get_in_transit(self) -> InTransitResponse:
        result = await self.db.execute(
            select(LogisticsRecord)
            .where(
                LogisticsRecord.status.in_(
                    [
                        LogisticsStatus.LOADED_ON_SHIP,
                        LogisticsStatus.IN_TRANSIT,
                        LogisticsStatus.ARRIVED,
                    ]
                )
            )
            .order_by(LogisticsRecord.created_at.desc())
        )
        records = list(result.scalars().all())
        items = [
            InTransitItem(
                logistics_id=r.id,
                logistics_no=r.logistics_no,
                container_plan_id=r.container_plan_id,
                status=r.status.value if hasattr(r.status, "value") else str(r.status),
                shipping_company=r.shipping_company,
                vessel_voyage=r.vessel_voyage,
                eta=r.eta,
                created_at=r.created_at,
            )
            for r in records
        ]
        return InTransitResponse(items=items, total=len(items))

    async def get_expiry_warnings(self) -> ExpiryWarningResponse:
        # Get threshold from config
        config = await self.config_repo.get_by_key("shelf_life_threshold")
        threshold = float(config.config_value) if config else 0.667

        # Get all inventory records with product info
        result = await self.db.execute(
            select(
                InventoryRecord.product_id,
                InventoryRecord.batch_no,
                InventoryRecord.production_date,
                InventoryRecord.quantity,
                InventoryRecord.sales_order_id,
                Product.shelf_life_days,
                Product.name_cn,
            )
            .join(Product, InventoryRecord.product_id == Product.id)
            .where(InventoryRecord.available_quantity > 0)
        )
        rows = result.all()

        today = date.today()
        items = []
        for row in rows:
            if not row.shelf_life_days or row.shelf_life_days <= 0:
                continue
            elapsed = (today - row.production_date).days
            remaining = row.shelf_life_days - elapsed
            ratio = remaining / row.shelf_life_days if row.shelf_life_days > 0 else 0

            if ratio < threshold:
                items.append(
                    ExpiryWarningItem(
                        product_id=row.product_id,
                        product_name=row.name_cn,
                        batch_no=row.batch_no,
                        production_date=row.production_date,
                        shelf_life_days=row.shelf_life_days,
                        remaining_days=max(remaining, 0),
                        remaining_ratio=round(ratio, 4),
                        sales_order_id=row.sales_order_id,
                        quantity=row.quantity,
                    )
                )

        return ExpiryWarningResponse(threshold=threshold, items=items)
