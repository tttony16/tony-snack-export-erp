import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class OverviewItem(BaseModel):
    status: str
    count: int
    total_amount: Decimal


class OverviewResponse(BaseModel):
    sales_orders: list[OverviewItem]
    purchase_orders: list[OverviewItem]


class TodoResponse(BaseModel):
    draft_sales_orders: int
    ordered_purchase_orders: int
    goods_ready_sales_orders: int
    arriving_soon_containers: int


class InTransitItem(BaseModel):
    logistics_id: uuid.UUID
    logistics_no: str
    container_plan_id: uuid.UUID
    status: str
    shipping_company: str | None = None
    vessel_voyage: str | None = None
    eta: date | None = None
    created_at: datetime | None = None


class InTransitResponse(BaseModel):
    items: list[InTransitItem]
    total: int


class ExpiryWarningItem(BaseModel):
    product_id: uuid.UUID
    product_name: str | None = None
    batch_no: str
    production_date: date
    shelf_life_days: int
    remaining_days: int
    remaining_ratio: float
    sales_order_id: uuid.UUID | None = None
    quantity: int


class ExpiryWarningResponse(BaseModel):
    threshold: float
    items: list[ExpiryWarningItem]
