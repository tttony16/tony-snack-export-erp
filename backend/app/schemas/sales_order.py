import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import (
    CurrencyType,
    PaymentMethod,
    SalesOrderStatus,
    TradeTerm,
    UnitType,
)

# --- Item schemas ---


class SalesOrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)
    unit: UnitType
    unit_price: Decimal = Field(..., ge=0)


class SalesOrderItemRead(BaseModel):
    id: uuid.UUID
    sales_order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit: UnitType
    unit_price: Decimal
    amount: Decimal
    purchased_quantity: int
    received_quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Order schemas ---


class SalesOrderCreate(BaseModel):
    customer_id: uuid.UUID
    order_date: date
    required_delivery_date: date | None = None
    destination_port: str = Field(..., min_length=1, max_length=200)
    trade_term: TradeTerm
    currency: CurrencyType
    payment_method: PaymentMethod
    payment_terms: str | None = None
    estimated_volume_cbm: Decimal | None = None
    estimated_weight_kg: Decimal | None = None
    remark: str | None = None
    items: list[SalesOrderItemCreate] = Field(..., min_length=1)


class SalesOrderUpdate(BaseModel):
    customer_id: uuid.UUID | None = None
    order_date: date | None = None
    required_delivery_date: date | None = None
    destination_port: str | None = Field(default=None, min_length=1, max_length=200)
    trade_term: TradeTerm | None = None
    currency: CurrencyType | None = None
    payment_method: PaymentMethod | None = None
    payment_terms: str | None = None
    estimated_volume_cbm: Decimal | None = None
    estimated_weight_kg: Decimal | None = None
    remark: str | None = None
    items: list[SalesOrderItemCreate] | None = None


class SalesOrderRead(BaseModel):
    id: uuid.UUID
    order_no: str
    customer_id: uuid.UUID
    order_date: date
    required_delivery_date: date | None = None
    destination_port: str
    trade_term: TradeTerm
    currency: CurrencyType
    payment_method: PaymentMethod
    payment_terms: str | None = None
    status: SalesOrderStatus
    total_amount: Decimal
    total_quantity: int
    estimated_volume_cbm: Decimal | None = None
    estimated_weight_kg: Decimal | None = None
    remark: str | None = None
    items: list[SalesOrderItemRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesOrderListRead(BaseModel):
    id: uuid.UUID
    order_no: str
    customer_id: uuid.UUID
    order_date: date
    required_delivery_date: date | None = None
    destination_port: str
    trade_term: TradeTerm
    currency: CurrencyType
    payment_method: PaymentMethod
    status: SalesOrderStatus
    total_amount: Decimal
    total_quantity: int
    purchase_progress: float | None = None
    arrival_progress: float | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesOrderListParams(BaseModel):
    keyword: str | None = None
    status: SalesOrderStatus | None = None
    customer_id: uuid.UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class SalesOrderStatusUpdate(BaseModel):
    status: SalesOrderStatus


class KanbanItem(BaseModel):
    status: SalesOrderStatus
    count: int
    total_amount: Decimal

    model_config = {"from_attributes": True}


class KanbanResponse(BaseModel):
    items: list[KanbanItem]
