import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditMixin, Base
from app.models.enums import ProductStatus


class Product(AuditMixin, Base):
    __tablename__ = "products"

    sku_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_cn: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=False
    )
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    spec: Mapped[str] = mapped_column(String(200), nullable=False)
    unit_weight_kg: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    unit_volume_cbm: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    packing_spec: Mapped[str] = mapped_column(String(200), nullable=False)
    carton_length_cm: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carton_width_cm: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carton_height_cm: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    carton_gross_weight_kg: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False)
    default_purchase_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    default_supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True
    )
    hs_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        ENUM(
            ProductStatus,
            name="product_status",
            create_type=False,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        server_default="active",
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    category = relationship("ProductCategoryModel", lazy="joined")
