import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permission
from app.core.permissions import Permission
from app.database import get_db
from app.models.enums import ProductStatus
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductListParams,
    ProductRead,
    ProductStatusUpdate,
    ProductUpdate,
)
from app.services.product_category_service import ProductCategoryService
from app.services.product_service import ProductService
from app.utils.excel import create_template, create_workbook, read_workbook

router = APIRouter(prefix="/products", tags=["商品管理"])

PRODUCT_EXPORT_HEADERS = [
    "SKU编码",
    "中文名称",
    "英文名称",
    "一级品类",
    "二级品类",
    "三级品类",
    "品牌",
    "规格",
    "单件重量(kg)",
    "单件体积(cbm)",
    "装箱规格",
    "保质期(天)",
    "状态",
]

PRODUCT_IMPORT_HEADERS = [
    "sku_code",
    "name_cn",
    "name_en",
    "category_name",
    "brand",
    "spec",
    "unit_weight_kg",
    "unit_volume_cbm",
    "packing_spec",
    "carton_length_cm",
    "carton_width_cm",
    "carton_height_cm",
    "carton_gross_weight_kg",
    "shelf_life_days",
]


@router.get("/brands", response_model=ApiResponse[list[str]])
async def list_brands(
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    brands = await service.get_brands()
    return ApiResponse(data=brands)


@router.get("", response_model=PaginatedResponse[ProductRead])
async def list_products(
    keyword: str | None = None,
    category_id: str | None = None,
    brand: str | None = None,
    product_status: ProductStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    parsed_category_id = uuid.UUID(category_id) if category_id else None
    params = ProductListParams(
        keyword=keyword,
        category_id=parsed_category_id,
        brand=brand,
        status=product_status,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.list_products(params)
    return PaginatedResponse(data=data)


@router.post("", response_model=ApiResponse[ProductRead], status_code=status.HTTP_201_CREATED)
async def create_product(
    body: ProductCreate,
    user: User = Depends(require_permission(Permission.PRODUCT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.create(body, user.id)
    read = ProductRead.model_validate(product)
    await service.fill_category_names(read)
    return ApiResponse(data=read)


@router.post("/import", response_model=ApiResponse)
async def import_products(
    file: UploadFile,
    user: User = Depends(require_permission(Permission.PRODUCT_IMPORT)),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    rows = read_workbook(content)
    service = ProductService(db)
    cat_service = ProductCategoryService(db)

    # Build name→id lookup from category tree
    all_cats = await cat_service.repo.get_all_ordered()
    name_to_id: dict[str, uuid.UUID] = {}
    for cat in all_cats:
        name_to_id[cat.name] = cat.id

    created = 0
    errors = []
    for i, row in enumerate(rows):
        try:
            category_name = str(row.get("category_name", row.get("category", "")))
            cat_id = name_to_id.get(category_name)
            if not cat_id:
                # Fall back: try matching against level-1 "其他" category
                cat_id = name_to_id.get("其他")
            if not cat_id:
                raise ValueError(f"品类 '{category_name}' 未找到")

            data = ProductCreate(
                sku_code=str(row.get("sku_code", "")),
                name_cn=str(row.get("name_cn", "")),
                name_en=str(row.get("name_en", "")),
                category_id=cat_id,
                spec=str(row.get("spec", "N/A")),
                unit_weight_kg=row.get("unit_weight_kg", 0.1),
                unit_volume_cbm=row.get("unit_volume_cbm", 0.001),
                packing_spec=str(row.get("packing_spec", "N/A")),
                carton_length_cm=row.get("carton_length_cm", 40),
                carton_width_cm=row.get("carton_width_cm", 30),
                carton_height_cm=row.get("carton_height_cm", 25),
                carton_gross_weight_kg=row.get("carton_gross_weight_kg", 10),
                shelf_life_days=int(row.get("shelf_life_days", 365)),
                brand=row.get("brand"),
            )
            await service.create(data, user.id)
            created += 1
        except Exception as e:
            errors.append({"row": i + 2, "error": str(e)})
    return ApiResponse(data={"created": created, "errors": errors})


@router.get("/export")
async def export_products(
    user: User = Depends(require_permission(Permission.PRODUCT_EXPORT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    params = ProductListParams(page=1, page_size=100)
    data = await service.list_products(params)
    rows = []
    for p in data.items:
        rows.append(
            [
                p.sku_code,
                p.name_cn,
                p.name_en,
                p.category_level1_name or "",
                p.category_level2_name or "",
                p.category_level3_name or "",
                p.brand or "",
                p.spec,
                str(p.unit_weight_kg),
                str(p.unit_volume_cbm),
                p.packing_spec,
                p.shelf_life_days,
                p.status.value if hasattr(p.status, "value") else str(p.status),
            ]
        )
    output = create_workbook("商品列表", PRODUCT_EXPORT_HEADERS, rows)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products.xlsx"},
    )


@router.get("/template")
async def download_template(
    user: User = Depends(require_permission(Permission.PRODUCT_IMPORT)),
):
    output = create_template("商品导入模板", PRODUCT_IMPORT_HEADERS)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=product_template.xlsx"},
    )


@router.get("/{id}", response_model=ApiResponse[ProductRead])
async def get_product(
    id: uuid.UUID,
    user: User = Depends(require_permission(Permission.PRODUCT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.get_by_id(id)
    read = ProductRead.model_validate(product)
    await service.fill_category_names(read)
    return ApiResponse(data=read)


@router.put("/{id}", response_model=ApiResponse[ProductRead])
async def update_product(
    id: uuid.UUID,
    body: ProductUpdate,
    user: User = Depends(require_permission(Permission.PRODUCT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.update(id, body, user.id)
    read = ProductRead.model_validate(product)
    await service.fill_category_names(read)
    return ApiResponse(data=read)


@router.patch("/{id}/status", response_model=ApiResponse[ProductRead])
async def update_product_status(
    id: uuid.UUID,
    body: ProductStatusUpdate,
    user: User = Depends(require_permission(Permission.PRODUCT_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.update_status(id, body.status, user.id)
    read = ProductRead.model_validate(product)
    await service.fill_category_names(read)
    return ApiResponse(data=read)
