from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.container import ContainerPlan
from app.models.customer import Customer
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.schemas.statistics import (
    ContainerSummaryStatItem,
    ContainerSummaryStatResponse,
    CustomerRankingItem,
    CustomerRankingResponse,
    ProductRankingItem,
    ProductRankingResponse,
    PurchaseSummaryItem,
    PurchaseSummaryResponse,
    SalesSummaryItem,
    SalesSummaryResponse,
)


class StatisticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def sales_summary(
        self,
        group_by: str = "month",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> SalesSummaryResponse:
        filters = []
        if date_from:
            filters.append(SalesOrder.order_date >= datetime.fromisoformat(date_from).date())
        if date_to:
            filters.append(SalesOrder.order_date <= datetime.fromisoformat(date_to).date())

        if group_by == "customer":
            group_col = sa.cast(SalesOrder.customer_id, sa.String).label("group_key")
            query = (
                select(
                    group_col,
                    func.count().label("order_count"),
                    func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_amount"),
                )
                .group_by(SalesOrder.customer_id)
                .order_by(func.sum(SalesOrder.total_amount).desc())
            )
        else:
            group_col = func.to_char(SalesOrder.order_date, sa.literal("YYYY-MM")).label(
                "group_key"
            )
            query = (
                select(
                    group_col,
                    func.count().label("order_count"),
                    func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_amount"),
                )
                .group_by(group_col)
                .order_by(group_col)
            )

        for f in filters:
            query = query.where(f)

        result = await self.db.execute(query)
        items = [
            SalesSummaryItem(
                group_key=str(row.group_key),
                order_count=row.order_count,
                total_amount=Decimal(str(row.total_amount)),
            )
            for row in result.all()
        ]
        return SalesSummaryResponse(items=items)

    async def purchase_summary(
        self,
        group_by: str = "month",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> PurchaseSummaryResponse:
        filters = []
        if date_from:
            filters.append(PurchaseOrder.order_date >= datetime.fromisoformat(date_from).date())
        if date_to:
            filters.append(PurchaseOrder.order_date <= datetime.fromisoformat(date_to).date())

        if group_by == "supplier":
            group_col = sa.cast(PurchaseOrder.supplier_id, sa.String).label("group_key")
            query = (
                select(
                    group_col,
                    func.count().label("order_count"),
                    func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label("total_amount"),
                )
                .group_by(PurchaseOrder.supplier_id)
                .order_by(func.sum(PurchaseOrder.total_amount).desc())
            )
        else:
            group_col = func.to_char(PurchaseOrder.order_date, sa.literal("YYYY-MM")).label(
                "group_key"
            )
            query = (
                select(
                    group_col,
                    func.count().label("order_count"),
                    func.coalesce(func.sum(PurchaseOrder.total_amount), 0).label("total_amount"),
                )
                .group_by(group_col)
                .order_by(group_col)
            )

        for f in filters:
            query = query.where(f)

        result = await self.db.execute(query)
        items = [
            PurchaseSummaryItem(
                group_key=str(row.group_key),
                order_count=row.order_count,
                total_amount=Decimal(str(row.total_amount)),
            )
            for row in result.all()
        ]
        return PurchaseSummaryResponse(items=items)

    async def container_summary(
        self,
        group_by: str = "month",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> ContainerSummaryStatResponse:
        filters = []
        if date_from:
            filters.append(ContainerPlan.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            filters.append(
                ContainerPlan.created_at <= datetime.fromisoformat(date_to + "T23:59:59")
            )

        if group_by == "container_type":
            group_col = sa.cast(ContainerPlan.container_type, sa.String).label("group_key")
            query = (
                select(
                    group_col,
                    func.count().label("plan_count"),
                    func.coalesce(func.sum(ContainerPlan.container_count), 0).label(
                        "container_count"
                    ),
                )
                .group_by(ContainerPlan.container_type)
                .order_by(func.count().desc())
            )
        else:
            group_col = func.to_char(ContainerPlan.created_at, sa.literal("YYYY-MM")).label(
                "group_key"
            )
            query = (
                select(
                    group_col,
                    func.count().label("plan_count"),
                    func.coalesce(func.sum(ContainerPlan.container_count), 0).label(
                        "container_count"
                    ),
                )
                .group_by(group_col)
                .order_by(group_col)
            )

        for f in filters:
            query = query.where(f)

        result = await self.db.execute(query)
        items = [
            ContainerSummaryStatItem(
                group_key=str(row.group_key),
                plan_count=row.plan_count,
                container_count=int(row.container_count),
            )
            for row in result.all()
        ]
        return ContainerSummaryStatResponse(items=items)

    async def customer_ranking(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        top_n: int = 20,
    ) -> CustomerRankingResponse:
        filters = []
        if date_from:
            filters.append(SalesOrder.order_date >= datetime.fromisoformat(date_from).date())
        if date_to:
            filters.append(SalesOrder.order_date <= datetime.fromisoformat(date_to).date())

        query = (
            select(
                sa.cast(SalesOrder.customer_id, sa.String).label("customer_id"),
                Customer.name.label("customer_name"),
                func.count().label("order_count"),
                func.coalesce(func.sum(SalesOrder.total_amount), 0).label("total_amount"),
            )
            .join(Customer, SalesOrder.customer_id == Customer.id)
            .group_by(SalesOrder.customer_id, Customer.name)
            .order_by(func.sum(SalesOrder.total_amount).desc())
            .limit(top_n)
        )

        for f in filters:
            query = query.where(f)

        result = await self.db.execute(query)
        items = [
            CustomerRankingItem(
                customer_id=str(row.customer_id),
                customer_name=row.customer_name,
                order_count=row.order_count,
                total_amount=Decimal(str(row.total_amount)),
            )
            for row in result.all()
        ]
        return CustomerRankingResponse(items=items)

    async def product_ranking(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
        top_n: int = 20,
    ) -> ProductRankingResponse:
        filters = []
        if date_from:
            filters.append(SalesOrder.order_date >= datetime.fromisoformat(date_from).date())
        if date_to:
            filters.append(SalesOrder.order_date <= datetime.fromisoformat(date_to).date())

        query = (
            select(
                sa.cast(SalesOrderItem.product_id, sa.String).label("product_id"),
                Product.name_cn.label("product_name"),
                func.coalesce(func.sum(SalesOrderItem.quantity), 0).label("total_quantity"),
                func.coalesce(func.sum(SalesOrderItem.amount), 0).label("total_amount"),
            )
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .join(Product, SalesOrderItem.product_id == Product.id)
            .group_by(SalesOrderItem.product_id, Product.name_cn)
            .order_by(func.sum(SalesOrderItem.amount).desc())
            .limit(top_n)
        )

        for f in filters:
            query = query.where(f)

        result = await self.db.execute(query)
        items = [
            ProductRankingItem(
                product_id=str(row.product_id),
                product_name=row.product_name,
                total_quantity=int(row.total_quantity),
                total_amount=Decimal(str(row.total_amount)),
            )
            for row in result.all()
        ]
        return ProductRankingResponse(items=items)
