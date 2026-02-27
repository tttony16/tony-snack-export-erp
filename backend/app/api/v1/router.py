from fastapi import APIRouter

from app.api.v1 import auth, customers, products, purchase_orders, sales_orders, suppliers

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(customers.router)
api_router.include_router(suppliers.router)
api_router.include_router(sales_orders.router)
api_router.include_router(purchase_orders.router)
