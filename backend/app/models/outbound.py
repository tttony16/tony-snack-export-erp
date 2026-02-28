import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base
from app.models.enums import OutboundOrderStatus


class OutboundOrder(AuditMixin, Base):
    __tablename__ = "outbound_orders"

    order_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    container_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_plans.id"), nullable=False
    )
    status: Mapped[OutboundOrderStatus] = mapped_column(
        ENUM(
            OutboundOrderStatus,
            name="outbound_order_status",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default="draft",
    )
    outbound_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    operator: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["OutboundOrderItem"]] = relationship(
        back_populates="outbound_order", cascade="all, delete-orphan"
    )


class OutboundOrderItem(Base):
    __tablename__ = "outbound_order_items"

    outbound_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("outbound_orders.id"), nullable=False
    )
    container_plan_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_plan_items.id"), nullable=True
    )
    inventory_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_records.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    sales_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    batch_no: Mapped[str] = mapped_column(String(50), nullable=False)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)

    outbound_order: Mapped["OutboundOrder"] = relationship(back_populates="items")
