from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.dashboard import (
    ExpiryWarningResponse,
    InTransitResponse,
    OverviewResponse,
    TodoResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/overview", response_model=ApiResponse[OverviewResponse])
async def get_overview(
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    data = await service.get_overview()
    return ApiResponse(data=data)


@router.get("/todos", response_model=ApiResponse[TodoResponse])
async def get_todos(
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    data = await service.get_todos()
    return ApiResponse(data=data)


@router.get("/in-transit", response_model=ApiResponse[InTransitResponse])
async def get_in_transit(
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    data = await service.get_in_transit()
    return ApiResponse(data=data)


@router.get("/expiry-warnings", response_model=ApiResponse[ExpiryWarningResponse])
async def get_expiry_warnings(
    user: User = Depends(require_permission(Permission.SALES_ORDER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = DashboardService(db)
    data = await service.get_expiry_warnings()
    return ApiResponse(data=data)
