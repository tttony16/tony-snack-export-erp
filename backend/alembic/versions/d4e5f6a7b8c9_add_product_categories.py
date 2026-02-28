"""add product_categories table and migrate products/suppliers

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-02-28 10:00:00.000000
"""

import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None

# Deterministic UUIDs for level-1 seed categories (uuid5 from namespace URL + name)
NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
CATEGORY_SEEDS = [
    ("puffed_food", "膨化食品", 0),
    ("candy", "糖果", 1),
    ("biscuit", "饼干", 2),
    ("nut", "坚果", 3),
    ("beverage", "饮料", 4),
    ("seasoning", "调味品", 5),
    ("instant_noodle", "方便面", 6),
    ("dried_fruit", "果干", 7),
    ("chocolate", "巧克力", 8),
    ("jelly", "果冻", 9),
    ("other", "其他", 10),
]


def _seed_id(key: str) -> str:
    return str(uuid.uuid5(NAMESPACE, key))


def upgrade() -> None:
    # 1. Create product_categories table
    op.create_table(
        "product_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("product_categories.id"), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("parent_id", "name", name="uq_category_parent_name"),
    )

    # 2. Insert 11 level-1 seed categories
    product_categories = sa.table(
        "product_categories",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("level", sa.Integer),
        sa.column("parent_id", UUID(as_uuid=True)),
        sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(
        product_categories,
        [
            {
                "id": _seed_id(key),
                "name": name,
                "level": 1,
                "parent_id": None,
                "sort_order": sort,
            }
            for key, name, sort in CATEGORY_SEEDS
        ],
    )

    # 3. Add category_id column to products (nullable initially)
    op.add_column("products", sa.Column("category_id", UUID(as_uuid=True), nullable=True))

    # 4. Data migration: map old enum values to new category UUIDs
    for key, _name, _sort in CATEGORY_SEEDS:
        cat_id = _seed_id(key)
        op.execute(
            sa.text(
                f"UPDATE products SET category_id = '{cat_id}'::uuid WHERE category::text = '{key}'"
            )
        )

    # 5. Set category_id NOT NULL + FK
    op.alter_column("products", "category_id", nullable=False)
    op.create_foreign_key(
        "fk_products_category_id",
        "products",
        "product_categories",
        ["category_id"],
        ["id"],
    )

    # 6. Drop old category column
    op.drop_column("products", "category")

    # 7. Supplier: add supply_category_ids UUID array, migrate data, rename
    op.add_column(
        "suppliers",
        sa.Column("supply_category_ids", sa.ARRAY(UUID(as_uuid=True)), nullable=True),
    )
    # Migrate: for each old string value, set the corresponding UUID
    for key, _name, _sort in CATEGORY_SEEDS:
        cat_id = _seed_id(key)
        op.execute(
            sa.text(
                f"UPDATE suppliers SET supply_category_ids = "
                f"array_append(COALESCE(supply_category_ids, ARRAY[]::uuid[]), '{cat_id}'::uuid) "
                f"WHERE '{key}' = ANY(supply_categories)"
            )
        )
    op.drop_column("suppliers", "supply_categories")
    op.alter_column("suppliers", "supply_category_ids", new_column_name="supply_categories")

    # 8. Drop old product_category enum type
    op.execute(sa.text("DROP TYPE IF EXISTS product_category"))


def downgrade() -> None:
    # Recreate enum type
    product_category_enum = sa.Enum(
        "puffed_food", "candy", "biscuit", "nut", "beverage", "seasoning",
        "instant_noodle", "dried_fruit", "chocolate", "jelly", "other",
        name="product_category",
    )
    product_category_enum.create(op.get_bind())

    # Suppliers: revert to string array
    op.alter_column("suppliers", "supply_categories", new_column_name="supply_category_ids")
    op.add_column("suppliers", sa.Column("supply_categories", sa.ARRAY(sa.String), nullable=True))
    for key, _name, _sort in CATEGORY_SEEDS:
        cat_id = _seed_id(key)
        op.execute(
            sa.text(
                f"UPDATE suppliers SET supply_categories = "
                f"array_append(COALESCE(supply_categories, ARRAY[]::varchar[]), '{key}') "
                f"WHERE '{cat_id}'::uuid = ANY(supply_category_ids)"
            )
        )
    op.drop_column("suppliers", "supply_category_ids")

    # Products: re-add category enum column
    op.add_column(
        "products",
        sa.Column("category", product_category_enum, nullable=True),
    )
    for key, _name, _sort in CATEGORY_SEEDS:
        cat_id = _seed_id(key)
        op.execute(
            sa.text(
                f"UPDATE products SET category = '{key}' WHERE category_id = '{cat_id}'::uuid"
            )
        )
    op.alter_column("products", "category", nullable=False)
    op.drop_constraint("fk_products_category_id", "products", type_="foreignkey")
    op.drop_column("products", "category_id")

    # Drop product_categories table
    op.drop_table("product_categories")
