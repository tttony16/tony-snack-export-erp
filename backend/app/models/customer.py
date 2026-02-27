from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base
from app.models.enums import CurrencyType, PaymentMethod, TradeTerm


class Customer(AuditMixin, Base):
    __tablename__ = "customers"

    customer_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    trade_term: Mapped[TradeTerm | None] = mapped_column(
        ENUM(
            TradeTerm,
            name="trade_term",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
