import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base
from app.models.enums import CurrencyType, LogisticsCostType, LogisticsStatus


class LogisticsRecord(AuditMixin, Base):
    __tablename__ = "logistics_records"

    logistics_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    container_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("container_plans.id"), nullable=False
    )
    shipping_company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vessel_voyage: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bl_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    port_of_loading: Mapped[str] = mapped_column(String(200), nullable=False)
    port_of_discharge: Mapped[str] = mapped_column(String(200), nullable=False)
    etd: Mapped[date | None] = mapped_column(Date, nullable=True)
    eta: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_departure_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[LogisticsStatus] = mapped_column(
        ENUM(
            LogisticsStatus,
            name="logistics_status",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default="booked",
    )
    customs_declaration_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_cost: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, server_default="0")
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    costs: Mapped[list["LogisticsCost"]] = relationship(
        back_populates="logistics_record", cascade="all, delete-orphan"
    )


class LogisticsCost(Base):
    __tablename__ = "logistics_costs"

    logistics_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("logistics_records.id"), nullable=False
    )
    cost_type: Mapped[LogisticsCostType] = mapped_column(
        ENUM(
            LogisticsCostType,
            name="logistics_cost_type",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(
        ENUM(
            CurrencyType,
            name="currency_type",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    logistics_record: Mapped["LogisticsRecord"] = relationship(back_populates="costs")
