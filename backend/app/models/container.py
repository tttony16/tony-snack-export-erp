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
from app.models.enums import ContainerPlanStatus, ContainerType

if TYPE_CHECKING:
    from app.models.sales_order import SalesOrder

# M2M association table: container plans <-> sales orders
container_plan_sales_orders = Table(
    "container_plan_sales_orders",
    Base.metadata,
    Column(
        "container_plan_id", UUID(as_uuid=True), ForeignKey("container_plans.id"), primary_key=True
    ),
    Column("sales_order_id", UUID(as_uuid=True), ForeignKey("sales_orders.id"), primary_key=True),
    UniqueConstraint("container_plan_id", "sales_order_id", name="uq_cp_so"),
)


class ContainerPlan(AuditMixin, Base):
    __tablename__ = "container_plans"

    plan_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    container_type: Mapped[ContainerType] = mapped_column(
        ENUM(
            ContainerType,
            name="container_type",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    container_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    destination_port: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[ContainerPlanStatus] = mapped_column(
        ENUM(
            ContainerPlanStatus,
            name="container_plan_status",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default="planning",
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list[ContainerPlanItem]] = relationship(
        back_populates="container_plan", cascade="all, delete-orphan"
    )
    stuffing_records: Mapped[list[ContainerStuffingRecord]] = relationship(
        back_populates="container_plan", cascade="all, delete-orphan"
    )
    sales_orders: Mapped[list[SalesOrder]] = relationship(
        "SalesOrder", secondary=container_plan_sales_orders
    )


class ContainerPlanItem(Base):
    __tablename__ = "container_plan_items"

    container_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_plans.id"), nullable=False
    )
    container_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    sales_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=True
    )
    inventory_record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_records.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_cbm: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)

    container_plan: Mapped[ContainerPlan] = relationship(back_populates="items")


class ContainerStuffingRecord(AuditMixin, Base):
    __tablename__ = "container_stuffing_records"

    container_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_plans.id"), nullable=False
    )
    container_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    container_no: Mapped[str] = mapped_column(String(20), nullable=False)
    seal_no: Mapped[str] = mapped_column(String(20), nullable=False)
    stuffing_date: Mapped[date] = mapped_column(Date, nullable=False)
    stuffing_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    container_plan: Mapped[ContainerPlan] = relationship(back_populates="stuffing_records")
    photos: Mapped[list[ContainerStuffingPhoto]] = relationship(
        back_populates="stuffing_record", cascade="all, delete-orphan"
    )


class ContainerStuffingPhoto(Base):
    __tablename__ = "container_stuffing_photos"

    stuffing_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_stuffing_records.id"), nullable=False
    )
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)

    stuffing_record: Mapped[ContainerStuffingRecord] = relationship(back_populates="photos")
