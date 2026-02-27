import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CurrencyType, PaymentMethod, TradeTerm


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    short_name: str | None = None
    country: str = Field(..., min_length=1, max_length=100)
    address: str | None = None
    contact_person: str = Field(..., min_length=1, max_length=100)
    phone: str | None = None
    email: str | None = None
    currency: CurrencyType
    payment_method: PaymentMethod
    payment_terms: str | None = None
    trade_term: TradeTerm | None = None
    remark: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    short_name: str | None = None
    country: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = None
    contact_person: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = None
    email: str | None = None
    currency: CurrencyType | None = None
    payment_method: PaymentMethod | None = None
    payment_terms: str | None = None
    trade_term: TradeTerm | None = None
    remark: str | None = None


class CustomerRead(BaseModel):
    id: uuid.UUID
    customer_code: str
    name: str
    short_name: str | None = None
    country: str
    address: str | None = None
    contact_person: str
    phone: str | None = None
    email: str | None = None
    currency: CurrencyType
    payment_method: PaymentMethod
    payment_terms: str | None = None
    trade_term: TradeTerm | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerListParams(BaseModel):
    keyword: str | None = None
    country: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
