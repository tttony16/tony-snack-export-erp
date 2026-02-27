import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import AuditAction
from app.repositories.audit_log_repo import AuditLogRepository


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditLogRepository(db)

    async def log(
        self,
        *,
        user_id: uuid.UUID | None = None,
        action: AuditAction,
        resource_type: str,
        resource_id: str | None = None,
        detail: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        await self.repo.create_log(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip_address,
        )
