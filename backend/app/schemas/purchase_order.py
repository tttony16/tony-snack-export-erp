import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import PurchaseOrderStatus, UnitType

# --- Item schemas ---


class PurchaseOrderItemCreate(BaseModel):
    product_id: uuid.UUID
    sales_order_item_id: uuid.UUID | None = None
    quantity: int = Field(..., gt=0)
    unit: UnitType
    unit_price: Decimal = Field(..., ge=0)


class PurchaseOrderItemRead(BaseModel):
    id: uuid.UUID
    purchase_order_id: uuid.UUID
    product_id: uuid.UUID
    sales_order_item_id: uuid.UUID | None = None
    quantity: int
    unit: UnitType
    unit_price: Decimal
    amount: Decimal
    received_quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Order schemas ---


class PurchaseOrderCreate(BaseModel):
    supplier_id: uuid.UUID
    order_date: date
    required_date: date | None = None
    remark: str | None = None
    sales_order_ids: list[uuid.UUID] = Field(default_factory=list)
    items: list[PurchaseOrderItemCreate] = Field(..., min_length=1)


class PurchaseOrderUpdate(BaseModel):
    supplier_id: uuid.UUID | None = None
    order_date: date | None = None
    required_date: date | None = None
    remark: str | None = None
    items: list[PurchaseOrderItemCreate] | None = None


class PurchaseOrderRead(BaseModel):
    id: uuid.UUID
    order_no: str
    supplier_id: uuid.UUID
    order_date: date
    required_date: date | None = None
    status: PurchaseOrderStatus
    total_amount: Decimal
    remark: str | None = None
    items: list[PurchaseOrderItemRead] = []
    linked_sales_order_ids: list[uuid.UUID] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PurchaseOrderListRead(BaseModel):
    id: uuid.UUID
    order_no: str
    supplier_id: uuid.UUID
    order_date: date
    required_date: date | None = None
    status: PurchaseOrderStatus
    total_amount: Decimal
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PurchaseOrderListParams(BaseModel):
    keyword: str | None = None
    status: PurchaseOrderStatus | None = None
    supplier_id: uuid.UUID | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class LinkSalesOrdersRequest(BaseModel):
    sales_order_ids: list[uuid.UUID] = Field(..., min_length=1)
