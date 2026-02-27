import math
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessError, NotFoundError
from app.models.container import (
    ContainerPlan,
    ContainerPlanItem,
    ContainerStuffingPhoto,
    ContainerStuffingRecord,
)
from app.models.enums import ContainerPlanStatus, SalesOrderStatus
from app.models.sales_order import SalesOrder
from app.repositories.container_repo import ContainerPlanRepository
from app.repositories.warehouse_repo import InventoryRepository
from app.schemas.common import PaginatedData
from app.schemas.container import (
    ContainerPlanCreate,
    ContainerPlanItemCreate,
    ContainerPlanItemUpdate,
    ContainerPlanListParams,
    ContainerPlanListRead,
    ContainerPlanUpdate,
    ContainerRecommendation,
    ContainerRecommendationResponse,
    ContainerStuffingCreate,
    ContainerSummaryItem,
    ContainerSummaryResponse,
    ContainerValidationResponse,
)
from app.services.container_calculator import CONTAINER_SPECS, recommend_container_type
from app.utils.code_generator import generate_order_no

VALID_TRANSITIONS: dict[ContainerPlanStatus, set[ContainerPlanStatus]] = {
    ContainerPlanStatus.PLANNING: {ContainerPlanStatus.CONFIRMED},
    ContainerPlanStatus.CONFIRMED: {ContainerPlanStatus.LOADING},
    ContainerPlanStatus.LOADING: {ContainerPlanStatus.LOADED},
    ContainerPlanStatus.LOADED: {ContainerPlanStatus.SHIPPED},
    ContainerPlanStatus.SHIPPED: set(),
}


class ContainerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ContainerPlanRepository(db)
        self.inventory_repo = InventoryRepository(db)

    # ==================== CRUD ====================

    async def create(self, data: ContainerPlanCreate, user_id: uuid.UUID) -> ContainerPlan:
        # R04: validate all linked SOs are goods_ready
        destination_ports = set()
        for so_id in data.sales_order_ids:
            result = await self.db.execute(select(SalesOrder).where(SalesOrder.id == so_id))
            so = result.scalar_one_or_none()
            if not so:
                raise NotFoundError("销售订单", str(so_id))
            if so.status != SalesOrderStatus.GOODS_READY:
                raise BusinessError(
                    code=42250,
                    message=f"订单 {so.order_no} 状态为 {so.status.value}，需为'已到齐'才可排柜",
                )
            destination_ports.add(so.destination_port)

        # R08: validate destination port consistency
        if len(destination_ports) > 1:
            raise BusinessError(
                code=42253,
                message=f"合柜的销售订单目的港不一致: {', '.join(destination_ports)}",
            )

        destination_port = data.destination_port or destination_ports.pop()

        seq = await self.repo.count_by_date(date.today()) + 1
        plan_no = generate_order_no("CL", date.today(), seq)

        plan = ContainerPlan(
            plan_no=plan_no,
            container_type=data.container_type,
            container_count=data.container_count,
            destination_port=destination_port,
            status=ContainerPlanStatus.PLANNING,
            remark=data.remark,
            created_by=user_id,
            updated_by=user_id,
        )
        plan = await self.repo.create(plan)

        # Link sales orders
        await self.repo.link_sales_orders(plan.id, data.sales_order_ids)

        plan_id = plan.id
        self.db.expire(plan)
        return await self.get_by_id(plan_id)

    async def get_by_id(self, id: uuid.UUID) -> ContainerPlan:
        plan = await self.repo.get_with_items(id)
        if not plan:
            raise NotFoundError("排柜计划", str(id))
        return plan

    async def update(
        self, id: uuid.UUID, data: ContainerPlanUpdate, user_id: uuid.UUID
    ) -> ContainerPlan:
        plan = await self.get_by_id(id)
        if plan.status != ContainerPlanStatus.PLANNING:
            raise BusinessError(code=42254, message="只有规划中状态的排柜计划可以编辑")

        update_fields = data.model_dump(exclude_unset=True)
        update_fields["updated_by"] = user_id
        for key, value in update_fields.items():
            if value is not None:
                setattr(plan, key, value)

        await self.db.flush()
        plan_id = plan.id
        self.db.expire(plan)
        return await self.get_by_id(plan_id)

    async def list_plans(
        self, params: ContainerPlanListParams
    ) -> PaginatedData[ContainerPlanListRead]:
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
            items=[ContainerPlanListRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )

    # ==================== Items ====================

    async def add_item(
        self, plan_id: uuid.UUID, data: ContainerPlanItemCreate
    ) -> ContainerPlanItem:
        plan = await self.get_by_id(plan_id)
        if plan.status != ContainerPlanStatus.PLANNING:
            raise BusinessError(code=42254, message="只有规划中状态可以添加配载明细")

        if data.container_seq > plan.container_count:
            raise BusinessError(
                code=42255,
                message=f"柜序号 {data.container_seq} 超过柜数量 {plan.container_count}",
            )

        # R05: Check inventory availability
        available = await self.inventory_repo.get_available_quantity(
            data.product_id, data.sales_order_id
        )
        # Subtract already allocated to other container items for this product+SO
        existing_items = await self.repo.get_items_by_plan(plan_id)
        already_allocated = sum(
            item.quantity
            for item in existing_items
            if item.product_id == data.product_id and item.sales_order_id == data.sales_order_id
        )
        actual_available = available - already_allocated
        if data.quantity > actual_available:
            raise BusinessError(
                code=42260,
                message=f"库存不足：可用 {actual_available}，请求 {data.quantity}",
                detail={
                    "product_id": str(data.product_id),
                    "available": actual_available,
                    "requested": data.quantity,
                },
            )

        item = ContainerPlanItem(
            container_plan_id=plan_id,
            container_seq=data.container_seq,
            product_id=data.product_id,
            sales_order_id=data.sales_order_id,
            quantity=data.quantity,
            volume_cbm=data.volume_cbm,
            weight_kg=data.weight_kg,
        )
        return await self.repo.add_item(item)

    async def update_item(
        self, plan_id: uuid.UUID, item_id: uuid.UUID, data: ContainerPlanItemUpdate
    ) -> ContainerPlanItem:
        plan = await self.get_by_id(plan_id)
        if plan.status != ContainerPlanStatus.PLANNING:
            raise BusinessError(code=42254, message="只有规划中状态可以编辑配载明细")

        item = await self.repo.get_item_by_id(item_id)
        if not item or item.container_plan_id != plan_id:
            raise NotFoundError("配载明细", str(item_id))

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(item, key, value)

        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def delete_item(self, plan_id: uuid.UUID, item_id: uuid.UUID) -> None:
        plan = await self.get_by_id(plan_id)
        if plan.status != ContainerPlanStatus.PLANNING:
            raise BusinessError(code=42254, message="只有规划中状态可以删除配载明细")

        item = await self.repo.get_item_by_id(item_id)
        if not item or item.container_plan_id != plan_id:
            raise NotFoundError("配载明细", str(item_id))
        await self.repo.delete_item(item)

    # ==================== Summary & Validation ====================

    async def get_summary(self, plan_id: uuid.UUID) -> ContainerSummaryResponse:
        plan = await self.get_by_id(plan_id)
        spec = CONTAINER_SPECS[plan.container_type.value]
        items = await self.repo.get_items_by_plan(plan_id)

        summaries: dict[int, dict] = {}
        for item in items:
            seq = item.container_seq
            if seq not in summaries:
                summaries[seq] = {"volume": Decimal("0"), "weight": Decimal("0"), "count": 0}
            summaries[seq]["volume"] += Decimal(str(item.volume_cbm))
            summaries[seq]["weight"] += Decimal(str(item.weight_kg))
            summaries[seq]["count"] += 1

        result = []
        for seq in range(1, plan.container_count + 1):
            data = summaries.get(seq, {"volume": Decimal("0"), "weight": Decimal("0"), "count": 0})
            vol = data["volume"]
            wt = data["weight"]
            result.append(
                ContainerSummaryItem(
                    container_seq=seq,
                    loaded_volume_cbm=round(vol, 3),
                    volume_utilization=(
                        round(vol / spec["volume_cbm"] * 100, 1)
                        if spec["volume_cbm"]
                        else Decimal("0")
                    ),
                    loaded_weight_kg=round(wt, 3),
                    weight_utilization=(
                        round(wt / spec["max_weight_kg"] * 100, 1)
                        if spec["max_weight_kg"]
                        else Decimal("0")
                    ),
                    is_over_volume=vol > spec["volume_cbm"],
                    is_over_weight=wt > spec["max_weight_kg"],
                    item_count=data["count"],
                )
            )
        return ContainerSummaryResponse(items=result)

    async def validate(self, plan_id: uuid.UUID) -> ContainerValidationResponse:
        """R06-R09: Validate the loading plan."""
        from app.models.product import Product
        from app.models.warehouse import InventoryRecord
        from app.repositories.system_config_repo import SystemConfigRepository

        plan = await self.get_by_id(plan_id)
        spec = CONTAINER_SPECS[plan.container_type.value]
        items = await self.repo.get_items_by_plan(plan_id)

        errors = []
        warnings = []

        # Group by container_seq
        seq_data: dict[int, dict] = {}
        for item in items:
            seq = item.container_seq
            if seq not in seq_data:
                seq_data[seq] = {"volume": Decimal("0"), "weight": Decimal("0")}
            seq_data[seq]["volume"] += Decimal(str(item.volume_cbm))
            seq_data[seq]["weight"] += Decimal(str(item.weight_kg))

        for seq, data in seq_data.items():
            # R06: volume check
            if data["volume"] > spec["volume_cbm"]:
                errors.append(
                    {
                        "code": 42251,
                        "container_seq": seq,
                        "field": "volume",
                        "message": f"柜{seq} 体积 {data['volume']} CBM 超过限制 {spec['volume_cbm']} CBM",
                    }
                )
            # R07: weight check
            if data["weight"] > spec["max_weight_kg"]:
                errors.append(
                    {
                        "code": 42252,
                        "container_seq": seq,
                        "field": "weight",
                        "message": f"柜{seq} 重量 {data['weight']} KG 超过限制 {spec['max_weight_kg']} KG",
                    }
                )

        # R09: Shelf life warning check
        config_repo = SystemConfigRepository(self.db)
        config = await config_repo.get_by_key("shelf_life_threshold")
        threshold = float(config.config_value) if config else 0.667

        today = date.today()
        for item in items:
            # Get product shelf_life_days
            product_result = await self.db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalar_one_or_none()
            if not product or not product.shelf_life_days:
                continue

            # Check inventory records for this product+sales_order
            inv_result = await self.db.execute(
                select(InventoryRecord).where(
                    InventoryRecord.product_id == item.product_id,
                    InventoryRecord.sales_order_id == item.sales_order_id,
                    InventoryRecord.available_quantity > 0,
                )
            )
            for inv in inv_result.scalars().all():
                elapsed = (today - inv.production_date).days
                remaining = product.shelf_life_days - elapsed
                ratio = remaining / product.shelf_life_days if product.shelf_life_days > 0 else 0
                if ratio < threshold:
                    warnings.append(
                        {
                            "code": 42253,
                            "product_id": str(item.product_id),
                            "batch_no": inv.batch_no,
                            "remaining_days": max(remaining, 0),
                            "remaining_ratio": round(ratio, 4),
                            "message": f"商品 {product.name_cn} 批次 {inv.batch_no} 保质期剩余 {max(remaining, 0)} 天 ({round(ratio * 100, 1)}%)，低于阈值 {round(threshold * 100, 1)}%",
                        }
                    )
                    break  # One warning per item is enough

        return ContainerValidationResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    async def recommend_type(self, plan_id: uuid.UUID) -> ContainerRecommendationResponse:
        await self.get_by_id(plan_id)
        items = await self.repo.get_items_by_plan(plan_id)

        total_volume = sum(Decimal(str(item.volume_cbm)) for item in items)
        total_weight = sum(Decimal(str(item.weight_kg)) for item in items)

        if total_volume == 0 and total_weight == 0:
            # Calculate from linked SO items if no items yet
            so_ids = await self.repo.get_linked_so_ids(plan_id)
            for so_id in so_ids:
                result = await self.db.execute(
                    select(SalesOrder)
                    .options(selectinload(SalesOrder.items))
                    .where(SalesOrder.id == so_id)
                )
                so = result.scalar_one_or_none()
                if so:
                    total_volume += Decimal(str(so.estimated_volume_cbm or 0))
                    total_weight += Decimal(str(so.estimated_weight_kg or 0))

        recs = recommend_container_type(total_volume, total_weight)
        return ContainerRecommendationResponse(
            total_volume_cbm=total_volume,
            total_weight_kg=total_weight,
            recommendations=[ContainerRecommendation(**r) for r in recs],
        )

    # ==================== Confirm & Stuffing ====================

    async def confirm(self, plan_id: uuid.UUID, user_id: uuid.UUID) -> ContainerPlan:
        """R12: Confirm plan → update linked SOs to container_planned."""
        plan = await self.get_by_id(plan_id)
        if plan.status != ContainerPlanStatus.PLANNING:
            raise BusinessError(code=42256, message="只有规划中的排柜计划可以确认")

        # Validate first
        validation = await self.validate(plan_id)
        if not validation.is_valid:
            raise BusinessError(
                code=42251,
                message="配载方案校验不通过",
                detail={"errors": validation.errors},
            )

        plan.status = ContainerPlanStatus.CONFIRMED
        plan.updated_by = user_id
        await self.db.flush()

        # R12: update linked SOs to container_planned
        so_ids = await self.repo.get_linked_so_ids(plan_id)
        for so_id in so_ids:
            result = await self.db.execute(select(SalesOrder).where(SalesOrder.id == so_id))
            so = result.scalar_one_or_none()
            if so and so.status == SalesOrderStatus.GOODS_READY:
                so.status = SalesOrderStatus.CONTAINER_PLANNED
                await self.db.flush()

        plan_id_val = plan.id
        self.db.expire(plan)
        return await self.get_by_id(plan_id_val)

    async def record_stuffing(
        self, plan_id: uuid.UUID, data: ContainerStuffingCreate, user_id: uuid.UUID
    ) -> ContainerStuffingRecord:
        """R13: Record stuffing. When all containers stuffed → update SO to container_loaded."""
        plan = await self.get_by_id(plan_id)
        if plan.status not in (ContainerPlanStatus.CONFIRMED, ContainerPlanStatus.LOADING):
            raise BusinessError(code=42257, message="只有已确认或装柜中的排柜计划可以录入装柜记录")

        if data.container_seq > plan.container_count:
            raise BusinessError(
                code=42255,
                message=f"柜序号 {data.container_seq} 超过柜数量 {plan.container_count}",
            )

        # Check if already stuffed
        existing = await self.repo.get_stuffing_record_by_seq(plan_id, data.container_seq)
        if existing:
            raise BusinessError(
                code=42258,
                message=f"柜{data.container_seq} 已有装柜记录",
            )

        # Update plan status to loading if not already
        if plan.status == ContainerPlanStatus.CONFIRMED:
            plan.status = ContainerPlanStatus.LOADING
            plan.updated_by = user_id
            await self.db.flush()

        record = ContainerStuffingRecord(
            container_plan_id=plan_id,
            container_seq=data.container_seq,
            container_no=data.container_no,
            seal_no=data.seal_no,
            stuffing_date=data.stuffing_date,
            stuffing_location=data.stuffing_location,
            remark=data.remark,
            created_by=user_id,
            updated_by=user_id,
        )
        record = await self.repo.add_stuffing_record(record)

        # Check if all containers are stuffed
        all_records = await self.repo.get_stuffing_records(plan_id)
        if len(all_records) >= plan.container_count:
            # All stuffed → R13: update plan to loaded, SOs to container_loaded
            plan.status = ContainerPlanStatus.LOADED
            plan.updated_by = user_id
            await self.db.flush()

            so_ids = await self.repo.get_linked_so_ids(plan_id)
            for so_id in so_ids:
                result = await self.db.execute(select(SalesOrder).where(SalesOrder.id == so_id))
                so = result.scalar_one_or_none()
                if so and so.status == SalesOrderStatus.CONTAINER_PLANNED:
                    so.status = SalesOrderStatus.CONTAINER_LOADED
                    await self.db.flush()

        return record

    async def add_stuffing_photo(
        self, plan_id: uuid.UUID, photo_url: str, description: str | None = None
    ) -> ContainerStuffingPhoto:
        await self.get_by_id(plan_id)
        records = await self.repo.get_stuffing_records(plan_id)
        if not records:
            raise BusinessError(code=42259, message="请先录入装柜记录再上传照片")

        # Add photo to the latest stuffing record
        latest_record = records[-1]
        photo = ContainerStuffingPhoto(
            stuffing_record_id=latest_record.id,
            photo_url=photo_url,
            description=description,
        )
        return await self.repo.add_stuffing_photo(photo)

    async def get_packing_list(self, plan_id: uuid.UUID) -> dict:
        """Generate packing list data (501 stub for actual export)."""
        plan = await self.get_by_id(plan_id)
        items = await self.repo.get_items_by_plan(plan_id)
        so_ids = await self.repo.get_linked_so_ids(plan_id)

        return {
            "plan_no": plan.plan_no,
            "container_type": plan.container_type.value,
            "container_count": plan.container_count,
            "destination_port": plan.destination_port,
            "sales_order_ids": [str(sid) for sid in so_ids],
            "items": [
                {
                    "container_seq": item.container_seq,
                    "product_id": str(item.product_id),
                    "sales_order_id": str(item.sales_order_id),
                    "quantity": item.quantity,
                    "volume_cbm": str(item.volume_cbm),
                    "weight_kg": str(item.weight_kg),
                }
                for item in items
            ],
        }
