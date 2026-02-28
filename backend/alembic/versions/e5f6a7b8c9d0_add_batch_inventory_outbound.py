"""add batch inventory management and outbound orders

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-02-28 12:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None

outbound_order_status_enum = PG_ENUM(
    "draft", "confirmed", "cancelled", name="outbound_order_status", create_type=False
)


def upgrade() -> None:
    # 1. Create outbound_order_status ENUM type
    outbound_order_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. inventory_records: add reserved_quantity column
    op.add_column(
        "inventory_records",
        sa.Column("reserved_quantity", sa.Integer(), nullable=False, server_default="0"),
    )

    # 3. container_plan_items: add inventory_record_id, make sales_order_id nullable
    op.add_column(
        "container_plan_items",
        sa.Column("inventory_record_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_cpi_inventory_record",
        "container_plan_items",
        "inventory_records",
        ["inventory_record_id"],
        ["id"],
    )
    # Make sales_order_id nullable
    op.alter_column(
        "container_plan_items",
        "sales_order_id",
        existing_type=UUID(as_uuid=True),
        nullable=True,
    )

    # 4. sales_order_items: add reserved_quantity and outbound_quantity
    op.add_column(
        "sales_order_items",
        sa.Column("reserved_quantity", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "sales_order_items",
        sa.Column("outbound_quantity", sa.Integer(), nullable=False, server_default="0"),
    )

    # 5. Create outbound_orders table
    op.create_table(
        "outbound_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_no", sa.String(50), unique=True, nullable=False),
        sa.Column(
            "container_plan_id",
            UUID(as_uuid=True),
            sa.ForeignKey("container_plans.id"),
            nullable=False,
        ),
        sa.Column(
            "status",
            outbound_order_status_enum,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("outbound_date", sa.Date(), nullable=True),
        sa.Column("operator", sa.String(100), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column(
            "created_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 6. Create outbound_order_items table
    op.create_table(
        "outbound_order_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "outbound_order_id",
            UUID(as_uuid=True),
            sa.ForeignKey("outbound_orders.id"),
            nullable=False,
        ),
        sa.Column(
            "container_plan_item_id",
            UUID(as_uuid=True),
            sa.ForeignKey("container_plan_items.id"),
            nullable=True,
        ),
        sa.Column(
            "inventory_record_id",
            UUID(as_uuid=True),
            sa.ForeignKey("inventory_records.id"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column(
            "sales_order_id",
            UUID(as_uuid=True),
            sa.ForeignKey("sales_orders.id"),
            nullable=True,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("batch_no", sa.String(50), nullable=False),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("outbound_order_items")
    op.drop_table("outbound_orders")

    op.drop_column("sales_order_items", "outbound_quantity")
    op.drop_column("sales_order_items", "reserved_quantity")

    op.drop_constraint("fk_cpi_inventory_record", "container_plan_items", type_="foreignkey")
    op.drop_column("container_plan_items", "inventory_record_id")
    op.alter_column(
        "container_plan_items",
        "sales_order_id",
        existing_type=UUID(as_uuid=True),
        nullable=False,
    )

    op.drop_column("inventory_records", "reserved_quantity")

    outbound_order_status_enum.drop(op.get_bind(), checkfirst=True)
