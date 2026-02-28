import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=50)
    address: str | None = None
    supply_categories: list[uuid.UUID] | None = None
    supply_brands: list[str] | None = None
    payment_terms: str | None = None
    business_license: str | None = None
    food_production_license: str | None = None
    certificate_urls: list[str] | None = None
    remark: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    contact_person: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = None
    supply_categories: list[uuid.UUID] | None = None
    supply_brands: list[str] | None = None
    payment_terms: str | None = None
    business_license: str | None = None
    food_production_license: str | None = None
    certificate_urls: list[str] | None = None
    remark: str | None = None


class SupplierRead(BaseModel):
    id: uuid.UUID
    supplier_code: str
    name: str
    contact_person: str
    phone: str
    address: str | None = None
    supply_categories: list[uuid.UUID] | None = None
    supply_brands: list[str] | None = None
    payment_terms: str | None = None
    business_license: str | None = None
    food_production_license: str | None = None
    certificate_urls: list[str] | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierProductCreate(BaseModel):
    product_id: uuid.UUID
    supply_price: Decimal | None = Field(default=None, ge=0)
    remark: str | None = None


class SupplierProductRead(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    product_id: uuid.UUID
    supply_price: Decimal | None = None
    remark: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SupplierListParams(BaseModel):
    keyword: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
