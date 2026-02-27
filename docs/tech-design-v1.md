# 零食出口贸易 ERP 系统 — 技术方案文档

> **版本**: v1.0
> **日期**: 2026-02-27
> **基于**: PRD v1.0
> **阶段**: 第一期（MVP + 排柜管理）

---

## 一、技术架构概览

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                          │
│              React 18 + TypeScript + Ant Design Pro       │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    Nginx（反向代理）                      │
│              静态文件托管 + API 路由转发                    │
└──────────────────────┬──────────────────────────────────┘
                       │ /api/v1/*
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI 后端服务                         │
│     Python 3.12 + SQLAlchemy 2.0 + Pydantic v2           │
│  ┌───────────┬──────────────┬────────────┬────────────┐  │
│  │ API Router│   Service    │ Repository │   Model    │  │
│  │  (路由层)  │  (业务逻辑层) │  (数据访问层) │  (数据模型) │  │
│  └───────────┴──────────────┴────────────┴────────────┘  │
└──────┬──────────────────────────────────┬───────────────┘
       │                                  │
       ▼                                  ▼
┌──────────────┐                 ┌──────────────┐
│ PostgreSQL 16│                 │   Redis 7    │
│   主数据库    │                 │ 会话/缓存     │
└──────────────┘                 └──────────────┘
```

### 1.2 技术栈选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **前端框架** | React | 18.x | 生态成熟，组件丰富 |
| **前端语言** | TypeScript | 5.x | 类型安全，减少运行时错误 |
| **UI 组件库** | Ant Design Pro | 6.x | 企业级中后台开箱即用 |
| **前端构建** | Vite | 5.x | 快速构建，HMR 体验好 |
| **后端框架** | FastAPI | 0.110+ | 异步高性能，自动 OpenAPI 文档 |
| **后端语言** | Python | 3.12 | 类型提示完善，生态丰富 |
| **ORM** | SQLAlchemy | 2.0 | Python ORM 标准，支持异步 |
| **数据校验** | Pydantic | 2.x | 与 FastAPI 深度集成 |
| **数据库** | PostgreSQL | 16 | 枚举类型、JSONB、全文检索 |
| **缓存** | Redis | 7.x | JWT 黑名单、会话缓存 |
| **数据库迁移** | Alembic | 1.13+ | SQLAlchemy 官方迁移工具 |
| **测试框架** | pytest + Playwright | - | 单元测试 + E2E 测试 |
| **容器化** | Docker Compose | - | 统一开发和部署环境 |
| **反向代理** | Nginx | 1.25+ | 静态文件 + API 转发 |

### 1.3 项目目录结构

```
snack-export-erp/
├── docs/                          # 文档
│   ├── PRD-v1.md
│   └── tech-design-v1.md
├── backend/                       # 后端代码
│   ├── alembic/                   # 数据库迁移
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI 入口
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库连接
│   │   ├── dependencies.py        # 公共依赖注入
│   │   ├── models/                # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # 基础模型（审计列）
│   │   │   ├── enums.py           # 枚举类型定义
│   │   │   ├── product.py
│   │   │   ├── customer.py
│   │   │   ├── supplier.py
│   │   │   ├── sales_order.py
│   │   │   ├── purchase_order.py
│   │   │   ├── warehouse.py
│   │   │   ├── container.py
│   │   │   ├── logistics.py
│   │   │   └── user.py
│   │   ├── schemas/               # Pydantic 请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── common.py          # 分页、排序等通用 schema
│   │   │   ├── product.py
│   │   │   ├── customer.py
│   │   │   ├── supplier.py
│   │   │   ├── sales_order.py
│   │   │   ├── purchase_order.py
│   │   │   ├── warehouse.py
│   │   │   ├── container.py
│   │   │   ├── logistics.py
│   │   │   └── user.py
│   │   ├── api/                   # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── deps.py            # 路由级依赖（认证、权限）
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py      # 路由聚合
│   │   │       ├── auth.py
│   │   │       ├── products.py
│   │   │       ├── customers.py
│   │   │       ├── suppliers.py
│   │   │       ├── sales_orders.py
│   │   │       ├── purchase_orders.py
│   │   │       ├── warehouse.py
│   │   │       ├── containers.py
│   │   │       ├── logistics.py
│   │   │       ├── dashboard.py
│   │   │       ├── statistics.py
│   │   │       └── system.py
│   │   ├── services/              # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── product_service.py
│   │   │   ├── customer_service.py
│   │   │   ├── supplier_service.py
│   │   │   ├── sales_order_service.py
│   │   │   ├── purchase_order_service.py
│   │   │   ├── warehouse_service.py
│   │   │   ├── container_service.py
│   │   │   ├── container_calculator.py  # 排柜计算引擎
│   │   │   ├── logistics_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── statistics_service.py
│   │   │   └── audit_service.py
│   │   ├── repositories/          # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # 通用 CRUD
│   │   │   ├── product_repo.py
│   │   │   ├── customer_repo.py
│   │   │   ├── supplier_repo.py
│   │   │   ├── sales_order_repo.py
│   │   │   ├── purchase_order_repo.py
│   │   │   ├── warehouse_repo.py
│   │   │   ├── container_repo.py
│   │   │   ├── logistics_repo.py
│   │   │   └── user_repo.py
│   │   ├── core/                  # 核心工具
│   │   │   ├── __init__.py
│   │   │   ├── security.py        # JWT、密码哈希
│   │   │   ├── permissions.py     # RBAC 权限检查
│   │   │   ├── exceptions.py      # 自定义异常
│   │   │   └── logging.py         # 结构化日志
│   │   └── utils/                 # 工具函数
│   │       ├── __init__.py
│   │       ├── code_generator.py  # 编号生成器
│   │       └── excel.py           # Excel 导入导出
│   ├── tests/                     # 测试
│   │   ├── conftest.py            # pytest fixtures
│   │   ├── factories.py           # 测试数据工厂
│   │   ├── unit/
│   │   │   ├── test_models/
│   │   │   ├── test_services/
│   │   │   └── test_utils/
│   │   ├── api/
│   │   │   └── test_v1/
│   │   └── integration/
│   ├── pyproject.toml             # 项目配置 + 依赖
│   └── Dockerfile
├── frontend/                      # 前端代码
│   ├── public/
│   ├── src/
│   │   ├── api/                   # API 请求封装
│   │   ├── components/            # 通用组件
│   │   ├── hooks/                 # 自定义 Hooks
│   │   ├── layouts/               # 布局组件
│   │   ├── pages/                 # 页面组件
│   │   │   ├── dashboard/
│   │   │   ├── products/
│   │   │   ├── customers/
│   │   │   ├── suppliers/
│   │   │   ├── sales-orders/
│   │   │   ├── purchase-orders/
│   │   │   ├── warehouse/
│   │   │   ├── containers/
│   │   │   ├── logistics/
│   │   │   ├── statistics/
│   │   │   └── system/
│   │   ├── store/                 # 状态管理
│   │   ├── types/                 # TypeScript 类型定义
│   │   ├── utils/                 # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── e2e/                           # E2E 测试
│   ├── playwright.config.ts
│   ├── fixtures/
│   └── tests/
│       ├── full-flow.spec.ts
│       ├── container-loading.spec.ts
│       ├── permissions.spec.ts
│       └── auth.spec.ts
├── nginx/                         # Nginx 配置
│   └── default.conf
├── docker-compose.yml             # 服务编排
├── docker-compose.dev.yml         # 开发环境覆盖
├── .env.example                   # 环境变量模板
├── .gitignore
└── CLAUDE.md                      # 项目级开发规范
```

### 1.4 分层架构说明

```
请求流向: HTTP Request → API Router → Service → Repository → Model/DB

API Router (路由层)
  ├── 参数解析与校验（Pydantic schema）
  ├── 认证与权限检查（依赖注入）
  ├── 调用 Service 层
  └── 返回统一响应格式

Service (业务逻辑层)
  ├── 业务规则校验（R01-R15）
  ├── 状态机转换
  ├── 跨模块协调
  ├── 事务管理
  └── 审计日志记录

Repository (数据访问层)
  ├── 通用 CRUD 操作
  ├── 复杂查询构建
  ├── 分页/排序/筛选
  └── 数据聚合统计

Model (数据模型层)
  ├── SQLAlchemy ORM 模型
  ├── 字段定义与约束
  ├── 关系映射
  └── 自动计算字段
```

---

## 二、数据库设计

### 2.1 PostgreSQL 枚举类型

```sql
-- 商品品类
CREATE TYPE product_category AS ENUM (
    'puffed_food',      -- 膨化食品
    'candy',            -- 糖果
    'biscuit',          -- 饼干
    'nut',              -- 坚果
    'beverage',         -- 饮料
    'seasoning',        -- 调味品
    'instant_noodle',   -- 方便面
    'dried_fruit',      -- 果脯蜜饯
    'chocolate',        -- 巧克力
    'jelly',            -- 果冻
    'other'             -- 其他
);

-- 商品状态
CREATE TYPE product_status AS ENUM ('active', 'inactive');

-- 销售订单状态
CREATE TYPE sales_order_status AS ENUM (
    'draft',            -- 新建
    'confirmed',        -- 已确认
    'purchasing',       -- 采购中
    'goods_ready',      -- 已到齐
    'container_planned',-- 已排柜
    'container_loaded', -- 已装柜
    'shipped',          -- 已出运
    'delivered',        -- 已签收
    'completed',        -- 已完成
    'abnormal'          -- 异常
);

-- 采购单状态
CREATE TYPE purchase_order_status AS ENUM (
    'draft',            -- 草稿
    'ordered',          -- 已下单
    'partial_received', -- 部分到货
    'fully_received',   -- 全部到货
    'completed',        -- 已完成
    'cancelled'         -- 已取消
);

-- 验货结果
CREATE TYPE inspection_result AS ENUM (
    'passed',           -- 合格
    'failed',           -- 不合格
    'partial_passed'    -- 部分合格
);

-- 排柜计划状态
CREATE TYPE container_plan_status AS ENUM (
    'planning',         -- 规划中
    'confirmed',        -- 已确认
    'loading',          -- 装柜中
    'loaded',           -- 已装柜
    'shipped'           -- 已出运
);

-- 柜型
CREATE TYPE container_type AS ENUM (
    '20GP', '40GP', '40HQ', 'reefer'
);

-- 物流状态
CREATE TYPE logistics_status AS ENUM (
    'booked',           -- 已订舱
    'customs_cleared',  -- 已报关
    'loaded_on_ship',   -- 已装船
    'in_transit',       -- 在途
    'arrived',          -- 已到港
    'picked_up',        -- 已提柜
    'delivered'         -- 已签收
);

-- 用户角色
CREATE TYPE user_role AS ENUM (
    'super_admin',      -- 超级管理员
    'admin',            -- 管理员
    'sales',            -- 业务员
    'purchaser',        -- 采购员
    'warehouse',        -- 仓库员
    'viewer'            -- 查看者
);

-- 结算币种
CREATE TYPE currency_type AS ENUM (
    'USD', 'EUR', 'JPY', 'GBP', 'THB', 'VND',
    'MYR', 'SGD', 'PHP', 'IDR', 'RMB', 'OTHER'
);

-- 付款方式
CREATE TYPE payment_method AS ENUM (
    'TT',              -- T/T 电汇
    'LC',              -- L/C 信用证
    'DP',              -- D/P 付款交单
    'DA'               -- D/A 承兑交单
);

-- 贸易术语
CREATE TYPE trade_term AS ENUM (
    'FOB', 'CIF', 'CFR', 'EXW', 'DDP', 'DAP'
);

-- 计量单位
CREATE TYPE unit_type AS ENUM ('piece', 'carton');

-- 物流费用类型
CREATE TYPE logistics_cost_type AS ENUM (
    'ocean_freight',    -- 海运费
    'customs_fee',      -- 报关费
    'port_charge',      -- 港杂费
    'trucking_fee',     -- 拖车费
    'insurance_fee',    -- 保险费
    'other'             -- 其他
);

-- 审计操作类型
CREATE TYPE audit_action AS ENUM (
    'create', 'update', 'delete', 'export',
    'status_change', 'login', 'logout', 'permission_change'
);
```

### 2.2 完整表结构

#### 2.2.1 系统表

**users — 用户表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希密码 |
| display_name | VARCHAR(100) | NOT NULL | 显示名称 |
| email | VARCHAR(255) | UNIQUE | 邮箱 |
| phone | VARCHAR(20) | | 手机号 |
| role | user_role | NOT NULL | 角色 |
| is_active | BOOLEAN | DEFAULT true | 是否启用 |
| last_login_at | TIMESTAMPTZ | | 最后登录时间 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT now() | 更新时间 |
| created_by | UUID | FK → users.id | 创建人 |
| updated_by | UUID | FK → users.id | 更新人 |

**audit_logs — 审计日志表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PK | 主键 |
| user_id | UUID | FK → users.id, NOT NULL | 操作人 |
| action | audit_action | NOT NULL | 操作类型 |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型（如 sales_order） |
| resource_id | VARCHAR(100) | | 资源 ID |
| detail | JSONB | | 操作详情（变更前后值） |
| ip_address | VARCHAR(45) | | 操作 IP |
| created_at | TIMESTAMPTZ | DEFAULT now() | 操作时间 |

**system_configs — 系统配置表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | SERIAL | PK | 主键 |
| config_key | VARCHAR(100) | UNIQUE, NOT NULL | 配置键 |
| config_value | JSONB | NOT NULL | 配置值 |
| description | TEXT | | 配置说明 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_by | UUID | FK → users.id | |

#### 2.2.2 主数据表

**products — 商品表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| sku_code | VARCHAR(50) | UNIQUE, NOT NULL | SKU 编码 |
| name_cn | VARCHAR(200) | NOT NULL | 中文名称 |
| name_en | VARCHAR(200) | NOT NULL | 英文名称 |
| category | product_category | NOT NULL | 品类 |
| brand | VARCHAR(100) | | 品牌 |
| barcode | VARCHAR(50) | | 商品条码 |
| spec | VARCHAR(200) | NOT NULL | 规格（如 500g/袋） |
| unit_weight_kg | NUMERIC(10,3) | NOT NULL | 单件毛重(kg) |
| unit_volume_cbm | NUMERIC(10,6) | NOT NULL | 单件体积(CBM) |
| packing_spec | VARCHAR(200) | NOT NULL | 装箱规格（如 24袋/箱） |
| carton_length_cm | NUMERIC(8,2) | NOT NULL | 外箱长(cm) |
| carton_width_cm | NUMERIC(8,2) | NOT NULL | 外箱宽(cm) |
| carton_height_cm | NUMERIC(8,2) | NOT NULL | 外箱高(cm) |
| carton_gross_weight_kg | NUMERIC(10,3) | NOT NULL | 外箱毛重(kg) |
| shelf_life_days | INTEGER | NOT NULL | 保质期(天) |
| default_purchase_price | NUMERIC(12,2) | | 默认采购价(RMB) |
| default_supplier_id | UUID | FK → suppliers.id | 默认供应商 |
| hs_code | VARCHAR(20) | | HS 编码 |
| image_url | VARCHAR(500) | | 商品图片 URL |
| status | product_status | NOT NULL, DEFAULT 'active' | 状态 |
| remark | TEXT | | 备注 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**customers — 客户表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| customer_code | VARCHAR(50) | UNIQUE, NOT NULL | 客户编码 |
| name | VARCHAR(200) | NOT NULL | 公司全称 |
| short_name | VARCHAR(100) | | 简称 |
| country | VARCHAR(100) | NOT NULL | 国家/地区 |
| address | TEXT | | 详细地址 |
| contact_person | VARCHAR(100) | NOT NULL | 联系人 |
| phone | VARCHAR(50) | | 联系电话 |
| email | VARCHAR(255) | | 邮箱 |
| currency | currency_type | NOT NULL | 结算币种 |
| payment_method | payment_method | NOT NULL | 付款方式 |
| payment_terms | VARCHAR(200) | | 付款条件 |
| trade_term | trade_term | | 贸易术语 |
| remark | TEXT | | 备注 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**suppliers — 供应商表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| supplier_code | VARCHAR(50) | UNIQUE, NOT NULL | 供应商编码 |
| name | VARCHAR(200) | NOT NULL | 供应商名称 |
| contact_person | VARCHAR(100) | NOT NULL | 联系人 |
| phone | VARCHAR(50) | NOT NULL | 联系电话 |
| address | TEXT | | 地址 |
| supply_categories | product_category[] | | 供应品类（PG 数组） |
| supply_brands | TEXT[] | | 供应品牌列表 |
| payment_terms | VARCHAR(200) | | 账期 |
| business_license | VARCHAR(100) | | 营业执照编号 |
| food_production_license | VARCHAR(100) | | SC 证号 |
| certificate_urls | TEXT[] | | 资质证书附件 URL 列表 |
| remark | TEXT | | 备注 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**supplier_products — 供应商-商品关联表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| supplier_id | UUID | FK → suppliers.id, NOT NULL | 供应商 |
| product_id | UUID | FK → products.id, NOT NULL | 商品 |
| supply_price | NUMERIC(12,2) | | 供货价 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| UNIQUE(supplier_id, product_id) | | | 联合唯一 |

#### 2.2.3 销售表

**sales_orders — 销售订单表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| order_no | VARCHAR(50) | UNIQUE, NOT NULL | 订单编号 SO-YYYYMMDD-NNN |
| customer_id | UUID | FK → customers.id, NOT NULL | 客户 |
| order_date | DATE | NOT NULL | 订单日期 |
| required_delivery_date | DATE | | 要求交货日期 |
| destination_port | VARCHAR(200) | NOT NULL | 目的港 |
| trade_term | trade_term | NOT NULL | 贸易术语 |
| currency | currency_type | NOT NULL | 结算币种 |
| payment_method | payment_method | NOT NULL | 付款方式 |
| payment_terms | VARCHAR(200) | | 付款条件 |
| status | sales_order_status | NOT NULL, DEFAULT 'draft' | 订单状态 |
| total_amount | NUMERIC(14,2) | DEFAULT 0 | 订单总金额（外币），自动计算 |
| total_quantity | INTEGER | DEFAULT 0 | 总件数/箱数，自动计算 |
| estimated_volume_cbm | NUMERIC(10,3) | DEFAULT 0 | 预估总体积，自动计算 |
| estimated_weight_kg | NUMERIC(12,3) | DEFAULT 0 | 预估总重量，自动计算 |
| remark | TEXT | | 备注 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**sales_order_items — 销售订单明细表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| sales_order_id | UUID | FK → sales_orders.id, NOT NULL | 所属订单 |
| product_id | UUID | FK → products.id, NOT NULL | 商品 |
| quantity | INTEGER | NOT NULL, CHECK > 0 | 销售数量 |
| unit | unit_type | NOT NULL | 单位 |
| unit_price | NUMERIC(12,2) | NOT NULL, CHECK >= 0 | 单价（外币） |
| amount | NUMERIC(14,2) | GENERATED (quantity * unit_price) | 金额（外币） |
| purchased_quantity | INTEGER | DEFAULT 0 | 已采购数量，自动统计 |
| received_quantity | INTEGER | DEFAULT 0 | 已入库数量，自动统计 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |

#### 2.2.4 采购表

**purchase_orders — 采购单表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| order_no | VARCHAR(50) | UNIQUE, NOT NULL | 采购单编号 PO-YYYYMMDD-NNN |
| supplier_id | UUID | FK → suppliers.id, NOT NULL | 供应商 |
| order_date | DATE | NOT NULL | 采购日期 |
| required_date | DATE | | 要求到货日期 |
| status | purchase_order_status | NOT NULL, DEFAULT 'draft' | 状态 |
| total_amount | NUMERIC(14,2) | DEFAULT 0 | 合计金额(RMB) |
| remark | TEXT | | 备注 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**purchase_order_items — 采购单明细表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| purchase_order_id | UUID | FK → purchase_orders.id, NOT NULL | 所属采购单 |
| product_id | UUID | FK → products.id, NOT NULL | 商品 |
| sales_order_item_id | UUID | FK → sales_order_items.id | 关联销售订单行（可选） |
| quantity | INTEGER | NOT NULL, CHECK > 0 | 采购数量 |
| unit | unit_type | NOT NULL | 单位 |
| unit_price | NUMERIC(12,2) | NOT NULL, CHECK >= 0 | 采购单价(RMB) |
| amount | NUMERIC(14,2) | GENERATED (quantity * unit_price) | 金额(RMB) |
| received_quantity | INTEGER | DEFAULT 0 | 已到货数量 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |

**purchase_order_sales_orders — 采购单-销售订单 M2M 关联表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| purchase_order_id | UUID | FK → purchase_orders.id, NOT NULL | 采购单 |
| sales_order_id | UUID | FK → sales_orders.id, NOT NULL | 销售订单 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| UNIQUE(purchase_order_id, sales_order_id) | | | 联合唯一 |

#### 2.2.5 仓储表

**receiving_notes — 收货单表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| note_no | VARCHAR(50) | UNIQUE, NOT NULL | 收货单编号 RCV-YYYYMMDD-NNN |
| purchase_order_id | UUID | FK → purchase_orders.id, NOT NULL | 关联采购单 |
| receiving_date | DATE | NOT NULL | 收货日期 |
| receiver | VARCHAR(100) | NOT NULL | 收货人 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**receiving_note_items — 收货单明细表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| receiving_note_id | UUID | FK → receiving_notes.id, NOT NULL | 所属收货单 |
| purchase_order_item_id | UUID | FK → purchase_order_items.id, NOT NULL | 关联采购单明细行 |
| product_id | UUID | FK → products.id, NOT NULL | 商品 |
| expected_quantity | INTEGER | NOT NULL | 应收数量 |
| actual_quantity | INTEGER | NOT NULL | 实收数量 |
| inspection_result | inspection_result | NOT NULL | 验货结果 |
| failed_quantity | INTEGER | DEFAULT 0 | 不合格数量 |
| failure_reason | TEXT | | 不合格原因 |
| production_date | DATE | NOT NULL | 生产日期 |
| batch_no | VARCHAR(50) | NOT NULL | 批次号 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |

**inventory_records — 库存记录表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| product_id | UUID | FK → products.id, NOT NULL | 商品 |
| sales_order_id | UUID | FK → sales_orders.id | 关联销售订单（可选） |
| receiving_note_item_id | UUID | FK → receiving_note_items.id, NOT NULL | 来源收货明细 |
| batch_no | VARCHAR(50) | NOT NULL | 批次号 |
| production_date | DATE | NOT NULL | 生产日期 |
| quantity | INTEGER | NOT NULL | 合格入库数量 |
| available_quantity | INTEGER | NOT NULL | 可用数量（减去已排柜的） |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |

#### 2.2.6 排柜表

**container_plans — 排柜计划表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| plan_no | VARCHAR(50) | UNIQUE, NOT NULL | 排柜计划编号 CL-YYYYMMDD-NNN |
| container_type | container_type | NOT NULL | 柜型 |
| container_count | INTEGER | NOT NULL, DEFAULT 1 | 柜数量 |
| destination_port | VARCHAR(200) | NOT NULL | 目的港 |
| status | container_plan_status | NOT NULL, DEFAULT 'planning' | 状态 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**container_plan_sales_orders — 排柜计划-销售订单 M2M 关联表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| container_plan_id | UUID | FK → container_plans.id, NOT NULL | 排柜计划 |
| sales_order_id | UUID | FK → sales_orders.id, NOT NULL | 销售订单 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| UNIQUE(container_plan_id, sales_order_id) | | | 联合唯一 |

**container_plan_items — 配载明细表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| container_plan_id | UUID | FK → container_plans.id, NOT NULL | 排柜计划 |
| container_seq | INTEGER | NOT NULL | 柜序号（第几个柜子） |
| product_id | UUID | FK → products.id, NOT NULL | 商品 |
| sales_order_id | UUID | FK → sales_orders.id, NOT NULL | 来源销售订单 |
| quantity | INTEGER | NOT NULL, CHECK > 0 | 装柜数量 |
| volume_cbm | NUMERIC(10,4) | NOT NULL | 占用体积 |
| weight_kg | NUMERIC(12,3) | NOT NULL | 占用重量 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |

**container_stuffing_records — 装柜记录表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| container_plan_id | UUID | FK → container_plans.id, NOT NULL | 排柜计划 |
| container_seq | INTEGER | NOT NULL | 柜序号 |
| container_no | VARCHAR(20) | NOT NULL | 柜号（集装箱号） |
| seal_no | VARCHAR(20) | NOT NULL | 铅封号 |
| stuffing_date | DATE | NOT NULL | 装柜日期 |
| stuffing_location | VARCHAR(200) | | 装柜地点 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**container_stuffing_photos — 装柜照片表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| stuffing_record_id | UUID | FK → container_stuffing_records.id, NOT NULL | 装柜记录 |
| photo_url | VARCHAR(500) | NOT NULL | 照片 URL |
| description | VARCHAR(200) | | 照片描述 |
| created_at | TIMESTAMPTZ | DEFAULT now() | |

#### 2.2.7 物流表

**logistics_records — 物流记录表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| logistics_no | VARCHAR(50) | UNIQUE, NOT NULL | 物流编号 LOG-YYYYMMDD-NNN |
| container_plan_id | UUID | FK → container_plans.id, NOT NULL | 关联排柜计划 |
| shipping_company | VARCHAR(200) | | 船公司 |
| vessel_voyage | VARCHAR(200) | | 船名航次 |
| bl_no | VARCHAR(100) | | 提单号 |
| port_of_loading | VARCHAR(200) | NOT NULL | 起运港 |
| port_of_discharge | VARCHAR(200) | NOT NULL | 目的港 |
| etd | DATE | | 预计开船日 |
| eta | DATE | | 预计到港日 |
| actual_departure_date | DATE | | 实际开船日 |
| actual_arrival_date | DATE | | 实际到港日 |
| status | logistics_status | NOT NULL, DEFAULT 'booked' | 物流状态 |
| customs_declaration_no | VARCHAR(100) | | 报关单号 |
| total_cost | NUMERIC(14,2) | DEFAULT 0 | 物流费用合计 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |
| created_by | UUID | FK → users.id | |
| updated_by | UUID | FK → users.id | |

**logistics_costs — 物流费用明细表**

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK | 主键 |
| logistics_record_id | UUID | FK → logistics_records.id, NOT NULL | 关联物流记录 |
| cost_type | logistics_cost_type | NOT NULL | 费用类型 |
| amount | NUMERIC(12,2) | NOT NULL | 金额 |
| currency | currency_type | NOT NULL | 币种 |
| remark | TEXT | | |
| created_at | TIMESTAMPTZ | DEFAULT now() | |
| updated_at | TIMESTAMPTZ | DEFAULT now() | |

### 2.3 关键索引设计

```sql
-- 商品
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_sku_code ON products(sku_code);

-- 客户
CREATE INDEX idx_customers_country ON customers(country);
CREATE INDEX idx_customers_code ON customers(customer_code);

-- 供应商
CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);

-- 销售订单
CREATE INDEX idx_sales_orders_status ON sales_orders(status);
CREATE INDEX idx_sales_orders_customer ON sales_orders(customer_id);
CREATE INDEX idx_sales_orders_order_date ON sales_orders(order_date);
CREATE INDEX idx_sales_orders_order_no ON sales_orders(order_no);
CREATE INDEX idx_sales_order_items_order ON sales_order_items(sales_order_id);
CREATE INDEX idx_sales_order_items_product ON sales_order_items(product_id);

-- 采购单
CREATE INDEX idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX idx_purchase_orders_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_order_date ON purchase_orders(order_date);
CREATE INDEX idx_purchase_order_items_order ON purchase_order_items(purchase_order_id);
CREATE INDEX idx_purchase_order_items_product ON purchase_order_items(product_id);
CREATE INDEX idx_purchase_order_items_so_item ON purchase_order_items(sales_order_item_id);

-- 收货单
CREATE INDEX idx_receiving_notes_po ON receiving_notes(purchase_order_id);
CREATE INDEX idx_receiving_note_items_note ON receiving_note_items(receiving_note_id);

-- 库存
CREATE INDEX idx_inventory_product ON inventory_records(product_id);
CREATE INDEX idx_inventory_sales_order ON inventory_records(sales_order_id);
CREATE INDEX idx_inventory_batch ON inventory_records(batch_no);

-- 排柜
CREATE INDEX idx_container_plans_status ON container_plans(status);
CREATE INDEX idx_container_plan_items_plan ON container_plan_items(container_plan_id);
CREATE INDEX idx_container_plan_items_seq ON container_plan_items(container_plan_id, container_seq);
CREATE INDEX idx_stuffing_records_plan ON container_stuffing_records(container_plan_id);

-- 物流
CREATE INDEX idx_logistics_status ON logistics_records(status);
CREATE INDEX idx_logistics_container_plan ON logistics_records(container_plan_id);
CREATE INDEX idx_logistics_bl_no ON logistics_records(bl_no);
CREATE INDEX idx_logistics_costs_record ON logistics_costs(logistics_record_id);

-- 审计日志
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### 2.4 ER 关系说明

```
products ──────────── supplier_products ──────────── suppliers
    │                                                    │
    │ (1:N)                                              │ (1:N)
    ▼                                                    ▼
sales_order_items ──── sales_orders              purchase_orders
    │                      │                          │
    │                      │ (M2M)                    │ (1:N)
    │                      ▼                          ▼
    │            purchase_order_sales_orders    purchase_order_items
    │                                                │
    │                                                │ (1:N)
    │                                                ▼
    │                                         receiving_notes
    │                                                │
    │                                                │ (1:N)
    │                                                ▼
    │                                         receiving_note_items
    │                                                │
    │                                                │ (1:N)
    │                                                ▼
    │                                         inventory_records
    │
    ├── (来源) ────────────── container_plan_items
    │                              │
    │                              │ (N:1)
    │                              ▼
sales_orders (M2M) ──── container_plan_sales_orders ──── container_plans
                                                              │
                                                              │ (1:N)
                                                              ├── container_stuffing_records
                                                              │        │ (1:N)
                                                              │        └── container_stuffing_photos
                                                              │
                                                              └── logistics_records
                                                                       │ (1:N)
                                                                       └── logistics_costs
```

核心关系链路：**销售订单 → 采购单 → 收货单 → 库存 → 排柜计划 → 物流记录**

---

## 三、RESTful API 设计

### 3.1 API 总体约定

**基础路径**: `/api/v1`

**认证方式**: JWT Bearer Token
```
Authorization: Bearer <access_token>
```

**分页约定**:
```
GET /api/v1/products?page=1&page_size=20
```
- `page`: 页码，从 1 开始，默认 1
- `page_size`: 每页条数，默认 20，最大 100

**排序约定**:
```
GET /api/v1/products?sort_by=created_at&sort_order=desc
```
- `sort_by`: 排序字段
- `sort_order`: `asc` 或 `desc`，默认 `desc`

**筛选约定**: 通过查询参数传递筛选条件
```
GET /api/v1/sales-orders?status=purchasing&customer_id=xxx&date_from=2026-01-01&date_to=2026-12-31
```

**统一响应格式**:

成功（单个对象）:
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

成功（列表/分页）:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

错误:
```json
{
  "code": 40001,
  "message": "参数校验失败",
  "detail": {
    "field": "quantity",
    "reason": "采购数量不能超过未采购需求"
  }
}
```

### 3.2 API 端点列表

#### Auth — 认证模块（4 个端点）

| Method | Path | 说明 |
|--------|------|------|
| POST | /api/v1/auth/login | 用户登录，返回 JWT |
| POST | /api/v1/auth/logout | 用户登出，令牌加入黑名单 |
| POST | /api/v1/auth/refresh | 刷新访问令牌 |
| GET | /api/v1/auth/me | 获取当前用户信息 |

#### Products — 商品管理（8 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/products | 商品列表（分页、筛选、搜索） |
| POST | /api/v1/products | 新增商品 |
| GET | /api/v1/products/{id} | 商品详情 |
| PUT | /api/v1/products/{id} | 编辑商品 |
| PATCH | /api/v1/products/{id}/status | 启用/停用商品 |
| POST | /api/v1/products/import | Excel 批量导入 |
| GET | /api/v1/products/export | 批量导出（仅超级管理员） |
| GET | /api/v1/products/template | 下载导入模板 |

#### Customers — 客户管理（6 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/customers | 客户列表 |
| POST | /api/v1/customers | 新增客户 |
| GET | /api/v1/customers/{id} | 客户详情（含历史订单） |
| PUT | /api/v1/customers/{id} | 编辑客户 |
| GET | /api/v1/customers/export | 批量导出（仅超级管理员） |
| GET | /api/v1/customers/{id}/orders | 客户历史订单列表 |

#### Suppliers — 供应商管理（8 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/suppliers | 供应商列表 |
| POST | /api/v1/suppliers | 新增供应商 |
| GET | /api/v1/suppliers/{id} | 供应商详情（含采购历史） |
| PUT | /api/v1/suppliers/{id} | 编辑供应商 |
| GET | /api/v1/suppliers/export | 批量导出（仅超级管理员） |
| GET | /api/v1/suppliers/{id}/purchase-orders | 供应商采购单历史 |
| POST | /api/v1/suppliers/{id}/products | 关联商品 |
| DELETE | /api/v1/suppliers/{id}/products/{product_id} | 取消关联商品 |

#### Sales Orders — 销售订单管理（10 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/sales-orders | 订单列表（分页、按状态/客户/日期筛选） |
| POST | /api/v1/sales-orders | 创建订单 |
| GET | /api/v1/sales-orders/{id} | 订单详情（含履约链路） |
| PUT | /api/v1/sales-orders/{id} | 编辑订单（仅 draft/confirmed） |
| POST | /api/v1/sales-orders/{id}/confirm | 确认订单 → 触发 R10 |
| POST | /api/v1/sales-orders/{id}/generate-purchase | 一键生成采购单草稿 |
| GET | /api/v1/sales-orders/{id}/fulfillment | 获取订单履约链路 |
| GET | /api/v1/sales-orders/export | 批量导出（仅超级管理员） |
| GET | /api/v1/sales-orders/kanban | 订单进度看板（按状态分组） |
| PATCH | /api/v1/sales-orders/{id}/status | 手动更新状态（异常处理） |

#### Purchase Orders — 采购管理（8 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/purchase-orders | 采购单列表 |
| POST | /api/v1/purchase-orders | 创建采购单（独立或关联销售订单） |
| GET | /api/v1/purchase-orders/{id} | 采购单详情 |
| PUT | /api/v1/purchase-orders/{id} | 编辑采购单（仅 draft） |
| POST | /api/v1/purchase-orders/{id}/confirm | 确认下单 |
| POST | /api/v1/purchase-orders/{id}/cancel | 取消采购单 |
| POST | /api/v1/purchase-orders/{id}/link-sales-orders | 补充关联销售订单 |
| GET | /api/v1/purchase-orders/{id}/receiving-notes | 关联的收货单 |

#### Warehouse — 仓储/收货管理（9 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/warehouse/receiving-notes | 收货单列表 |
| POST | /api/v1/warehouse/receiving-notes | 创建收货单 |
| GET | /api/v1/warehouse/receiving-notes/{id} | 收货单详情 |
| PUT | /api/v1/warehouse/receiving-notes/{id} | 编辑收货单 |
| GET | /api/v1/warehouse/inventory | 库存查询（按商品维度） |
| GET | /api/v1/warehouse/inventory/by-order | 库存查询（按销售订单维度） |
| GET | /api/v1/warehouse/inventory/pending-inspection | 待验货清单 |
| GET | /api/v1/warehouse/inventory/readiness/{sales_order_id} | 齐套检查 |
| GET | /api/v1/warehouse/inventory/export | 库存导出 |

#### Container Loading — 排柜管理（14 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/containers | 排柜计划列表 |
| POST | /api/v1/containers | 创建排柜计划 |
| GET | /api/v1/containers/{id} | 排柜计划详情 |
| PUT | /api/v1/containers/{id} | 编辑排柜计划 |
| POST | /api/v1/containers/{id}/recommend-type | 柜型推荐 |
| POST | /api/v1/containers/{id}/items | 添加配载明细 |
| PUT | /api/v1/containers/{id}/items/{item_id} | 编辑配载明细 |
| DELETE | /api/v1/containers/{id}/items/{item_id} | 删除配载明细 |
| GET | /api/v1/containers/{id}/summary | 柜子利用率汇总 |
| POST | /api/v1/containers/{id}/validate | 校验配载方案（R06-R09） |
| POST | /api/v1/containers/{id}/confirm | 确认配载方案 → 触发 R12 |
| POST | /api/v1/containers/{id}/stuffing | 录入装柜记录 → 触发 R13 |
| POST | /api/v1/containers/{id}/stuffing/photos | 上传装柜照片 |
| GET | /api/v1/containers/{id}/packing-list | 导出装箱单（Excel/PDF） |

#### Logistics — 物流管理（9 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/logistics | 物流记录列表 |
| POST | /api/v1/logistics | 创建物流记录 |
| GET | /api/v1/logistics/{id} | 物流记录详情 |
| PUT | /api/v1/logistics/{id} | 编辑物流记录 |
| PATCH | /api/v1/logistics/{id}/status | 更新物流状态 → 触发 R14/R15 |
| POST | /api/v1/logistics/{id}/costs | 添加费用明细 |
| PUT | /api/v1/logistics/{id}/costs/{cost_id} | 编辑费用明细 |
| DELETE | /api/v1/logistics/{id}/costs/{cost_id} | 删除费用明细 |
| GET | /api/v1/logistics/kanban | 物流看板 |

#### Dashboard — 仪表盘（4 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/dashboard/overview | 订单概览（各状态数量） |
| GET | /api/v1/dashboard/todos | 待办事项列表 |
| GET | /api/v1/dashboard/in-transit | 在途货柜列表 |
| GET | /api/v1/dashboard/expiry-warnings | 保质期预警 |

#### Statistics — 数据统计（5 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/statistics/sales-summary | 销售订单汇总（按月/按客户） |
| GET | /api/v1/statistics/purchase-summary | 采购汇总（按月/按供应商） |
| GET | /api/v1/statistics/container-summary | 出柜统计（按月/按柜型） |
| GET | /api/v1/statistics/customer-ranking | 客户排名 |
| GET | /api/v1/statistics/product-ranking | 商品排名 |

#### System — 系统管理（9 个端点）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/v1/system/users | 用户列表 |
| POST | /api/v1/system/users | 创建用户 |
| GET | /api/v1/system/users/{id} | 用户详情 |
| PUT | /api/v1/system/users/{id} | 编辑用户 |
| PATCH | /api/v1/system/users/{id}/role | 修改角色 |
| PATCH | /api/v1/system/users/{id}/status | 启用/停用用户 |
| GET | /api/v1/system/audit-logs | 操作日志列表 |
| GET | /api/v1/system/configs | 系统配置列表 |
| PUT | /api/v1/system/configs/{key} | 更新系统配置 |

### 3.3 状态码规范

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | GET 成功、PUT/PATCH 更新成功 |
| 201 | Created | POST 创建成功 |
| 204 | No Content | DELETE 成功 |
| 400 | Bad Request | 请求参数格式错误 |
| 401 | Unauthorized | 未登录或 Token 过期 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如编码重复） |
| 422 | Unprocessable Entity | 业务规则校验失败 |
| 500 | Internal Server Error | 服务器内部错误 |

### 3.4 错误码命名规范

错误码格式: `{HTTP状态码}{模块编号}{序号}`

| 模块 | 编号 | 示例 |
|------|------|------|
| 通用 | 00 | 40001（参数缺失）、40002（参数格式错误） |
| 认证 | 01 | 40101（Token 过期）、40102（Token 无效）、40301（无权限） |
| 商品 | 10 | 40910（SKU 重复）、42210（商品已停用不可操作） |
| 客户 | 11 | 40911（客户编码重复） |
| 供应商 | 12 | 40912（供应商编码重复） |
| 销售订单 | 20 | 42220（订单状态不允许编辑）、42221（状态转换非法） |
| 采购单 | 30 | 42230（R02 采购数量超限）、42231（状态不允许编辑） |
| 仓储 | 40 | 42240（R03 实收数量超限） |
| 排柜 | 50 | 42250（R04 订单状态不符）、42251（R06 体积超限）、42252（R07 重量超限）、42253（R08 目的港不一致） |
| 物流 | 60 | 42260（物流状态转换非法） |
| 系统 | 90 | 40390（仅超级管理员可操作） |

---

## 四、认证与权限（RBAC）

### 4.1 JWT 认证流程

```
1. 登录
   POST /api/v1/auth/login { username, password }
   → 验证密码（bcrypt）
   → 生成 access_token（有效期 2 小时）+ refresh_token（有效期 7 天）
   → 返回两个 Token

2. 请求认证
   客户端在 Header 中携带: Authorization: Bearer <access_token>
   → 后端中间件解码 JWT
   → 检查 Token 是否在 Redis 黑名单中
   → 提取 user_id、role
   → 注入到请求上下文

3. Token 刷新
   POST /api/v1/auth/refresh { refresh_token }
   → 验证 refresh_token 有效性
   → 生成新的 access_token
   → 返回新 Token

4. 登出
   POST /api/v1/auth/logout
   → 将当前 access_token 加入 Redis 黑名单（TTL = Token 剩余有效期）
```

**JWT Payload 结构**:
```json
{
  "sub": "user_uuid",
  "role": "sales",
  "exp": 1709136000,
  "iat": 1709128800,
  "jti": "unique_token_id"
}
```

### 4.2 权限实现方案

**6 个角色定义**:

| 角色枚举值 | 角色名 | 权限等级 |
|-----------|--------|---------|
| super_admin | 超级管理员 | 全部权限 + 批量导出 + 用户管理 |
| admin | 管理员 | 全部业务权限（不含批量导出和用户管理） |
| sales | 业务员 | 客户、销售订单、排柜查看/创建、物流 |
| purchaser | 采购员 | 供应商、采购单、关联的销售订单查看 |
| warehouse | 仓库员 | 收货验货、库存查看、装柜记录、装箱单 |
| viewer | 查看者 | 全部只读 |

**权限装饰器设计**:

```python
# app/core/permissions.py
from enum import Enum
from functools import wraps

class Permission(str, Enum):
    # 商品
    PRODUCT_VIEW = "product:view"
    PRODUCT_EDIT = "product:edit"
    PRODUCT_IMPORT = "product:import"
    PRODUCT_EXPORT = "product:export"
    # 客户
    CUSTOMER_VIEW = "customer:view"
    CUSTOMER_EDIT = "customer:edit"
    CUSTOMER_EXPORT = "customer:export"
    # 供应商
    SUPPLIER_VIEW = "supplier:view"
    SUPPLIER_EDIT = "supplier:edit"
    SUPPLIER_EXPORT = "supplier:export"
    # 销售订单
    SALES_ORDER_VIEW = "sales_order:view"
    SALES_ORDER_EDIT = "sales_order:edit"
    SALES_ORDER_CONFIRM = "sales_order:confirm"
    SALES_ORDER_EXPORT = "sales_order:export"
    # 采购单
    PURCHASE_ORDER_VIEW = "purchase_order:view"
    PURCHASE_ORDER_EDIT = "purchase_order:edit"
    PURCHASE_ORDER_CONFIRM = "purchase_order:confirm"
    # 仓储
    WAREHOUSE_OPERATE = "warehouse:operate"
    INVENTORY_VIEW = "inventory:view"
    # 排柜
    CONTAINER_VIEW = "container:view"
    CONTAINER_EDIT = "container:edit"
    CONTAINER_CONFIRM = "container:confirm"
    CONTAINER_STUFFING = "container:stuffing"
    PACKING_LIST_EXPORT = "packing_list:export"
    # 物流
    LOGISTICS_VIEW = "logistics:view"
    LOGISTICS_EDIT = "logistics:edit"
    # 系统
    USER_MANAGE = "user:manage"
    AUDIT_LOG_VIEW = "audit_log:view"
    SYSTEM_CONFIG = "system:config"
    STATISTICS_VIEW = "statistics:view"

# 角色-权限映射表
ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "super_admin": set(Permission),  # 全部权限
    "admin": {
        Permission.PRODUCT_VIEW, Permission.PRODUCT_EDIT, Permission.PRODUCT_IMPORT,
        Permission.CUSTOMER_VIEW, Permission.CUSTOMER_EDIT,
        Permission.SUPPLIER_VIEW, Permission.SUPPLIER_EDIT,
        Permission.SALES_ORDER_VIEW, Permission.SALES_ORDER_EDIT,
        Permission.SALES_ORDER_CONFIRM,
        Permission.PURCHASE_ORDER_VIEW, Permission.PURCHASE_ORDER_EDIT,
        Permission.PURCHASE_ORDER_CONFIRM,
        Permission.WAREHOUSE_OPERATE, Permission.INVENTORY_VIEW,
        Permission.CONTAINER_VIEW, Permission.CONTAINER_EDIT,
        Permission.CONTAINER_CONFIRM, Permission.CONTAINER_STUFFING,
        Permission.PACKING_LIST_EXPORT,
        Permission.LOGISTICS_VIEW, Permission.LOGISTICS_EDIT,
        Permission.AUDIT_LOG_VIEW, Permission.STATISTICS_VIEW,
    },
    "sales": {
        Permission.PRODUCT_VIEW,
        Permission.CUSTOMER_VIEW, Permission.CUSTOMER_EDIT,
        Permission.SALES_ORDER_VIEW, Permission.SALES_ORDER_EDIT,
        Permission.PURCHASE_ORDER_VIEW,  # 只能看关联的
        Permission.INVENTORY_VIEW,        # 只能看关联的
        Permission.CONTAINER_VIEW, Permission.CONTAINER_EDIT,
        Permission.PACKING_LIST_EXPORT,
        Permission.LOGISTICS_VIEW, Permission.LOGISTICS_EDIT,
    },
    "purchaser": {
        Permission.PRODUCT_VIEW,
        Permission.SUPPLIER_VIEW, Permission.SUPPLIER_EDIT,
        Permission.SALES_ORDER_VIEW,      # 只能看关联的
        Permission.PURCHASE_ORDER_VIEW, Permission.PURCHASE_ORDER_EDIT,
        Permission.INVENTORY_VIEW,        # 只能看关联的
    },
    "warehouse": {
        Permission.PRODUCT_VIEW,
        Permission.SALES_ORDER_VIEW,      # 只能看关联的
        Permission.INVENTORY_VIEW,
        Permission.WAREHOUSE_OPERATE,
        Permission.CONTAINER_VIEW,
        Permission.CONTAINER_STUFFING,
        Permission.PACKING_LIST_EXPORT,
    },
    "viewer": {
        Permission.PRODUCT_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.SUPPLIER_VIEW,
        Permission.SALES_ORDER_VIEW,
        Permission.PURCHASE_ORDER_VIEW,
        Permission.INVENTORY_VIEW,
        Permission.CONTAINER_VIEW,
        Permission.LOGISTICS_VIEW,
    },
}
```

**API 路由中使用权限依赖**:

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from app.core.permissions import Permission, ROLE_PERMISSIONS

def require_permission(permission: Permission):
    """权限检查依赖"""
    def checker(current_user = Depends(get_current_user)):
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": 40301, "message": "无权限执行此操作"}
            )
        return current_user
    return checker

# 使用示例
@router.post("/products")
async def create_product(
    data: ProductCreate,
    user = Depends(require_permission(Permission.PRODUCT_EDIT))
):
    ...
```

### 4.3 数据级隔离策略

对于标注"只能看关联的"权限，在 Repository 层自动追加过滤条件：

```python
# 采购员只能看到自己创建的采购单关联的销售订单
async def get_sales_orders(self, user, filters):
    query = select(SalesOrder)
    if user.role == "purchaser":
        # 只返回与该用户采购单关联的销售订单
        query = query.join(PurchaseOrderSalesOrder).join(PurchaseOrder).where(
            PurchaseOrder.created_by == user.id
        )
    elif user.role == "warehouse":
        # 只返回有收货单关联的销售订单
        query = query.join(SalesOrderItem).join(PurchaseOrderItem).join(
            ReceivingNoteItem
        ).join(ReceivingNote).where(
            ReceivingNote.created_by == user.id
        )
    return await self.paginate(query, filters)
```

### 4.4 敏感操作控制

所有批量导出接口强制校验 `super_admin` 角色：

```python
def require_super_admin(current_user = Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40390, "message": "仅超级管理员可执行此操作"}
        )
    return current_user

@router.get("/products/export")
async def export_products(user = Depends(require_super_admin)):
    # 记录审计日志
    await audit_service.log(user.id, "export", "product", detail="批量导出商品")
    ...
```

---

## 五、核心业务逻辑

### 5.1 状态机设计

#### 销售订单状态机

```
draft ──── confirm ────→ confirmed
                              │
                         (自动 R10)
                              ▼
                         purchasing
                              │
                      (自动 R11, 全部入库)
                              ▼
                         goods_ready
                              │
                      (自动 R12, 排柜确认)
                              ▼
                      container_planned
                              │
                      (自动 R13, 装柜完成)
                              ▼
                      container_loaded
                              │
                      (自动 R14, 已装船)
                              ▼
                          shipped
                              │
                      (自动 R15, 已签收)
                              ▼
                         delivered
                              │
                        (手动确认)
                              ▼
                         completed

任意状态 ──── mark_abnormal ────→ abnormal
```

合法转换表：

| 当前状态 | 允许转换到 | 触发方式 |
|---------|-----------|---------|
| draft | confirmed | 手动确认 |
| confirmed | purchasing | 自动（R10，确认后立即触发） |
| purchasing | goods_ready | 自动（R11，全部到货） |
| goods_ready | container_planned | 自动（R12，排柜确认） |
| container_planned | container_loaded | 自动（R13，装柜完成） |
| container_loaded | shipped | 自动（R14，物流已装船） |
| shipped | delivered | 自动（R15，物流已签收） |
| delivered | completed | 手动确认 |
| * | abnormal | 手动标记 |

#### 采购单状态机

```
draft ──── confirm ────→ ordered
                            │
                     (收货单创建, 部分到货)
                            ▼
                      partial_received
                            │
                     (全部到货)
                            ▼
                      fully_received
                            │
                       (手动确认)
                            ▼
                        completed

draft/ordered ──── cancel ────→ cancelled
```

#### 排柜计划状态机

```
planning ──── confirm ────→ confirmed
                               │
                          (开始装柜)
                               ▼
                            loading
                               │
                      (装柜完成, 录入柜号+铅封号)
                               ▼
                            loaded
                               │
                       (物流已装船)
                               ▼
                            shipped
```

#### 物流状态机

```
booked → customs_cleared → loaded_on_ship → in_transit → arrived → picked_up → delivered
```

状态只能按顺序前进，不可跳过或回退。

### 5.2 业务规则实现方案（R01-R15）

#### R01：采购单可以关联销售订单，也可以独立创建

```python
# purchase_order_service.py
async def create_purchase_order(self, data: PurchaseOrderCreate) -> PurchaseOrder:
    po = PurchaseOrder(
        supplier_id=data.supplier_id,
        order_date=data.order_date,
        ...
    )
    # sales_order_ids 为可选字段
    if data.sales_order_ids:
        for so_id in data.sales_order_ids:
            po.sales_orders.append(
                PurchaseOrderSalesOrder(sales_order_id=so_id)
            )
    # 创建明细行
    for item in data.items:
        po.items.append(PurchaseOrderItem(
            product_id=item.product_id,
            sales_order_item_id=item.sales_order_item_id,  # 可选
            quantity=item.quantity,
            ...
        ))
    return await self.repo.create(po)
```

#### R02：关联时采购数量不能超过未采购需求

```python
async def validate_purchase_quantity(self, item: PurchaseOrderItemCreate):
    if item.sales_order_item_id:
        so_item = await self.sales_order_repo.get_item(item.sales_order_item_id)
        remaining = so_item.quantity - so_item.purchased_quantity
        if item.quantity > remaining:
            raise BusinessError(
                code=42230,
                message=f"采购数量({item.quantity})超过未采购需求({remaining})"
            )
```

#### R03：实收数量不能超过采购单未到货数量

```python
async def validate_receiving_quantity(self, item: ReceivingNoteItemCreate):
    po_item = await self.purchase_order_repo.get_item(item.purchase_order_item_id)
    remaining = po_item.quantity - po_item.received_quantity
    if item.actual_quantity > remaining:
        raise BusinessError(
            code=42240,
            message=f"实收数量({item.actual_quantity})超过未到货数量({remaining})"
        )
```

#### R04：排柜计划只能关联"已到齐"的销售订单

```python
async def validate_container_plan_orders(self, sales_order_ids: list[UUID]):
    for so_id in sales_order_ids:
        so = await self.sales_order_repo.get(so_id)
        if so.status != SalesOrderStatus.GOODS_READY:
            raise BusinessError(
                code=42250,
                message=f"订单 {so.order_no} 状态为 {so.status}，需为'已到齐'才可排柜"
            )
```

#### R05：配载商品总数不能超过已入库数量

```python
async def validate_loading_quantity(self, plan_id: UUID, product_id: UUID,
                                      sales_order_id: UUID, quantity: int):
    # 查询该订单该商品的已入库数量
    inventory_qty = await self.inventory_repo.get_available_quantity(
        product_id=product_id, sales_order_id=sales_order_id
    )
    # 查询已排柜数量（排除当前计划）
    loaded_qty = await self.container_repo.get_loaded_quantity(
        product_id=product_id, sales_order_id=sales_order_id,
        exclude_plan_id=plan_id
    )
    available = inventory_qty - loaded_qty
    if quantity > available:
        raise BusinessError(
            code=42254,
            message=f"装柜数量({quantity})超过可用库存({available})"
        )
```

#### R06 & R07：体积/重量超限校验

```python
async def validate_container_limits(self, plan_id: UUID, container_seq: int):
    plan = await self.container_repo.get(plan_id)
    items = await self.container_repo.get_items_by_seq(plan_id, container_seq)

    total_volume = sum(item.volume_cbm for item in items)
    total_weight = sum(item.weight_kg for item in items)

    specs = CONTAINER_SPECS[plan.container_type]
    errors = []
    if total_volume > specs["volume_cbm"]:
        errors.append({
            "code": 42251, "field": "volume",
            "message": f"体积 {total_volume} CBM 超过限制 {specs['volume_cbm']} CBM"
        })
    if total_weight > specs["max_weight_kg"]:
        errors.append({
            "code": 42252, "field": "weight",
            "message": f"重量 {total_weight} KG 超过限制 {specs['max_weight_kg']} KG"
        })
    if errors:
        raise BusinessError(code=42251, message="配载超限", detail=errors)
```

#### R08：合柜目的港一致性

```python
async def validate_destination_consistency(self, sales_order_ids: list[UUID]):
    ports = set()
    for so_id in sales_order_ids:
        so = await self.sales_order_repo.get(so_id)
        ports.add(so.destination_port)
    if len(ports) > 1:
        raise BusinessError(
            code=42253,
            message=f"合柜的销售订单目的港不一致: {', '.join(ports)}"
        )
```

#### R09：保质期校验

```python
async def check_shelf_life(self, plan_id: UUID, eta: date | None = None):
    """检查配载商品的保质期是否充足"""
    config = await self.config_repo.get("shelf_life_threshold")
    threshold = config.value if config else 2/3  # 默认 2/3

    warnings = []
    items = await self.container_repo.get_all_items(plan_id)
    for item in items:
        inventory = await self.inventory_repo.get_by_product_and_order(
            item.product_id, item.sales_order_id
        )
        for inv in inventory:
            expiry_date = inv.production_date + timedelta(days=item.product.shelf_life_days)
            arrival_date = eta or (date.today() + timedelta(days=30))  # 默认30天海运
            remaining_days = (expiry_date - arrival_date).days
            total_days = item.product.shelf_life_days
            if remaining_days / total_days < threshold:
                warnings.append({
                    "product": item.product.name_cn,
                    "batch_no": inv.batch_no,
                    "production_date": inv.production_date.isoformat(),
                    "remaining_ratio": f"{remaining_days/total_days:.1%}",
                    "message": f"到港后剩余保质期不足 {threshold:.0%}"
                })
    return warnings
```

#### R10-R15：状态联动机制

```python
# sales_order_service.py
async def confirm_order(self, order_id: UUID):
    """R10: 确认订单后自动变为'采购中'"""
    order = await self.repo.get(order_id)
    self._validate_transition(order.status, SalesOrderStatus.CONFIRMED)
    order.status = SalesOrderStatus.PURCHASING  # 确认即进入采购中
    await self.repo.update(order)

# warehouse_service.py
async def create_receiving_note(self, data):
    """R11: 创建收货单后检查是否全部到齐"""
    note = await self._save_receiving_note(data)
    # 更新采购单到货数量和状态
    await self._update_purchase_order_status(note.purchase_order_id)
    # 检查关联的销售订单是否全部到齐
    sales_order_ids = await self._get_related_sales_orders(note.purchase_order_id)
    for so_id in sales_order_ids:
        if await self._check_all_goods_received(so_id):
            await self.sales_order_service.update_status(
                so_id, SalesOrderStatus.GOODS_READY
            )

# container_service.py
async def confirm_plan(self, plan_id: UUID):
    """R12: 确认排柜后，关联订单状态变为'已排柜'"""
    await self.validate_container_limits_all(plan_id)
    plan = await self.repo.get(plan_id)
    plan.status = ContainerPlanStatus.CONFIRMED
    await self.repo.update(plan)
    for so in plan.sales_orders:
        await self.sales_order_service.update_status(
            so.sales_order_id, SalesOrderStatus.CONTAINER_PLANNED
        )

async def complete_stuffing(self, plan_id: UUID, data: StuffingCreate):
    """R13: 装柜完成，关联订单状态变为'已装柜'"""
    record = await self._save_stuffing_record(plan_id, data)
    if await self._all_containers_stuffed(plan_id):
        plan = await self.repo.get(plan_id)
        plan.status = ContainerPlanStatus.LOADED
        await self.repo.update(plan)
        for so in plan.sales_orders:
            await self.sales_order_service.update_status(
                so.sales_order_id, SalesOrderStatus.CONTAINER_LOADED
            )

# logistics_service.py
async def update_status(self, logistics_id: UUID, new_status: LogisticsStatus):
    """R14 & R15: 物流状态联动销售订单"""
    record = await self.repo.get(logistics_id)
    self._validate_transition(record.status, new_status)
    record.status = new_status
    await self.repo.update(record)

    plan = await self.container_repo.get(record.container_plan_id)
    if new_status == LogisticsStatus.LOADED_ON_SHIP:
        # R14: 已装船 → 销售订单'已出运'
        plan.status = ContainerPlanStatus.SHIPPED
        for so in plan.sales_orders:
            await self.sales_order_service.update_status(
                so.sales_order_id, SalesOrderStatus.SHIPPED
            )
    elif new_status == LogisticsStatus.DELIVERED:
        # R15: 已签收 → 销售订单'已签收'
        for so in plan.sales_orders:
            await self.sales_order_service.update_status(
                so.sales_order_id, SalesOrderStatus.DELIVERED
            )
```

### 5.3 排柜计算引擎

#### 柜型参数常量

```python
# app/services/container_calculator.py
CONTAINER_SPECS = {
    "20GP": {"volume_cbm": 33.2, "max_weight_kg": 21800,
             "length_cm": 590, "width_cm": 235, "height_cm": 239},
    "40GP": {"volume_cbm": 67.7, "max_weight_kg": 26680,
             "length_cm": 1203, "width_cm": 235, "height_cm": 239},
    "40HQ": {"volume_cbm": 76.3, "max_weight_kg": 26580,
             "length_cm": 1203, "width_cm": 235, "height_cm": 269},
    "reefer": {"volume_cbm": 28.0, "max_weight_kg": 27000,
               "length_cm": 550, "width_cm": 228, "height_cm": 222},
}
```

#### 柜型推荐算法

```python
async def recommend_container_type(self, sales_order_ids: list[UUID]) -> list[dict]:
    """根据待装货物总量推荐柜型和数量"""
    total_volume, total_weight = await self._calc_totals(sales_order_ids)

    recommendations = []
    for ctype, spec in CONTAINER_SPECS.items():
        if ctype == "reefer":
            continue  # 冷藏柜需手动选择

        # 按体积计算需要的柜数
        count_by_volume = math.ceil(total_volume / spec["volume_cbm"])
        # 按重量计算需要的柜数
        count_by_weight = math.ceil(total_weight / spec["max_weight_kg"])
        # 取较大值
        count = max(count_by_volume, count_by_weight)

        # 计算利用率
        volume_utilization = total_volume / (spec["volume_cbm"] * count)
        weight_utilization = total_weight / (spec["max_weight_kg"] * count)

        recommendations.append({
            "container_type": ctype,
            "count": count,
            "volume_utilization": round(volume_utilization * 100, 1),
            "weight_utilization": round(weight_utilization * 100, 1),
            "estimated_cost_rank": count,  # 柜数越少越经济
        })

    # 按柜数排序（柜数少的优先推荐）
    recommendations.sort(key=lambda x: (x["count"], -max(
        x["volume_utilization"], x["weight_utilization"]
    )))
    return recommendations
```

#### 利用率实时计算

```python
async def get_container_summary(self, plan_id: UUID) -> list[dict]:
    """获取每个柜子的利用率汇总"""
    plan = await self.repo.get(plan_id)
    spec = CONTAINER_SPECS[plan.container_type]
    items = await self.repo.get_all_items(plan_id)

    summaries = {}
    for item in items:
        seq = item.container_seq
        if seq not in summaries:
            summaries[seq] = {"volume": 0, "weight": 0, "items": []}
        summaries[seq]["volume"] += float(item.volume_cbm)
        summaries[seq]["weight"] += float(item.weight_kg)
        summaries[seq]["items"].append(item)

    result = []
    for seq in range(1, plan.container_count + 1):
        data = summaries.get(seq, {"volume": 0, "weight": 0, "items": []})
        result.append({
            "container_seq": seq,
            "loaded_volume_cbm": round(data["volume"], 3),
            "volume_utilization": round(data["volume"] / spec["volume_cbm"] * 100, 1),
            "loaded_weight_kg": round(data["weight"], 3),
            "weight_utilization": round(data["weight"] / spec["max_weight_kg"] * 100, 1),
            "is_over_volume": data["volume"] > spec["volume_cbm"],
            "is_over_weight": data["weight"] > spec["max_weight_kg"],
            "item_count": len(data["items"]),
        })
    return result
```

---

## 六、测试策略

### 6.1 单元测试（pytest）

#### 6.1.1 测试基础设施

**测试数据库**: 使用独立的 PostgreSQL 测试数据库，每个测试用例在事务内执行并自动回滚。

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    """每个测试用例独立事务，测试后自动回滚"""
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await session.close()
        await transaction.rollback()
```

**测试数据工厂（factory_boy）**:

```python
# tests/factories.py
import factory
from app.models import Product, Customer, Supplier, SalesOrder

class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    sku_code = factory.Sequence(lambda n: f"SN-{n:04d}")
    name_cn = factory.Faker("company", locale="zh_CN")
    name_en = factory.Faker("company")
    category = "biscuit"
    spec = "500g/袋"
    unit_weight_kg = 0.55
    unit_volume_cbm = 0.001
    packing_spec = "24袋/箱"
    carton_length_cm = 40
    carton_width_cm = 30
    carton_height_cm = 25
    carton_gross_weight_kg = 13.5
    shelf_life_days = 365
    status = "active"

class CustomerFactory(factory.Factory):
    class Meta:
        model = Customer
    customer_code = factory.Sequence(lambda n: f"CUS-{n:04d}")
    name = factory.Faker("company")
    country = "Philippines"
    contact_person = factory.Faker("name")
    currency = "USD"
    payment_method = "TT"

class SalesOrderFactory(factory.Factory):
    class Meta:
        model = SalesOrder
    order_no = factory.Sequence(lambda n: f"SO-20260301-{n:03d}")
    order_date = factory.LazyFunction(date.today)
    destination_port = "Manila, Philippines"
    trade_term = "FOB"
    currency = "USD"
    payment_method = "TT"
    status = "draft"
```

#### 6.1.2 Models 层测试

```
tests/unit/test_models/
├── test_product.py           # 商品模型：自动计算、唯一约束、软删除
├── test_sales_order.py       # 订单模型：金额自动计算、汇总字段
├── test_purchase_order.py    # 采购单模型：金额自动计算
├── test_container_plan.py    # 排柜模型：体积/重量计算
└── test_user.py              # 用户模型：密码哈希验证
```

关键测试用例：
- 销售订单明细 `amount = quantity × unit_price` 自动计算
- 订单汇总 `total_amount`、`estimated_volume_cbm`、`estimated_weight_kg` 自动更新
- `sku_code`、`order_no` 等唯一约束测试
- 商品软删除（status 改为 inactive，不物理删除）

#### 6.1.3 Services 层测试

```
tests/unit/test_services/
├── test_auth_service.py             # 登录、Token 生成、密码验证
├── test_product_service.py          # CRUD + 批量导入
├── test_sales_order_service.py      # R10 状态联动、编辑限制
├── test_purchase_order_service.py   # R01 独立/关联创建、R02 数量校验
├── test_warehouse_service.py        # R03 实收校验、R11 到齐联动
├── test_container_service.py        # R04-R09 全部排柜规则
├── test_container_calculator.py     # 柜型推荐、利用率计算、保质期校验
├── test_logistics_service.py        # R14/R15 状态联动
└── test_permissions.py              # 权限矩阵全覆盖
```

**业务规则覆盖矩阵**:

| 规则 | 测试文件 | 关键用例 |
|------|---------|---------|
| R01 | test_purchase_order_service | 独立创建成功 / 关联创建成功 |
| R02 | test_purchase_order_service | 数量等于上限→通过 / 数量超限→异常 42230 |
| R03 | test_warehouse_service | 实收=剩余→通过 / 实收>剩余→异常 42240 |
| R04 | test_container_service | goods_ready→通过 / 其他状态→异常 42250 |
| R05 | test_container_service | 数量≤库存→通过 / 数量>库存→异常 42254 |
| R06 | test_container_service | 体积刚好=上限→通过 / 体积超限→异常 42251 |
| R07 | test_container_service | 重量刚好=上限→通过 / 重量超限→异常 42252 |
| R08 | test_container_service | 目的港一致→通过 / 不一致→异常 42253 |
| R09 | test_container_calculator | 剩余>2/3→无警告 / 剩余<2/3→警告 / 自定义阈值 |
| R10 | test_sales_order_service | 确认后状态=purchasing |
| R11 | test_warehouse_service | 部分到货→不变 / 全部到齐→goods_ready |
| R12 | test_container_service | 排柜确认→关联订单 container_planned |
| R13 | test_container_service | 装柜完成→关联订单 container_loaded |
| R14 | test_logistics_service | 物流已装船→关联订单 shipped |
| R15 | test_logistics_service | 物流已签收→关联订单 delivered |

#### 6.1.4 API 层测试

```
tests/api/test_v1/
├── test_auth.py              # 登录成功/失败、Token 刷新、登出
├── test_products.py          # CRUD + 导入导出 + 权限
├── test_customers.py         # CRUD + 权限
├── test_suppliers.py         # CRUD + 权限
├── test_sales_orders.py      # CRUD + 确认 + 生成采购单 + 权限
├── test_purchase_orders.py   # CRUD + 确认 + 取消 + 权限
├── test_warehouse.py         # 收货 + 库存查询 + 权限
├── test_containers.py        # CRUD + 校验 + 确认 + 装柜 + 权限
├── test_logistics.py         # CRUD + 状态更新 + 权限
├── test_dashboard.py         # 各仪表盘端点
├── test_statistics.py        # 统计端点
└── test_system.py            # 用户管理 + 配置 + 审计日志
```

每个端点覆盖 4 类场景：
1. **成功场景**: 正确参数 → 预期结果
2. **参数校验失败**: 缺少必填字段/格式错误 → 400/422
3. **无权限**: 用不同角色请求 → 403
4. **业务规则违反**: 触发 R01-R15 规则 → 422 + 具体错误码

#### 6.1.5 覆盖率目标

- 总体覆盖率 ≥ 80%
- Services 层覆盖率 ≥ 90%（核心业务逻辑）
- 所有 R01-R15 业务规则 100% 覆盖

使用 `pytest-cov` 生成覆盖率报告：
```bash
uv run pytest --cov=app --cov-report=html --cov-report=term-missing
```

### 6.2 端到端测试（Playwright）

#### 6.2.1 完整业务流测试

```typescript
// e2e/tests/full-flow.spec.ts
// 14 步完整业务流：创建订单 → 采购 → 收货 → 排柜 → 物流
test("complete business flow", async ({ page }) => {
  // 1. 管理员登录
  // 2. 创建商品
  // 3. 创建客户
  // 4. 创建供应商
  // 5. 创建销售订单（添加商品明细）
  // 6. 确认销售订单 → 验证状态变为"采购中"
  // 7. 一键生成采购单 → 验证采购单草稿
  // 8. 确认采购单（下单）
  // 9. 创建收货单 → 验证入库 → 验证采购单状态更新
  // 10. 全部到货后验证销售订单状态变为"已到齐"
  // 11. 创建排柜计划 → 柜型推荐 → 配载 → 确认
  // 12. 录入装柜记录（柜号+铅封号）→ 验证状态联动
  // 13. 创建物流记录 → 更新物流状态（已装船）
  // 14. 更新物流状态（已签收）→ 验证最终状态
});
```

#### 6.2.2 排柜管理专项测试

```typescript
// e2e/tests/container-loading.spec.ts
test.describe("排柜管理", () => {
  test("柜型推荐 — 根据货物体积推荐合适柜型");
  test("超体积告警 — 配载超过柜型容积时显示红色警告并阻止确认");
  test("超重量告警 — 配载超过柜型载重时显示红色警告并阻止确认");
  test("保质期警告 — 剩余保质期不足时显示黄色警告");
  test("装箱单导出 — 确认配载后导出装箱单并验证内容");
  test("合柜目的港校验 — 不同目的港订单合柜时阻止");
  test("多柜分配 — 多个柜子间正确分配货物");
});
```

#### 6.2.3 权限控制测试

```typescript
// e2e/tests/permissions.spec.ts
test.describe("权限控制", () => {
  test("业务员 — 可创建订单但不可确认");
  test("采购员 — 可创建采购单但不可确认");
  test("仓库员 — 可操作收货但不可创建订单");
  test("查看者 — 只读访问所有模块");
  test("超级管理员 — 可执行批量导出");
  test("非超级管理员 — 批量导出按钮不可见");
});
```

#### 6.2.4 认证流程测试

```typescript
// e2e/tests/auth.spec.ts
test.describe("认证", () => {
  test("正确用户名密码登录成功");
  test("错误密码登录失败");
  test("Token 过期后自动跳转登录页");
  test("登出后无法访问受保护页面");
});
```

### 6.3 CI 集成

```yaml
# 测试流水线阶段
stages:
  - lint        # black + ruff + mypy 代码检查
  - unit-test   # pytest 单元测试
  - api-test    # pytest API 测试（需要测试数据库）
  - integration # 集成测试（服务间交互）
  - e2e         # Playwright E2E 测试（需要完整环境）
```

---

## 七、开发规范

### 7.1 Python 代码规范

**工具配置** (`pyproject.toml`):

```toml
[tool.black]
line-length = 100
target-version = ["py312"]

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 7.2 命名规范

| 类别 | 规范 | 示例 |
|------|------|------|
| Python 文件 | snake_case | `sales_order_service.py` |
| Python 类 | PascalCase | `SalesOrderService` |
| Python 函数/变量 | snake_case | `create_sales_order` |
| Python 常量 | UPPER_SNAKE_CASE | `CONTAINER_SPECS` |
| 数据库表名 | snake_case 复数 | `sales_orders` |
| 数据库字段名 | snake_case | `order_date` |
| API 路径 | kebab-case 复数 | `/api/v1/sales-orders` |
| TypeScript 文件 | kebab-case | `sales-order-list.tsx` |
| TypeScript 组件 | PascalCase | `SalesOrderList` |
| TypeScript 接口 | PascalCase + I 前缀 | `ISalesOrder` |

### 7.3 Git 工作流

```
main         ──────────────────────────────── 生产分支（受保护）
  │
  └── develop ──────────────────────────────── 开发主线
        │
        ├── feature/product-crud ──────────── 功能分支
        ├── feature/container-loading ──────── 功能分支
        ├── fix/order-status-calc ──────────── 修复分支
        └── hotfix/login-crash ──────────────── 紧急修复（从 main 切出）
```

分支命名: `feature/<模块>-<描述>` / `fix/<模块>-<描述>` / `hotfix/<描述>`

### 7.4 Commit 规范（Conventional Commits）

```
<type>(<scope>): <description>

feat(sales-order): 添加一键生成采购单功能
fix(container): 修复体积利用率计算精度问题
refactor(auth): 重构 JWT 认证中间件
test(warehouse): 添加 R03 业务规则单元测试
docs(api): 更新 API 文档
chore(docker): 更新 PostgreSQL 镜像版本
```

**scope 列表**: `product` / `customer` / `supplier` / `sales-order` / `purchase-order` / `warehouse` / `container` / `logistics` / `auth` / `dashboard` / `system` / `docker` / `ci` / `api` / `db`

### 7.5 PR 流程与检查清单

每个 PR 合入前需满足：

- [ ] 代码通过 `black` + `ruff` + `mypy` 检查
- [ ] 新增功能有对应的单元测试
- [ ] 所有测试通过
- [ ] 覆盖率未下降
- [ ] API 变更更新了 schema 定义
- [ ] 数据库变更有 Alembic 迁移脚本

### 7.6 错误处理模式

**异常类层次**:

```python
# app/core/exceptions.py
class AppError(Exception):
    """应用基础异常"""
    def __init__(self, code: int, message: str, detail: dict | None = None):
        self.code = code
        self.message = message
        self.detail = detail

class BusinessError(AppError):
    """业务规则异常（返回 422）"""
    pass

class NotFoundError(AppError):
    """资源不存在（返回 404）"""
    def __init__(self, resource: str, id: str):
        super().__init__(code=40400, message=f"{resource} {id} 不存在")

class PermissionDeniedError(AppError):
    """权限不足（返回 403）"""
    def __init__(self, message: str = "无权限执行此操作"):
        super().__init__(code=40301, message=message)

class ConflictError(AppError):
    """资源冲突（返回 409）"""
    pass
```

**全局异常处理器**:

```python
# app/main.py
@app.exception_handler(BusinessError)
async def business_error_handler(request, exc: BusinessError):
    return JSONResponse(status_code=422, content={
        "code": exc.code, "message": exc.message, "detail": exc.detail
    })

@app.exception_handler(NotFoundError)
async def not_found_handler(request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={
        "code": exc.code, "message": exc.message
    })

@app.exception_handler(PermissionDeniedError)
async def permission_handler(request, exc: PermissionDeniedError):
    return JSONResponse(status_code=403, content={
        "code": exc.code, "message": exc.message
    })
```

### 7.7 结构化日志策略

使用 `structlog` 输出 JSON 格式日志：

```python
# app/core/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()

# 使用示例
logger.info("sales_order_confirmed",
    order_no="SO-20260226-001",
    user_id="xxx",
    old_status="draft",
    new_status="purchasing"
)
```

输出:
```json
{
  "event": "sales_order_confirmed",
  "order_no": "SO-20260226-001",
  "user_id": "xxx",
  "old_status": "draft",
  "new_status": "purchasing",
  "level": "info",
  "timestamp": "2026-02-27T10:00:00Z"
}
```

### 7.8 审计日志

所有关键操作写入 `audit_logs` 表：

```python
# app/services/audit_service.py
class AuditService:
    async def log(self, user_id: UUID, action: str, resource_type: str,
                  resource_id: str = None, detail: dict = None, ip: str = None):
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip,
        )
        await self.repo.create(log_entry)
```

需记录审计日志的操作：
- 创建、编辑、删除任何主数据
- 订单确认、状态变更
- 数据导出（含导出范围）
- 用户登录/登出
- 角色/权限变更
- 系统配置修改

---

## 八、部署方案

### 8.1 Docker Compose 服务编排

```yaml
# docker-compose.yml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: snack-erp-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-snack_erp}
      POSTGRES_USER: ${DB_USER:-erp_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-erp_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: snack-erp-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: snack-erp-backend
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET: ${JWT_SECRET}
      CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:3000}
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: snack-erp-frontend
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:80"
    depends_on:
      - backend

  nginx:
    image: nginx:1.25-alpine
    container_name: snack-erp-nginx
    restart: unless-stopped
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "127.0.0.1:80:80"
    depends_on:
      - backend
      - frontend

volumes:
  pg_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/dev/docker-data/snack-erp/postgres
  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /home/dev/docker-data/snack-erp/redis
```

### 8.2 环境变量管理

```bash
# .env.example
# Database
DB_NAME=snack_erp
DB_USER=erp_user
DB_PASSWORD=          # 必填，不要提交真实值
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_PASSWORD=       # 必填

# JWT
JWT_SECRET=           # 必填，至少 32 位随机字符串
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000

# App
APP_ENV=development   # development / production
LOG_LEVEL=INFO
```

**安全要求**:
- `.env` 文件不提交到 Git（已在 `.gitignore` 中排除）
- 生产环境使用 Docker secrets 或 GCP Secret Manager
- 所有密码/密钥在部署时通过环境变量注入

### 8.3 数据库备份策略

```bash
#!/bin/bash
# scripts/backup-db.sh — 每日自动备份
BACKUP_DIR="/home/dev/docker-data/snack-erp/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/snack_erp_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

docker exec snack-erp-postgres pg_dump -U erp_user snack_erp | gzip > "${BACKUP_FILE}"

# 保留最近 30 天的备份
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +30 -delete
```

通过 cron 定时执行：
```
0 2 * * * /home/dev/workspace/snack-export-erp/scripts/backup-db.sh
```

### 8.4 端口绑定

遵循 CLAUDE.md 规范，所有端口绑定 `127.0.0.1`：

| 服务 | 端口 | 绑定地址 |
|------|------|---------|
| PostgreSQL | 5432 | 127.0.0.1:5432 |
| Redis | 6379 | 127.0.0.1:6379 |
| Backend (FastAPI) | 8000 | 127.0.0.1:8000 |
| Frontend (Nginx) | 3000 | 127.0.0.1:3000 |
| Nginx (入口) | 80 | 127.0.0.1:80 |

外部访问通过 GCP 防火墙规则 + SSH 隧道或反向代理网关控制。

---

## 附录

### A. 柜型参数参考

| 柜型 | 内容积(CBM) | 最大载重(KG) | 内尺寸 L×W×H (cm) |
|------|------------|-------------|-------------------|
| 20GP | 33.2 | 21,800 | 590 × 235 × 239 |
| 40GP | 67.7 | 26,680 | 1203 × 235 × 239 |
| 40HQ | 76.3 | 26,580 | 1203 × 235 × 269 |
| 冷藏柜 | 28.0 | 27,000 | 550 × 228 × 222 |

### B. 默认系统配置

| 配置键 | 默认值 | 说明 |
|--------|--------|------|
| shelf_life_threshold | 0.667 | 保质期预警阈值（剩余/总保质期） |
| default_shipping_days | 30 | 默认海运天数（用于保质期估算） |
| page_size_default | 20 | 默认分页大小 |
| page_size_max | 100 | 最大分页大小 |
