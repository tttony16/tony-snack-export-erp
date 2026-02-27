import uuid

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base


class Supplier(AuditMixin, Base):
    __tablename__ = "suppliers"

    supplier_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    supply_categories: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    supply_brands: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(200), nullable=True)
    business_license: Mapped[str | None] = mapped_column(String(100), nullable=True)
    food_production_license: Mapped[str | None] = mapped_column(String(100), nullable=True)
    certificate_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    products: Mapped[list["SupplierProduct"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )


class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    __table_args__ = (UniqueConstraint("supplier_id", "product_id", name="uq_supplier_product"),)

    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    supply_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    supplier: Mapped["Supplier"] = relationship(back_populates="products")
