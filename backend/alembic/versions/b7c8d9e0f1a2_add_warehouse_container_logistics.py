"""add warehouse, container and logistics tables

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-02-27 12:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM, UUID

revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

# Enum types already created in initial migration
inspection_result = ENUM("passed", "failed", "partial_passed", name="inspection_result", create_type=False)
container_plan_status = ENUM("planning", "confirmed", "loading", "loaded", "shipped", name="container_plan_status", create_type=False)
container_type = ENUM("20GP", "40GP", "40HQ", "reefer", name="container_type", create_type=False)
logistics_status = ENUM(
    "booked", "customs_cleared", "loaded_on_ship", "in_transit",
    "arrived", "picked_up", "delivered", name="logistics_status", create_type=False
)
logistics_cost_type = ENUM(
    "ocean_freight", "customs_fee", "port_charge", "trucking_fee",
    "insurance_fee", "other", name="logistics_cost_type", create_type=False
)
currency_type = ENUM(
    "USD", "EUR", "JPY", "GBP", "THB", "VND", "MYR", "SGD", "PHP", "IDR", "RMB", "OTHER",
    name="currency_type", create_type=False
)


def upgrade() -> None:
    # --- Warehouse: receiving_notes ---
    op.create_table(
        "receiving_notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("note_no", sa.String(50), unique=True, nullable=False),
        sa.Column("purchase_order_id", UUID(as_uuid=True), sa.ForeignKey("purchase_orders.id"), nullable=False),
        sa.Column("receiving_date", sa.Date, nullable=False),
        sa.Column("receiver", sa.String(100), nullable=False),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_receiving_notes_po", "receiving_notes", ["purchase_order_id"])

    # --- Warehouse: receiving_note_items ---
    op.create_table(
        "receiving_note_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("receiving_note_id", UUID(as_uuid=True), sa.ForeignKey("receiving_notes.id"), nullable=False),
        sa.Column("purchase_order_item_id", UUID(as_uuid=True), sa.ForeignKey("purchase_order_items.id"), nullable=False),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("expected_quantity", sa.Integer, nullable=False),
        sa.Column("actual_quantity", sa.Integer, nullable=False),
        sa.Column("inspection_result", inspection_result, nullable=False),
        sa.Column("failed_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("production_date", sa.Date, nullable=False),
        sa.Column("batch_no", sa.String(50), nullable=False),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_receiving_note_items_note", "receiving_note_items", ["receiving_note_id"])

    # --- Warehouse: inventory_records ---
    op.create_table(
        "inventory_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("sales_order_id", UUID(as_uuid=True), sa.ForeignKey("sales_orders.id"), nullable=True),
        sa.Column("receiving_note_item_id", UUID(as_uuid=True), sa.ForeignKey("receiving_note_items.id"), nullable=False),
        sa.Column("batch_no", sa.String(50), nullable=False),
        sa.Column("production_date", sa.Date, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("available_quantity", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_inventory_product", "inventory_records", ["product_id"])
    op.create_index("idx_inventory_sales_order", "inventory_records", ["sales_order_id"])
    op.create_index("idx_inventory_batch", "inventory_records", ["batch_no"])

    # --- Container: container_plans ---
    op.create_table(
        "container_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("plan_no", sa.String(50), unique=True, nullable=False),
        sa.Column("container_type", container_type, nullable=False),
        sa.Column("container_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("destination_port", sa.String(200), nullable=False),
        sa.Column("status", container_plan_status, nullable=False, server_default="planning"),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_container_plans_status", "container_plans", ["status"])

    # --- Container: container_plan_sales_orders M2M ---
    op.create_table(
        "container_plan_sales_orders",
        sa.Column("container_plan_id", UUID(as_uuid=True), sa.ForeignKey("container_plans.id"), primary_key=True),
        sa.Column("sales_order_id", UUID(as_uuid=True), sa.ForeignKey("sales_orders.id"), primary_key=True),
        sa.UniqueConstraint("container_plan_id", "sales_order_id", name="uq_cp_so"),
    )

    # --- Container: container_plan_items ---
    op.create_table(
        "container_plan_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("container_plan_id", UUID(as_uuid=True), sa.ForeignKey("container_plans.id"), nullable=False),
        sa.Column("container_seq", sa.Integer, nullable=False),
        sa.Column("product_id", UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("sales_order_id", UUID(as_uuid=True), sa.ForeignKey("sales_orders.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("volume_cbm", sa.Numeric(10, 4), nullable=False),
        sa.Column("weight_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_container_plan_items_plan", "container_plan_items", ["container_plan_id"])
    op.create_index("idx_container_plan_items_seq", "container_plan_items", ["container_plan_id", "container_seq"])

    # --- Container: container_stuffing_records ---
    op.create_table(
        "container_stuffing_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("container_plan_id", UUID(as_uuid=True), sa.ForeignKey("container_plans.id"), nullable=False),
        sa.Column("container_seq", sa.Integer, nullable=False),
        sa.Column("container_no", sa.String(20), nullable=False),
        sa.Column("seal_no", sa.String(20), nullable=False),
        sa.Column("stuffing_date", sa.Date, nullable=False),
        sa.Column("stuffing_location", sa.String(200), nullable=True),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_stuffing_records_plan", "container_stuffing_records", ["container_plan_id"])

    # --- Container: container_stuffing_photos ---
    op.create_table(
        "container_stuffing_photos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("stuffing_record_id", UUID(as_uuid=True), sa.ForeignKey("container_stuffing_records.id"), nullable=False),
        sa.Column("photo_url", sa.String(500), nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- Logistics: logistics_records ---
    op.create_table(
        "logistics_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("logistics_no", sa.String(50), unique=True, nullable=False),
        sa.Column("container_plan_id", UUID(as_uuid=True), sa.ForeignKey("container_plans.id"), nullable=False),
        sa.Column("shipping_company", sa.String(200), nullable=True),
        sa.Column("vessel_voyage", sa.String(200), nullable=True),
        sa.Column("bl_no", sa.String(100), nullable=True),
        sa.Column("port_of_loading", sa.String(200), nullable=False),
        sa.Column("port_of_discharge", sa.String(200), nullable=False),
        sa.Column("etd", sa.Date, nullable=True),
        sa.Column("eta", sa.Date, nullable=True),
        sa.Column("actual_departure_date", sa.Date, nullable=True),
        sa.Column("actual_arrival_date", sa.Date, nullable=True),
        sa.Column("status", logistics_status, nullable=False, server_default="booked"),
        sa.Column("customs_declaration_no", sa.String(100), nullable=True),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("idx_logistics_status", "logistics_records", ["status"])
    op.create_index("idx_logistics_container_plan", "logistics_records", ["container_plan_id"])
    op.create_index("idx_logistics_bl_no", "logistics_records", ["bl_no"])

    # --- Logistics: logistics_costs ---
    op.create_table(
        "logistics_costs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("logistics_record_id", UUID(as_uuid=True), sa.ForeignKey("logistics_records.id"), nullable=False),
        sa.Column("cost_type", logistics_cost_type, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", currency_type, nullable=False),
        sa.Column("remark", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_logistics_costs_record", "logistics_costs", ["logistics_record_id"])


def downgrade() -> None:
    op.drop_table("logistics_costs")
    op.drop_table("logistics_records")
    op.drop_table("container_stuffing_photos")
    op.drop_table("container_stuffing_records")
    op.drop_table("container_plan_items")
    op.drop_table("container_plan_sales_orders")
    op.drop_table("container_plans")
    op.drop_table("inventory_records")
    op.drop_table("receiving_note_items")
    op.drop_table("receiving_notes")
