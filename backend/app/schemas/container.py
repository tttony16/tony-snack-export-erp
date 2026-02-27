import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import ContainerPlanStatus, ContainerType


# --- Container Plan Item ---
class ContainerPlanItemCreate(BaseModel):
    container_seq: int = Field(ge=1)
    product_id: uuid.UUID
    sales_order_id: uuid.UUID
    quantity: int = Field(gt=0)
    volume_cbm: Decimal = Field(ge=0)
    weight_kg: Decimal = Field(ge=0)


class ContainerPlanItemRead(BaseModel):
    id: uuid.UUID
    container_plan_id: uuid.UUID
    container_seq: int
    product_id: uuid.UUID
    sales_order_id: uuid.UUID
    quantity: int
    volume_cbm: Decimal
    weight_kg: Decimal

    model_config = {"from_attributes": True}


class ContainerPlanItemUpdate(BaseModel):
    container_seq: int | None = None
    quantity: int | None = Field(default=None, gt=0)
    volume_cbm: Decimal | None = None
    weight_kg: Decimal | None = None


# --- Container Plan ---
class ContainerPlanCreate(BaseModel):
    sales_order_ids: list[uuid.UUID] = Field(min_length=1)
    container_type: ContainerType
    container_count: int = Field(default=1, ge=1)
    destination_port: str | None = None
    remark: str | None = None


class ContainerPlanUpdate(BaseModel):
    container_type: ContainerType | None = None
    container_count: int | None = Field(default=None, ge=1)
    destination_port: str | None = None
    remark: str | None = None


class ContainerPlanRead(BaseModel):
    id: uuid.UUID
    plan_no: str
    container_type: ContainerType
    container_count: int
    destination_port: str
    status: ContainerPlanStatus
    remark: str | None
    items: list[ContainerPlanItemRead]
    linked_sales_order_ids: list[uuid.UUID]
    stuffing_records: list["ContainerStuffingRecordRead"] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContainerPlanListRead(BaseModel):
    id: uuid.UUID
    plan_no: str
    container_type: ContainerType
    container_count: int
    destination_port: str
    status: ContainerPlanStatus
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContainerPlanListParams(BaseModel):
    status: ContainerPlanStatus | None = None
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# --- Container Summary ---
class ContainerSummaryItem(BaseModel):
    container_seq: int
    loaded_volume_cbm: Decimal
    volume_utilization: Decimal
    loaded_weight_kg: Decimal
    weight_utilization: Decimal
    is_over_volume: bool
    is_over_weight: bool
    item_count: int


class ContainerSummaryResponse(BaseModel):
    items: list[ContainerSummaryItem]


# --- Container Type Recommendation ---
class ContainerRecommendation(BaseModel):
    container_type: str
    count: int
    volume_utilization: Decimal
    weight_utilization: Decimal


class ContainerRecommendationResponse(BaseModel):
    total_volume_cbm: Decimal
    total_weight_kg: Decimal
    recommendations: list[ContainerRecommendation]


# --- Stuffing Record ---
class ContainerStuffingCreate(BaseModel):
    container_seq: int = Field(ge=1)
    container_no: str = Field(max_length=20)
    seal_no: str = Field(max_length=20)
    stuffing_date: date
    stuffing_location: str | None = None
    remark: str | None = None


class ContainerStuffingRecordRead(BaseModel):
    id: uuid.UUID
    container_plan_id: uuid.UUID
    container_seq: int
    container_no: str
    seal_no: str
    stuffing_date: date
    stuffing_location: str | None
    remark: str | None
    photos: list["ContainerStuffingPhotoRead"] = []

    model_config = {"from_attributes": True}


# --- Stuffing Photo ---
class ContainerStuffingPhotoCreate(BaseModel):
    photo_url: str = Field(max_length=500)
    description: str | None = None


class ContainerStuffingPhotoRead(BaseModel):
    id: uuid.UUID
    stuffing_record_id: uuid.UUID
    photo_url: str
    description: str | None

    model_config = {"from_attributes": True}


# --- Validation ---
class ContainerValidationResponse(BaseModel):
    is_valid: bool
    errors: list[dict] = []
    warnings: list[dict] = []
