import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base
from app.models.enums import (
    CurrencyType,
    PaymentMethod,
    SalesOrderStatus,
    TradeTerm,
    UnitType,
)


class SalesOrder(AuditMixin, Base):
    __tablename__ = "sales_orders"

    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    destination_port: Mapped[str] = mapped_column(String(200), nullable=False)
    trade_term: Mapped[TradeTerm] = mapped_column(
        ENUM(
            TradeTerm,
            name="trade_term",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    currency: Mapped[CurrencyType] = mapped_column(
        ENUM(
            CurrencyType,
            name="currency_type",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        ENUM(
            PaymentMethod,
            name="payment_method",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    payment_terms: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[SalesOrderStatus] = mapped_column(
        ENUM(
            SalesOrderStatus,
            name="sales_order_status",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default="draft",
    )
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    estimated_volume_cbm: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    estimated_weight_kg: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["SalesOrderItem"]] = relationship(
        back_populates="sales_order", cascade="all, delete-orphan"
    )


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    sales_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
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
    purchased_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    outbound_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    sales_order: Mapped["SalesOrder"] = relationship(back_populates="items")
