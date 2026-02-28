"""Seed script: create initial super_admin user and product categories."""

import asyncio
import uuid

from sqlalchemy import select

from app.core.security import hash_password
from app.database import async_session_factory
from app.models.enums import UserRole
from app.models.product_category import ProductCategoryModel
from app.models.user import User

# Same namespace and seeds as the migration for deterministic UUIDs
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


async def seed() -> None:
    async with async_session_factory() as session:
        # Seed admin user
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping.")
        else:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                display_name="超级管理员",
                email="admin@snack-erp.local",
                role=UserRole.SUPER_ADMIN,
                is_active=True,
            )
            session.add(admin)
            await session.flush()
            print(f"Created admin user: admin / admin123 (id={admin.id})")

        # Seed level-1 categories
        result = await session.execute(
            select(ProductCategoryModel).where(ProductCategoryModel.level == 1).limit(1)
        )
        if result.scalar_one_or_none():
            print("Product categories already exist, skipping.")
        else:
            for key, name, sort in CATEGORY_SEEDS:
                cat = ProductCategoryModel(
                    id=uuid.uuid5(NAMESPACE, key),
                    name=name,
                    level=1,
                    parent_id=None,
                    sort_order=sort,
                )
                session.add(cat)
            await session.flush()
            print(f"Created {len(CATEGORY_SEEDS)} level-1 product categories.")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
