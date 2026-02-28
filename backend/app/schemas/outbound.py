import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import OutboundOrderStatus


# --- Outbound Order Item ---
class OutboundOrderItemRead(BaseModel):
    id: uuid.UUID
    outbound_order_id: uuid.UUID
    container_plan_item_id: uuid.UUID | None
    inventory_record_id: uuid.UUID
    product_id: uuid.UUID
    sales_order_id: uuid.UUID | None
    quantity: int
    batch_no: str
    production_date: date

    model_config = {"from_attributes": True}


# --- Outbound Order ---
class OutboundOrderCreate(BaseModel):
    container_plan_id: uuid.UUID


class OutboundOrderConfirm(BaseModel):
    outbound_date: date
    operator: str = Field(max_length=100)


class OutboundOrderRead(BaseModel):
    id: uuid.UUID
    order_no: str
    container_plan_id: uuid.UUID
    status: OutboundOrderStatus
    outbound_date: date | None
    operator: str | None
    remark: str | None
    items: list[OutboundOrderItemRead] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class OutboundOrderListRead(BaseModel):
    id: uuid.UUID
    order_no: str
    container_plan_id: uuid.UUID
    status: OutboundOrderStatus
    outbound_date: date | None
    operator: str | None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class OutboundOrderListParams(BaseModel):
    status: OutboundOrderStatus | None = None
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
