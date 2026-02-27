"""Seed script: create initial super_admin user."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database import async_session_factory
from app.models.enums import UserRole
from app.models.user import User


async def seed() -> None:
    async with async_session_factory() as session:
        # Check if admin already exists
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping.")
            return

        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            display_name="超级管理员",
            email="admin@snack-erp.local",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Created admin user: admin / admin123 (id={admin.id})")


if __name__ == "__main__":
    asyncio.run(seed())
