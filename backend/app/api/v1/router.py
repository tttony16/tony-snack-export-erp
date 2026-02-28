from fastapi import APIRouter

from app.api.v1 import (
    auth,
    containers,
    customers,
    dashboard,
    logistics,
    outbound,
    product_categories,
    products,
    purchase_orders,
    sales_orders,
    statistics,
    suppliers,
    system,
    warehouse,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(product_categories.router)
api_router.include_router(products.router)
api_router.include_router(customers.router)
api_router.include_router(suppliers.router)
api_router.include_router(sales_orders.router)
api_router.include_router(purchase_orders.router)
api_router.include_router(warehouse.router)
api_router.include_router(containers.router)
api_router.include_router(outbound.router)
api_router.include_router(logistics.router)
api_router.include_router(dashboard.router)
api_router.include_router(statistics.router)
api_router.include_router(system.router)
