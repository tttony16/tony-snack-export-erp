import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import CurrencyType, LogisticsCostType, LogisticsStatus


# --- Logistics Cost ---
class LogisticsCostCreate(BaseModel):
    cost_type: LogisticsCostType
    amount: Decimal = Field(ge=0)
    currency: CurrencyType
    remark: str | None = None


class LogisticsCostRead(BaseModel):
    id: uuid.UUID
    logistics_record_id: uuid.UUID
    cost_type: LogisticsCostType
    amount: Decimal
    currency: CurrencyType
    remark: str | None

    model_config = {"from_attributes": True}


class LogisticsCostUpdate(BaseModel):
    cost_type: LogisticsCostType | None = None
    amount: Decimal | None = Field(default=None, ge=0)
    currency: CurrencyType | None = None
    remark: str | None = None


# --- Logistics Record ---
class LogisticsRecordCreate(BaseModel):
    container_plan_id: uuid.UUID
    shipping_company: str | None = None
    vessel_voyage: str | None = None
    bl_no: str | None = None
    port_of_loading: str = Field(max_length=200)
    port_of_discharge: str | None = None
    etd: date | None = None
    eta: date | None = None
    actual_departure_date: date | None = None
    actual_arrival_date: date | None = None
    customs_declaration_no: str | None = None
    remark: str | None = None


class LogisticsRecordUpdate(BaseModel):
    shipping_company: str | None = None
    vessel_voyage: str | None = None
    bl_no: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    etd: date | None = None
    eta: date | None = None
    actual_departure_date: date | None = None
    actual_arrival_date: date | None = None
    customs_declaration_no: str | None = None
    remark: str | None = None


class LogisticsRecordRead(BaseModel):
    id: uuid.UUID
    logistics_no: str
    container_plan_id: uuid.UUID
    shipping_company: str | None
    vessel_voyage: str | None
    bl_no: str | None
    port_of_loading: str
    port_of_discharge: str
    etd: date | None
    eta: date | None
    actual_departure_date: date | None
    actual_arrival_date: date | None
    status: LogisticsStatus
    customs_declaration_no: str | None
    total_cost: Decimal
    remark: str | None
    costs: list[LogisticsCostRead]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class LogisticsRecordListRead(BaseModel):
    id: uuid.UUID
    logistics_no: str
    container_plan_id: uuid.UUID
    shipping_company: str | None
    vessel_voyage: str | None
    bl_no: str | None
    port_of_loading: str
    port_of_discharge: str
    etd: date | None
    eta: date | None
    status: LogisticsStatus
    total_cost: Decimal
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class LogisticsRecordListParams(BaseModel):
    status: LogisticsStatus | None = None
    container_plan_id: uuid.UUID | None = None
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class LogisticsStatusUpdate(BaseModel):
    status: LogisticsStatus


class LogisticsKanbanItem(BaseModel):
    status: LogisticsStatus
    count: int
    total_cost: Decimal


class LogisticsKanbanResponse(BaseModel):
    items: list[LogisticsKanbanItem]
