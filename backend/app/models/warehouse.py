import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base
from app.models.enums import InspectionResult


class ReceivingNote(AuditMixin, Base):
    __tablename__ = "receiving_notes"

    note_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    purchase_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False
    )
    receiving_date: Mapped[date] = mapped_column(Date, nullable=False)
    receiver: Mapped[str] = mapped_column(String(100), nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["ReceivingNoteItem"]] = relationship(
        back_populates="receiving_note", cascade="all, delete-orphan"
    )


class ReceivingNoteItem(Base):
    __tablename__ = "receiving_note_items"

    receiving_note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("receiving_notes.id"), nullable=False
    )
    purchase_order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_order_items.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    expected_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    inspection_result: Mapped[InspectionResult] = mapped_column(
        ENUM(
            InspectionResult,
            name="inspection_result",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    failed_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    batch_no: Mapped[str] = mapped_column(String(50), nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    receiving_note: Mapped["ReceivingNote"] = relationship(back_populates="items")


class InventoryRecord(Base):
    __tablename__ = "inventory_records"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    sales_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id"), nullable=True
    )
    receiving_note_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("receiving_note_items.id"), nullable=False
    )
    batch_no: Mapped[str] = mapped_column(String(50), nullable=False)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
