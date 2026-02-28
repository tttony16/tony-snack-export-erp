import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.security import hash_password
from app.database import get_db
from app.main import app
from app.models import Base
from app.models.enums import UserRole
from app.models.product_category import ProductCategoryModel
from app.models.user import User

# Use a separate test database
TEST_DB_NAME = f"{settings.DB_NAME}_test"
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{TEST_DB_NAME}"
)

_ENUM_DEFS = [
    ("user_role", ["super_admin", "admin", "sales", "purchaser", "warehouse", "viewer"]),
    ("product_status", ["active", "inactive"]),
    (
        "currency_type",
        ["USD", "EUR", "JPY", "GBP", "THB", "VND", "MYR", "SGD", "PHP", "IDR", "RMB", "OTHER"],
    ),
    ("payment_method", ["TT", "LC", "DP", "DA"]),
    ("trade_term", ["FOB", "CIF", "CFR", "EXW", "DDP", "DAP"]),
    (
        "sales_order_status",
        [
            "draft",
            "confirmed",
            "purchasing",
            "goods_ready",
            "container_planned",
            "container_loaded",
            "shipped",
            "delivered",
            "completed",
            "abnormal",
        ],
    ),
    (
        "purchase_order_status",
        ["draft", "ordered", "partial_received", "fully_received", "completed", "cancelled"],
    ),
    ("unit_type", ["piece", "carton"]),
    ("inspection_result", ["passed", "failed", "partial_passed"]),
    ("container_plan_status", ["planning", "confirmed", "loading", "loaded", "shipped"]),
    ("container_type", ["20GP", "40GP", "40HQ", "reefer"]),
    (
        "logistics_status",
        [
            "booked",
            "customs_cleared",
            "loaded_on_ship",
            "in_transit",
            "arrived",
            "picked_up",
            "delivered",
        ],
    ),
    (
        "logistics_cost_type",
        ["ocean_freight", "customs_fee", "port_charge", "trucking_fee", "insurance_fee", "other"],
    ),
    (
        "audit_action",
        [
            "create",
            "update",
            "delete",
            "export",
            "status_change",
            "login",
            "logout",
            "permission_change",
        ],
    ),
]

_db_initialized = False


async def _ensure_test_db_ready():
    """Ensure test database exists with enums and tables. Idempotent."""
    global _db_initialized
    if _db_initialized:
        return
    _db_initialized = True

    # Create test database if needed
    admin_url = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        )
        if not result.scalar():
            await conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    await admin_engine.dispose()

    # Create enum types and tables
    setup_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with setup_engine.begin() as conn:
        for name, values in _ENUM_DEFS:
            enum = PG_ENUM(*values, name=name, create_type=False)
            await conn.run_sync(lambda sc, e=enum: e.create(sc, checkfirst=True))
        await conn.run_sync(Base.metadata.create_all)

    # Seed level-1 categories if the table is empty
    _NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    _CATEGORY_SEEDS = [
        ("puffed_food", "膨化食品", 0),
        ("candy", "糖果", 1),
        ("biscuit", "饼干", 2),
        ("nut", "坚果", 3),
        ("beverage", "饮料", 4),
        ("seasoning", "调味品", 5),
        ("instant_noodle", "方便面", 6),
        ("dried_fruit", "果干", 7),
        ("chocolate", "巧克力", 8),
        ("jelly", "果冻", 9),
        ("other", "其他", 10),
    ]
    factory = async_sessionmaker(setup_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        result = await session.execute(text("SELECT count(*) FROM product_categories"))
        if result.scalar() == 0:
            for key, name, sort in _CATEGORY_SEEDS:
                cat = ProductCategoryModel(
                    id=uuid.uuid5(_NAMESPACE, key),
                    name=name,
                    level=1,
                    parent_id=None,
                    sort_order=sort,
                )
                session.add(cat)
            await session.commit()
    await setup_engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh database session per test with its own engine."""
    await _ensure_test_db_ready()

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client with overridden dependencies."""

    async def _get_db():
        yield db_session

    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis = redis
    app.dependency_overrides[get_db] = _get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.pop(get_db, None)
    await redis.aclose()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create a super_admin user for testing."""
    user = User(
        username=f"admin_{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("testpass123"),
        display_name="Test Admin",
        email=f"admin_{uuid.uuid4().hex[:8]}@test.com",
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def viewer_user(db_session: AsyncSession) -> User:
    """Create a viewer user for testing."""
    user = User(
        username=f"viewer_{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("testpass123"),
        display_name="Test Viewer",
        email=f"viewer_{uuid.uuid4().hex[:8]}@test.com",
        role=UserRole.VIEWER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sales_user(db_session: AsyncSession) -> User:
    """Create a sales user for testing."""
    user = User(
        username=f"sales_{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("testpass123"),
        display_name="Test Sales",
        email=f"sales_{uuid.uuid4().hex[:8]}@test.com",
        role=UserRole.SALES,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def purchaser_user(db_session: AsyncSession) -> User:
    """Create a purchaser user for testing."""
    user = User(
        username=f"purchaser_{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("testpass123"),
        display_name="Test Purchaser",
        email=f"purchaser_{uuid.uuid4().hex[:8]}@test.com",
        role=UserRole.PURCHASER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def warehouse_user(db_session: AsyncSession) -> User:
    """Create a warehouse user for testing."""
    user = User(
        username=f"warehouse_{uuid.uuid4().hex[:8]}",
        password_hash=hash_password("testpass123"),
        display_name="Test Warehouse",
        email=f"warehouse_{uuid.uuid4().hex[:8]}@test.com",
        role=UserRole.WAREHOUSE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


def get_auth_headers(user: User) -> dict:
    """Generate auth headers for a user."""
    from app.core.security import create_access_token

    token = create_access_token(user.id, user.role.value)
    return {"Authorization": f"Bearer {token}"}
