import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.enums import AuditAction


class AuditLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_log(
        self,
        *,
        user_id: uuid.UUID | None = None,
        action: AuditAction,
        resource_type: str,
        resource_id: str | None = None,
        detail: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def search(
        self,
        *,
        user_id: uuid.UUID | None = None,
        action: AuditAction | None = None,
        resource_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog)
        count_query = select(func.count()).select_from(AuditLog)

        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if action:
            filters.append(AuditLog.action == action)
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        if date_from:
            filters.append(AuditLog.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            filters.append(AuditLog.created_at <= datetime.fromisoformat(date_to + "T23:59:59"))

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        order_col = getattr(AuditLog, order_by, AuditLog.created_at)
        if order_desc:
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total
