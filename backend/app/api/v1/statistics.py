from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.statistics import (
    ContainerSummaryStatResponse,
    CustomerRankingResponse,
    ProductRankingResponse,
    PurchaseSummaryResponse,
    SalesSummaryResponse,
)
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["统计报表"])


@router.get("/sales-summary", response_model=ApiResponse[SalesSummaryResponse])
async def sales_summary(
    group_by: str = Query("month", pattern="^(month|customer)$"),
    date_from: str | None = None,
    date_to: str | None = None,
    user: User = Depends(require_permission(Permission.STATISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = StatisticsService(db)
    data = await service.sales_summary(group_by=group_by, date_from=date_from, date_to=date_to)
    return ApiResponse(data=data)


@router.get("/purchase-summary", response_model=ApiResponse[PurchaseSummaryResponse])
async def purchase_summary(
    group_by: str = Query("month", pattern="^(month|supplier)$"),
    date_from: str | None = None,
    date_to: str | None = None,
    user: User = Depends(require_permission(Permission.STATISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = StatisticsService(db)
    data = await service.purchase_summary(group_by=group_by, date_from=date_from, date_to=date_to)
    return ApiResponse(data=data)


@router.get("/container-summary", response_model=ApiResponse[ContainerSummaryStatResponse])
async def container_summary(
    group_by: str = Query("month", pattern="^(month|container_type)$"),
    date_from: str | None = None,
    date_to: str | None = None,
    user: User = Depends(require_permission(Permission.STATISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = StatisticsService(db)
    data = await service.container_summary(group_by=group_by, date_from=date_from, date_to=date_to)
    return ApiResponse(data=data)


@router.get("/customer-ranking", response_model=ApiResponse[CustomerRankingResponse])
async def customer_ranking(
    date_from: str | None = None,
    date_to: str | None = None,
    top_n: int = Query(20, ge=1, le=100),
    user: User = Depends(require_permission(Permission.STATISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = StatisticsService(db)
    data = await service.customer_ranking(date_from=date_from, date_to=date_to, top_n=top_n)
    return ApiResponse(data=data)


@router.get("/product-ranking", response_model=ApiResponse[ProductRankingResponse])
async def product_ranking(
    date_from: str | None = None,
    date_to: str | None = None,
    top_n: int = Query(20, ge=1, le=100),
    user: User = Depends(require_permission(Permission.STATISTICS_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = StatisticsService(db)
    data = await service.product_ranking(date_from=date_from, date_to=date_to, top_n=top_n)
    return ApiResponse(data=data)
