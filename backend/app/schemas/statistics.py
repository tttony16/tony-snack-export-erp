from decimal import Decimal

from pydantic import BaseModel


class SalesSummaryItem(BaseModel):
    group_key: str
    order_count: int
    total_amount: Decimal


class SalesSummaryResponse(BaseModel):
    items: list[SalesSummaryItem]


class PurchaseSummaryItem(BaseModel):
    group_key: str
    order_count: int
    total_amount: Decimal


class PurchaseSummaryResponse(BaseModel):
    items: list[PurchaseSummaryItem]


class ContainerSummaryStatItem(BaseModel):
    group_key: str
    plan_count: int
    container_count: int


class ContainerSummaryStatResponse(BaseModel):
    items: list[ContainerSummaryStatItem]


class CustomerRankingItem(BaseModel):
    customer_id: str
    customer_name: str | None = None
    order_count: int
    total_amount: Decimal


class CustomerRankingResponse(BaseModel):
    items: list[CustomerRankingItem]


class ProductRankingItem(BaseModel):
    product_id: str
    product_name: str | None = None
    total_quantity: int
    total_amount: Decimal


class ProductRankingResponse(BaseModel):
    items: list[ProductRankingItem]
