import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_config import SystemConfig


class SystemConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_key(self, key: str) -> SystemConfig | None:
        result = await self.db.execute(select(SystemConfig).where(SystemConfig.config_key == key))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[SystemConfig]:
        result = await self.db.execute(select(SystemConfig).order_by(SystemConfig.config_key))
        return list(result.scalars().all())

    async def upsert(
        self, key: str, value, description: str | None = None, user_id: uuid.UUID | None = None
    ) -> SystemConfig:
        config = await self.get_by_key(key)
        if config:
            config.config_value = value
            if description is not None:
                config.description = description
            config.updated_by = user_id
            await self.db.flush()
            await self.db.refresh(config)
        else:
            config = SystemConfig(
                config_key=key,
                config_value=value,
                description=description,
                updated_by=user_id,
            )
            self.db.add(config)
            await self.db.flush()
            await self.db.refresh(config)
        return config
