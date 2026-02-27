import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import ProductCategory, ProductStatus


class ProductCreate(BaseModel):
    sku_code: str = Field(..., min_length=1, max_length=50)
    name_cn: str = Field(..., min_length=1, max_length=200)
    name_en: str = Field(..., min_length=1, max_length=200)
    category: ProductCategory
    brand: str | None = None
    barcode: str | None = None
    spec: str = Field(..., min_length=1, max_length=200)
    unit_weight_kg: Decimal = Field(..., gt=0)
    unit_volume_cbm: Decimal = Field(..., gt=0)
    packing_spec: str = Field(..., min_length=1, max_length=200)
    carton_length_cm: Decimal = Field(..., gt=0)
    carton_width_cm: Decimal = Field(..., gt=0)
    carton_height_cm: Decimal = Field(..., gt=0)
    carton_gross_weight_kg: Decimal = Field(..., gt=0)
    shelf_life_days: int = Field(..., gt=0)
    default_purchase_price: Decimal | None = Field(default=None, ge=0)
    default_supplier_id: uuid.UUID | None = None
    hs_code: str | None = None
    image_url: str | None = None
    remark: str | None = None


class ProductUpdate(BaseModel):
    name_cn: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    category: ProductCategory | None = None
    brand: str | None = None
    barcode: str | None = None
    spec: str | None = Field(default=None, min_length=1, max_length=200)
    unit_weight_kg: Decimal | None = Field(default=None, gt=0)
    unit_volume_cbm: Decimal | None = Field(default=None, gt=0)
    packing_spec: str | None = Field(default=None, min_length=1, max_length=200)
    carton_length_cm: Decimal | None = Field(default=None, gt=0)
    carton_width_cm: Decimal | None = Field(default=None, gt=0)
    carton_height_cm: Decimal | None = Field(default=None, gt=0)
    carton_gross_weight_kg: Decimal | None = Field(default=None, gt=0)
    shelf_life_days: int | None = Field(default=None, gt=0)
    default_purchase_price: Decimal | None = Field(default=None, ge=0)
    default_supplier_id: uuid.UUID | None = None
    hs_code: str | None = None
    image_url: str | None = None
    remark: str | None = None


class ProductRead(BaseModel):
    id: uuid.UUID
    sku_code: str
    name_cn: str
    name_en: str
    category: ProductCategory
    brand: str | None = None
    barcode: str | None = None
    spec: str
    unit_weight_kg: Decimal
    unit_volume_cbm: Decimal
    packing_spec: str
    carton_length_cm: Decimal
    carton_width_cm: Decimal
    carton_height_cm: Decimal
    carton_gross_weight_kg: Decimal
    shelf_life_days: int
    default_purchase_price: Decimal | None = None
    default_supplier_id: uuid.UUID | None = None
    hs_code: str | None = None
    image_url: str | None = None
    status: ProductStatus
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListParams(BaseModel):
    keyword: str | None = None
    category: ProductCategory | None = None
    status: ProductStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class ProductStatusUpdate(BaseModel):
    status: ProductStatus
