import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import InspectionResult


# --- Receiving Note Item ---
class ReceivingNoteItemCreate(BaseModel):
    purchase_order_item_id: uuid.UUID
    product_id: uuid.UUID
    expected_quantity: int = Field(ge=0)
    actual_quantity: int = Field(ge=0)
    inspection_result: InspectionResult
    failed_quantity: int = Field(default=0, ge=0)
    failure_reason: str | None = None
    production_date: date
    remark: str | None = None


class ReceivingNoteItemRead(BaseModel):
    id: uuid.UUID
    receiving_note_id: uuid.UUID
    purchase_order_item_id: uuid.UUID
    product_id: uuid.UUID
    expected_quantity: int
    actual_quantity: int
    inspection_result: InspectionResult
    failed_quantity: int
    failure_reason: str | None
    production_date: date
    batch_no: str
    remark: str | None

    model_config = {"from_attributes": True}


# --- Receiving Note ---
class ReceivingNoteCreate(BaseModel):
    purchase_order_id: uuid.UUID
    receiving_date: date
    receiver: str = Field(max_length=100)
    remark: str | None = None
    items: list[ReceivingNoteItemCreate] = Field(min_length=1)


class ReceivingNoteUpdate(BaseModel):
    receiving_date: date | None = None
    receiver: str | None = None
    remark: str | None = None
    items: list[ReceivingNoteItemCreate] | None = None


class ReceivingNoteRead(BaseModel):
    id: uuid.UUID
    note_no: str
    purchase_order_id: uuid.UUID
    receiving_date: date
    receiver: str
    remark: str | None
    items: list[ReceivingNoteItemRead]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReceivingNoteListRead(BaseModel):
    id: uuid.UUID
    note_no: str
    purchase_order_id: uuid.UUID
    receiving_date: date
    receiver: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReceivingNoteListParams(BaseModel):
    purchase_order_id: uuid.UUID | None = None
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# --- Inventory ---
class InventoryRecordRead(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    sales_order_id: uuid.UUID | None
    receiving_note_item_id: uuid.UUID
    batch_no: str
    production_date: date
    quantity: int
    available_quantity: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class InventoryByProductRead(BaseModel):
    product_id: uuid.UUID
    total_quantity: int
    available_quantity: int


class InventoryByOrderRead(BaseModel):
    sales_order_id: uuid.UUID
    product_id: uuid.UUID
    total_quantity: int
    available_quantity: int


class InventoryListParams(BaseModel):
    product_id: uuid.UUID | None = None
    sales_order_id: uuid.UUID | None = None
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class ReadinessCheckResponse(BaseModel):
    sales_order_id: uuid.UUID
    is_ready: bool
    items: list[dict]
