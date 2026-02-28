import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.container import (
    ContainerPlanCreate,
    ContainerPlanItemCreate,
    ContainerPlanItemRead,
    ContainerPlanItemUpdate,
    ContainerPlanListParams,
    ContainerPlanListRead,
    ContainerPlanRead,
    ContainerPlanUpdate,
    ContainerRecommendationResponse,
    ContainerStuffingCreate,
    ContainerStuffingPhotoCreate,
    ContainerStuffingPhotoRead,
    ContainerStuffingRecordRead,
    ContainerSummaryResponse,
    ContainerValidationResponse,
)
from app.services.container_service import ContainerService

router = APIRouter(prefix="/containers", tags=["排柜管理"])


def _build_plan_read(plan) -> ContainerPlanRead:
    sos = plan.sales_orders
    so_ids = [so.id for so in sos] if isinstance(sos, list) else []
    stuffing = plan.stuffing_records
    stuffing_list = (
        [ContainerStuffingRecordRead.model_validate(r) for r in stuffing]
        if isinstance(stuffing, list)
        else []
    )
    item_reads = []
    for i in plan.items:
        item_data = ContainerPlanItemRead.model_validate(i)
        item_reads.append(item_data)
    return ContainerPlanRead(
        id=plan.id,
        plan_no=plan.plan_no,
        container_type=plan.container_type,
        container_count=plan.container_count,
        destination_port=plan.destination_port,
        status=plan.status,
        remark=plan.remark,
        items=item_reads,
        linked_sales_order_ids=so_ids,
        stuffing_records=stuffing_list,
        created_at=str(plan.created_at) if plan.created_at else None,
        updated_at=str(plan.updated_at) if plan.updated_at else None,
    )


@router.get("", response_model=PaginatedResponse[ContainerPlanListRead])
async def list_container_plans(
    status_filter: str | None = Query(None, alias="status"),
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.CONTAINER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.enums import ContainerPlanStatus

    params = ContainerPlanListParams(
        status=ContainerPlanStatus(status_filter) if status_filter else None,
        keyword=keyword,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    service = ContainerService(db)
    data = await service.list_plans(params)
    return PaginatedResponse(data=data)


@router.post(
    "",
    response_model=ApiResponse[ContainerPlanRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_container_plan(
    body: ContainerPlanCreate,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    plan = await service.create(body, user.id)
    return ApiResponse(data=_build_plan_read(plan))


@router.get("/{id}", response_model=ApiResponse[ContainerPlanRead])
async def get_container_plan(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    plan = await service.get_by_id(id)
    return ApiResponse(data=_build_plan_read(plan))


@router.put("/{id}", response_model=ApiResponse[ContainerPlanRead])
async def update_container_plan(
    id: uuid.UUID,
    body: ContainerPlanUpdate,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    plan = await service.update(id, body, user.id)
    return ApiResponse(data=_build_plan_read(plan))


@router.post("/{id}/recommend-type", response_model=ApiResponse[ContainerRecommendationResponse])
async def recommend_container_type(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    data = await service.recommend_type(id)
    return ApiResponse(data=data)


@router.post(
    "/{id}/items",
    response_model=ApiResponse[ContainerPlanItemRead],
    status_code=status.HTTP_201_CREATED,
)
async def add_container_item(
    id: uuid.UUID,
    body: ContainerPlanItemCreate,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    item = await service.add_item(id, body)
    return ApiResponse(data=ContainerPlanItemRead.model_validate(item))


@router.put("/{id}/items/{item_id}", response_model=ApiResponse[ContainerPlanItemRead])
async def update_container_item(
    id: uuid.UUID,
    item_id: uuid.UUID,
    body: ContainerPlanItemUpdate,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    item = await service.update_item(id, item_id, body)
    return ApiResponse(data=ContainerPlanItemRead.model_validate(item))


@router.delete("/{id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_container_item(
    id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    await service.delete_item(id, item_id)


@router.get("/{id}/summary", response_model=ApiResponse[ContainerSummaryResponse])
async def get_container_summary(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    data = await service.get_summary(id)
    return ApiResponse(data=data)


@router.post("/{id}/validate", response_model=ApiResponse[ContainerValidationResponse])
async def validate_container(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    data = await service.validate(id)
    return ApiResponse(data=data)


@router.post("/{id}/confirm", response_model=ApiResponse[ContainerPlanRead])
async def confirm_container_plan(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_CONFIRM)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    plan = await service.confirm(id, user.id)
    return ApiResponse(data=_build_plan_read(plan))


@router.post("/{id}/cancel", response_model=ApiResponse[ContainerPlanRead])
async def cancel_container_plan(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.CONTAINER_CONFIRM)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    plan = await service.cancel_plan(id, user.id)
    return ApiResponse(data=_build_plan_read(plan))


@router.post(
    "/{id}/stuffing",
    response_model=ApiResponse[ContainerStuffingRecordRead],
    status_code=status.HTTP_201_CREATED,
)
async def record_stuffing(
    id: uuid.UUID,
    body: ContainerStuffingCreate,
    user: User = Depends(require_permission(Permission.CONTAINER_STUFFING)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    record = await service.record_stuffing(id, body, user.id)
    return ApiResponse(data=ContainerStuffingRecordRead.model_validate(record))


@router.post(
    "/{id}/stuffing/photos",
    response_model=ApiResponse[ContainerStuffingPhotoRead],
    status_code=status.HTTP_201_CREATED,
)
async def upload_stuffing_photo(
    id: uuid.UUID,
    body: ContainerStuffingPhotoCreate,
    user: User = Depends(require_permission(Permission.CONTAINER_STUFFING)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    photo = await service.add_stuffing_photo(id, body.photo_url, body.description)
    return ApiResponse(data=ContainerStuffingPhotoRead.model_validate(photo))


@router.get("/{id}/packing-list", response_model=ApiResponse)
async def get_packing_list(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PACKING_LIST_EXPORT)),
    db: AsyncSession = Depends(get_db),
):
    service = ContainerService(db)
    data = await service.get_packing_list(id)
    return ApiResponse(data=data)
