from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import (
    AppError,
    BusinessError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.logging import setup_logging
from app.dependencies import create_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.state.redis = await create_redis_pool()
    yield
    await app.state.redis.aclose()


app = FastAPI(
    title="零食出口贸易 ERP",
    description="零食出口贸易 ERP 系统 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router)


# Exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"code": exc.code, "message": exc.message},
    )


@app.exception_handler(PermissionDeniedError)
async def permission_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=403,
        content={"code": exc.code, "message": exc.message},
    )


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={"code": exc.code, "message": exc.message},
    )


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(
        status_code=422,
        content={"code": exc.code, "message": exc.message, "detail": exc.detail},
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "message": exc.message},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
