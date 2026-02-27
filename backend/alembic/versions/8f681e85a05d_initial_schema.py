"""initial schema

Revision ID: 8f681e85a05d
Revises:
Create Date: 2026-02-27 05:56:39.704452

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f681e85a05d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define enums with create_type=False for use in table definitions
user_role = postgresql.ENUM(
    'super_admin', 'admin', 'sales', 'purchaser', 'warehouse', 'viewer',
    name='user_role', create_type=False,
)
product_category = postgresql.ENUM(
    'puffed_food', 'candy', 'biscuit', 'nut', 'beverage', 'seasoning',
    'instant_noodle', 'dried_fruit', 'chocolate', 'jelly', 'other',
    name='product_category', create_type=False,
)
product_status = postgresql.ENUM(
    'active', 'inactive', name='product_status', create_type=False,
)
currency_type = postgresql.ENUM(
    'USD', 'EUR', 'JPY', 'GBP', 'THB', 'VND', 'MYR', 'SGD', 'PHP', 'IDR', 'RMB', 'OTHER',
    name='currency_type', create_type=False,
)
payment_method = postgresql.ENUM(
    'TT', 'LC', 'DP', 'DA', name='payment_method', create_type=False,
)
trade_term = postgresql.ENUM(
    'FOB', 'CIF', 'CFR', 'EXW', 'DDP', 'DAP', name='trade_term', create_type=False,
)


def upgrade() -> None:
    # Create all enum types (including future ones to avoid ALTER TYPE)
    bind = op.get_bind()
    for enum in [
        user_role, product_category, product_status, currency_type, payment_method, trade_term,
    ]:
        enum.create(bind, checkfirst=True)

    # Future enums — create now, use in later phases
    for name, values in [
        ('sales_order_status', ['draft', 'confirmed', 'purchasing', 'goods_ready', 'container_planned', 'container_loaded', 'shipped', 'delivered', 'completed', 'abnormal']),
        ('purchase_order_status', ['draft', 'ordered', 'partial_received', 'fully_received', 'completed', 'cancelled']),
        ('inspection_result', ['passed', 'failed', 'partial_passed']),
        ('container_plan_status', ['planning', 'confirmed', 'loading', 'loaded', 'shipped']),
        ('container_type', ['20GP', '40GP', '40HQ', 'reefer']),
        ('logistics_status', ['booked', 'customs_cleared', 'loaded_on_ship', 'in_transit', 'arrived', 'picked_up', 'delivered']),
        ('unit_type', ['piece', 'carton']),
        ('logistics_cost_type', ['ocean_freight', 'customs_fee', 'port_charge', 'trucking_fee', 'insurance_fee', 'other']),
        ('audit_action', ['create', 'update', 'delete', 'export', 'status_change', 'login', 'logout', 'permission_change']),
    ]:
        postgresql.ENUM(*values, name=name, create_type=False).create(bind, checkfirst=True)

    # Create tables
    op.create_table('users',
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', user_role, nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_table('customers',
        sa.Column('customer_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('short_name', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('contact_person', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('currency', currency_type, nullable=False),
        sa.Column('payment_method', payment_method, nullable=False),
        sa.Column('payment_terms', sa.String(length=200), nullable=True),
        sa.Column('trade_term', trade_term, nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_code')
    )
    op.create_table('suppliers',
        sa.Column('supplier_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('supply_categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('supply_brands', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('payment_terms', sa.String(length=200), nullable=True),
        sa.Column('business_license', sa.String(length=100), nullable=True),
        sa.Column('food_production_license', sa.String(length=100), nullable=True),
        sa.Column('certificate_urls', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_code')
    )
    op.create_table('products',
        sa.Column('sku_code', sa.String(length=50), nullable=False),
        sa.Column('name_cn', sa.String(length=200), nullable=False),
        sa.Column('name_en', sa.String(length=200), nullable=False),
        sa.Column('category', product_category, nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('barcode', sa.String(length=50), nullable=True),
        sa.Column('spec', sa.String(length=200), nullable=False),
        sa.Column('unit_weight_kg', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('unit_volume_cbm', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('packing_spec', sa.String(length=200), nullable=False),
        sa.Column('carton_length_cm', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('carton_width_cm', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('carton_height_cm', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('carton_gross_weight_kg', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('shelf_life_days', sa.Integer(), nullable=False),
        sa.Column('default_purchase_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('default_supplier_id', sa.UUID(), nullable=True),
        sa.Column('hs_code', sa.String(length=20), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('status', product_status, server_default='active', nullable=False),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['default_supplier_id'], ['suppliers.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku_code')
    )
    op.create_table('supplier_products',
        sa.Column('supplier_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('supply_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_id', 'product_id', name='uq_supplier_product')
    )


def downgrade() -> None:
    op.drop_table('supplier_products')
    op.drop_table('products')
    op.drop_table('suppliers')
    op.drop_table('customers')
    op.drop_table('users')

    # Drop all enum types
    bind = op.get_bind()
    for name in [
        'audit_action', 'logistics_cost_type', 'unit_type', 'logistics_status',
        'container_type', 'container_plan_status', 'inspection_result',
        'purchase_order_status', 'sales_order_status', 'trade_term',
        'payment_method', 'currency_type', 'product_status', 'product_category',
        'user_role',
    ]:
        postgresql.ENUM(name=name, create_type=False).drop(bind, checkfirst=True)
