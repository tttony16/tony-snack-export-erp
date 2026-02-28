import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProductCategoryModel(Base):
    __tablename__ = "product_categories"
    __table_args__ = (
        UniqueConstraint("parent_id", "name", name="uq_category_parent_name"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_categories.id"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, server_default="0")

    parent = relationship(
        "ProductCategoryModel",
        back_populates="children",
        remote_side="ProductCategoryModel.id",
    )
    children = relationship(
        "ProductCategoryModel",
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="ProductCategoryModel.sort_order",
    )
