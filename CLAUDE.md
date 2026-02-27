# 零食出口贸易 ERP 系统 — 项目开发规范

## 项目概述
零食出口贸易 ERP 系统，管理商品、客户、供应商、销售订单、采购、仓储、排柜、物流全流程。

## 技术栈
- **后端**: FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2
- **数据库**: PostgreSQL 16 + Redis 7
- **Python**: 3.12，依赖用 uv 管理
- **迁移**: Alembic (async)
- **测试**: pytest + pytest-asyncio + httpx

## 运行方式
```bash
# 启动 PG/Redis（在宿主机）
cd ~/workspace/snack-export-erp
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 在 obiwanfly-dev 容器内运行后端代码
docker exec -it -u vscode obiwanfly-dev bash
cd /workspace/snack-export-erp/backend
uv run alembic upgrade head          # 执行迁移
uv run python -m scripts.seed        # 初始化数据
uv run uvicorn app.main:app --reload # 启动开发服务器
uv run pytest -v                     # 运行测试
```

## 代码规范
- 分层架构：API Router → Service → Repository → Model
- 所有数据库操作用 async/await
- 统一使用 UUID 主键
- 枚举类型同时定义 Python Enum 和 PostgreSQL ENUM
- 异常处理用自定义异常类（AppError 体系）
- 权限校验用依赖注入 `require_permission(Permission.XXX)`
- 响应格式统一用 `ApiResponse` 包装

## 目录结构
```
backend/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── config.py        # 配置（pydantic-settings）
│   ├── database.py      # 数据库连接
│   ├── dependencies.py  # 全局依赖
│   ├── models/          # SQLAlchemy 模型
│   ├── schemas/         # Pydantic 请求/响应
│   ├── api/             # 路由层
│   ├── services/        # 业务逻辑层
│   ├── repositories/    # 数据访问层
│   ├── core/            # 安全、权限、异常、日志
│   └── utils/           # 工具函数
├── alembic/             # 数据库迁移
├── tests/               # 测试
├── scripts/             # 脚本（seed 等）
└── pyproject.toml
```

## 环境变量
所有配置通过 `.env` 文件加载，参见 `.env.example`。
