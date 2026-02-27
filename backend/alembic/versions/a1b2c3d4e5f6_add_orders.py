"""add sales orders and purchase orders

Revision ID: a1b2c3d4e5f6
Revises: 8f681e85a05d
Create Date: 2026-02-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8f681e85a05d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Reuse existing enum types (created in initial migration)
sales_order_status = postgresql.ENUM(
    'draft', 'confirmed', 'purchasing', 'goods_ready', 'container_planned',
    'container_loaded', 'shipped', 'delivered', 'completed', 'abnormal',
    name='sales_order_status', create_type=False,
)
purchase_order_status = postgresql.ENUM(
    'draft', 'ordered', 'partial_received', 'fully_received', 'completed', 'cancelled',
    name='purchase_order_status', create_type=False,
)
unit_type = postgresql.ENUM('piece', 'carton', name='unit_type', create_type=False)
currency_type = postgresql.ENUM(
    'USD', 'EUR', 'JPY', 'GBP', 'THB', 'VND', 'MYR', 'SGD', 'PHP', 'IDR', 'RMB', 'OTHER',
    name='currency_type', create_type=False,
)
payment_method = postgresql.ENUM('TT', 'LC', 'DP', 'DA', name='payment_method', create_type=False)
trade_term = postgresql.ENUM('FOB', 'CIF', 'CFR', 'EXW', 'DDP', 'DAP', name='trade_term', create_type=False)


def upgrade() -> None:
    # 1. sales_orders
    op.create_table('sales_orders',
        sa.Column('order_no', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.UUID(), nullable=False),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('required_delivery_date', sa.Date(), nullable=True),
        sa.Column('destination_port', sa.String(length=200), nullable=False),
        sa.Column('trade_term', trade_term, nullable=False),
        sa.Column('currency', currency_type, nullable=False),
        sa.Column('payment_method', payment_method, nullable=False),
        sa.Column('payment_terms', sa.String(length=200), nullable=True),
        sa.Column('status', sales_order_status, server_default='draft', nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=14, scale=2), server_default='0', nullable=False),
        sa.Column('total_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('estimated_volume_cbm', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('estimated_weight_kg', sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no'),
    )
    op.create_index('ix_sales_orders_customer_id', 'sales_orders', ['customer_id'])
    op.create_index('ix_sales_orders_status', 'sales_orders', ['status'])
    op.create_index('ix_sales_orders_order_date', 'sales_orders', ['order_date'])

    # 2. sales_order_items
    op.create_table('sales_order_items',
        sa.Column('sales_order_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit', unit_type, nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('purchased_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('received_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 3. purchase_orders
    op.create_table('purchase_orders',
        sa.Column('order_no', sa.String(length=50), nullable=False),
        sa.Column('supplier_id', sa.UUID(), nullable=False),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('required_date', sa.Date(), nullable=True),
        sa.Column('status', purchase_order_status, server_default='draft', nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=14, scale=2), server_default='0', nullable=False),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no'),
    )
    op.create_index('ix_purchase_orders_supplier_id', 'purchase_orders', ['supplier_id'])
    op.create_index('ix_purchase_orders_status', 'purchase_orders', ['status'])

    # 4. purchase_order_items
    op.create_table('purchase_order_items',
        sa.Column('purchase_order_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('sales_order_item_id', sa.UUID(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit', unit_type, nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('received_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['sales_order_item_id'], ['sales_order_items.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # 5. purchase_order_sales_orders (M2M)
    op.create_table('purchase_order_sales_orders',
        sa.Column('purchase_order_id', sa.UUID(), nullable=False),
        sa.Column('sales_order_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id']),
        sa.ForeignKeyConstraint(['sales_order_id'], ['sales_orders.id']),
        sa.PrimaryKeyConstraint('purchase_order_id', 'sales_order_id'),
        sa.UniqueConstraint('purchase_order_id', 'sales_order_id', name='uq_po_so'),
    )


def downgrade() -> None:
    op.drop_table('purchase_order_sales_orders')
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('sales_order_items')
    op.drop_table('sales_orders')
