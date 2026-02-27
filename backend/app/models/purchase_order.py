from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base
from app.models.enums import PurchaseOrderStatus, UnitType

if TYPE_CHECKING:
    from app.models.sales_order import SalesOrder

# M2M association table: purchase orders <-> sales orders
purchase_order_sales_orders = Table(
    "purchase_order_sales_orders",
    Base.metadata,
    Column(
        "purchase_order_id", UUID(as_uuid=True), ForeignKey("purchase_orders.id"), primary_key=True
    ),
    Column("sales_order_id", UUID(as_uuid=True), ForeignKey("sales_orders.id"), primary_key=True),
    UniqueConstraint("purchase_order_id", "sales_order_id", name="uq_po_so"),
)


class PurchaseOrder(AuditMixin, Base):
    __tablename__ = "purchase_orders"

    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PurchaseOrderStatus] = mapped_column(
        ENUM(
            PurchaseOrderStatus,
            name="purchase_order_status",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default="draft",
    )
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list[PurchaseOrderItem]] = relationship(
        back_populates="purchase_order", cascade="all, delete-orphan"
    )
    sales_orders: Mapped[list[SalesOrder]] = relationship(
        "SalesOrder", secondary=purchase_order_sales_orders
    )


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    purchase_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    sales_order_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_order_items.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[UnitType] = mapped_column(
        ENUM(
            UnitType,
            name="unit_type",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    purchase_order: Mapped[PurchaseOrder] = relationship(back_populates="items")
