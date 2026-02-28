---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-内部运营中台客户信息管理与运营系统 -2026-02-25_17-41-07.md
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
workflowType: 'architecture'
project_name: '内部运营中台客户信息管理与运营系统'
user_name: 'Sacrtap'
date: '2026-02-27'
status: 'complete'
completedAt: '2026-02-27'
lastStep: 8
---

# Architecture Decision Document

_本文档通过逐步协作探索创建，确保 AI 代理实现保持一致。各章节在架构决策过程中依次 Append。_

---

## 文档说明

**项目名称：** 内部运营中台客户信息管理与运营系统  
**架构师：** Sacrtap  
**创建日期：** 2026-02-27  
**状态：** 实现模式已定义

**输入文档：**
- ✅ 产品简报 (Product Brief)
- ✅ 产品需求文档 (PRD)
- ✅ UX 设计规格说明 (UX Design Specification)

**技术栈：**
- **后端**: Python 3.11 + Sanic + SQLAlchemy 2.0
- **前端**: Vue 3 + Arco Design + TypeScript
- **数据库**: PostgreSQL 18 (UTF-8)
- **部署**: Docker + Docker Compose
- **任务队列**: Celery + Redis
- **进度推送**: REST API 轮询 (2 秒间隔)

---

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
- 客户 MDM（8 个 FR）：CRUD API、批量导入/导出、数据验证层
- 健康度监控（7 个 FR）：定时任务、预警推送、规则引擎
- 价值评估（6 个 FR）：配置管理、批量重算、版本历史记录
- 结算管理（10 个 FR）：结算引擎、异常检测、PDF 生成、邮件集成
- 权限系统（5 个 FR）：RBAC、数据权限过滤、审计日志
- 数据分析（5 个 FR）：统计查询、报表生成、数据可视化

**Non-Functional Requirements:**
- 性能：关键查询<1 秒，复杂查询<5 秒 → 数据库索引优化、缓存策略
- 可用性：≥99.5% → 容器化部署、健康检查
- 并发：≥50 用户 → 异步后端、连接池
- 安全：JWT+RBAC、敏感数据加密 → 认证中间件、加密层
- 可扩展性：支持 SaaS 化 → 多租户预留、模块化设计

**Scale & Complexity:**

- Primary domain: Full-Stack Web App（企业内部系统）
- Complexity level: 中等偏高（复杂业务逻辑）
- Estimated architectural components: ~15 个核心组件

### Technical Constraints & Dependencies

**确定技术栈：**
- 后端：Python 3.11 + Sanic + SQLAlchemy 2.0
- 前端：Vue 3 + Arco Design + TypeScript
- 数据库：PostgreSQL 18（UTF-8）
- 部署：Docker + Docker Compose

**关键依赖：**
- Arco Design Vue 组件库
- JWT 认证库
- SQLAlchemy 2.0 ORM
- Docker 容器化

**第二期依赖：**
- 外部用量数据采集接口
- 邮件发送服务
- PDF 生成库

### Cross-Cutting Concerns Identified

1. **权限控制** - 贯穿所有 API 和前端组件（数据权限 + 功能权限）
2. **审计日志** - 所有关键操作记录（增删改/转移/导出/配置）
3. **数据验证** - 前端 + 后端双重验证（必填/业务规则/数据清洗）
4. **异常处理** - 统一错误响应格式（标准错误代码 + 友好提示）
5. **性能优化** - 多层级策略（索引/缓存/虚拟滚动）
6. **数据安全** - 多层级防护（认证/加密/SQL 注入/XSS）

---

## Core Domain Models

### Customer Domain (客户域)

**CRITICAL**: Customer table has **TWO ID fields**:
- `id` - Database primary key (auto-increment integer), used for internal database relationships
- `customer_code` - Business customer ID (e.g., "C001", "C002"), used for business operations

**Table: customers**
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,              -- 数据库主键（内部关联使用）
    customer_code VARCHAR(50) NOT NULL UNIQUE,  -- 业务客户 ID（如 "C001"）
    customer_name VARCHAR(200) NOT NULL,        -- 客户名称
    organization_name VARCHAR(200),             -- 组织名称
    contact_person VARCHAR(100),                -- 联系人
    contact_phone VARCHAR(50),                  -- 联系电话
    contact_email VARCHAR(100),                 -- 联系邮箱
    industry VARCHAR(100),                      -- 行业
    region VARCHAR(100),                        -- 区域
    sales_rep_id INTEGER REFERENCES users(id),  -- 负责销售（数据权限）
    tier_level VARCHAR(10),                     -- 客户等级 (S/A/B/C/D)
    annual_consumption DECIMAL(15,2),           -- 年消费金额
    status VARCHAR(20) DEFAULT 'active',        -- 状态 (active/inactive/risk)
    last_activity_date DATE,                    -- 最后活跃日期
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 索引优化
    CONSTRAINT chk_tier_level CHECK (tier_level IN ('S', 'A', 'B', 'C', 'D')),
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'risk'))
);

-- 索引定义
CREATE INDEX idx_customers_sales_rep ON customers(sales_rep_id);  -- 数据权限查询
CREATE INDEX idx_customers_tier ON customers(tier_level);          -- 按等级筛选
CREATE INDEX idx_customers_status ON customers(status);            -- 按状态筛选
CREATE INDEX idx_customers_code ON customers(customer_code);      -- 业务 ID 查询
CREATE INDEX idx_customers_region ON customers(region);            -- 按区域筛选
```

**业务场景说明：**
- **API 返回**：使用 `customer_code`（业务 ID），如 `GET /api/v1/customers/C001`
- **数据库关联**：使用 `id`（数据库主键），如外键引用
- **用户界面**：显示 `customer_code`（用户可见的业务 ID）
- **数据导入**：通过 `customer_code` 识别重复客户

---

## Architectural Decisions

### Core Architecture Patterns

**1. Strategy Pattern for Pricing Models**

```
PricingStrategy (Abstract Base Class)
├── FlatRateStrategy (定价模式)
├── TieredRateStrategy (阶梯模式)
└── PackageRateStrategy (包年模式)
```

**Rationale:**
- 支持 3 种结算模式灵活切换
- 新增模式只需添加新策略类，无需修改现有代码
- 每种策略独立测试，覆盖率可达 95%+

**Implementation:**
```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, usage: Usage, config: PricingConfig) -> Decimal:
        pass

class SettlementService:
    def __init__(self):
        self.strategies = {
            'flat': FlatRateStrategy(),
            'tiered': TieredStrategy(),
            'package': PackageStrategy()
        }
```

**2. SQLAlchemy Session-Level Data Permission Filtering**

**Rationale:**
- 销售天然只看到自己客户，无需在每个 API 中重复判断
- 透明的 WHERE 条件注入，代码一致性好
- 支持 4 级 RBAC 权限（Admin/经理/专员/销售）

**Implementation:**
```python
# Custom query decorator with role-based filtering
def role_filtered_query(query, user_role, user_id):
    if user_role == 'sales':
        return query.filter(Customer.sales_rep_id == user_id)
    elif user_role == 'specialist':
        return query.filter(Customer.org_id == user.org_id)
    # ... other roles
    return query
```

**3. Celery Async Task Queue for Batch Operations**

**Architecture:**
```
Celery Worker Pool (4 processes)
├── Redis Message Broker
├── Task Result Storage (PostgreSQL)
└── Progress Polling API (2s interval)
```

**Use Cases:**
- 批量定价配置（100+ 客户）
- 批量结算单生成（月度结算）
- 批量邮件发送（结算单群发）
- 批量数据导入（Excel 导入）

**Performance:**
- 1000 个客户定价配置：~30 秒
- 1000 个结算单生成：~5 分钟

**4. REST API Polling for Progress Tracking**

**Rationale:**
- MVP 阶段简单可靠，无需 WebSocket 基础设施
- 2 秒轮询间隔，延迟可接受
- 易于调试和维护

**API Design:**
```python
POST /api/pricing/batch-apply-async  # 异步批量配置
→ { "task_id": "xxx", "status": "PROCESSING" }

GET /api/tasks/{task_id}/status      # 进度查询
→ { "status": "PROCESSING", "progress": "750/1000", "failed_ids": [...] }
```

### Database Schema Design

**Core Tables:**

```sql
-- 定价配置表
CREATE TABLE pricing_configs (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    pricing_mode VARCHAR(20) NOT NULL,  -- flat/tiered/package
    device_type VARCHAR(10) NOT NULL,   -- X/N/L
    floor_type VARCHAR(10) NOT NULL,    -- single/multi
    base_rate DECIMAL(10,4) NOT NULL,
    floor_discount DECIMAL(4,2) DEFAULT 1.0,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 阶梯定价表
CREATE TABLE pricing_tiers (
    id SERIAL PRIMARY KEY,
    pricing_config_id INTEGER REFERENCES pricing_configs(id),
    tier_level INTEGER NOT NULL,
    threshold_usage INTEGER NOT NULL,
    tier_rate DECIMAL(10,4) NOT NULL,
    UNIQUE(pricing_config_id, tier_level)
);

-- 包年定价表
CREATE TABLE package_pricing (
    id SERIAL PRIMARY KEY,
    pricing_config_id INTEGER REFERENCES pricing_configs(id),
    package_months INTEGER NOT NULL,
    package_rate DECIMAL(10,4) NOT NULL,
    overage_rate DECIMAL(10,4) NOT NULL
);
```

### API Design Highlights

**Pricing Simulation API (Real-time Calculation):**
```python
POST /api/pricing/calculate-simulation
Request: {
    "pricing_config": { "mode": "tiered", ... },
    "usage_amount": 3000
}
Response: {
    "total": 4500.00,
    "breakdown": [
        { "tier": 1, "usage": 1000, "rate": 1.5, "subtotal": 1500 },
        { "tier": 2, "usage": 2000, "rate": 1.3, "subtotal": 2600 }
    ]
}
```

**Batch Operations:**
```python
POST /api/pricing/batch-apply-async  # 异步批量配置
GET /api/tasks/{task_id}/status      # 进度查询
```

### Cross-Cutting Concerns

**1. Authentication & Authorization**
- JWT Token + Refresh Token
- 4-level RBAC (Admin/经理/专员/销售)
- Data permission filtering at session level

**2. Audit Logging**
- All CRUD operations logged
- Customer transfer, pricing changes, exports
- Stored in `audit_logs` table

**3. Data Validation**
- Frontend + Backend dual validation
- Business rule validation (pricing config completeness)
- Bulk import data cleansing

**4. Error Handling**
- Standard error codes (VALIDATION_ERROR, NOT_FOUND, etc.)
- Friendly error messages (frontend)
- Detailed error logs (backend)

**5. Performance Optimization**
- Database indexing on frequently queried columns
- Query result caching (optional Redis)
- Frontend virtual scrolling for large lists (1000+ items)

**6. Data Security**
- JWT authentication
- Sensitive data encryption at rest
- SQL injection prevention (parameterized queries)
- XSS prevention (input filtering, output encoding)

### Testing Strategy

**Unit Testing (pytest):**
- 95%+ coverage for pricing strategies
- Parameterized tests for device_type × floor_type combinations
- Boundary condition tests for tier thresholds

**Integration Testing:**
- Full settlement flow (create customer → configure pricing → generate settlement)
- Async task flow (trigger task → poll status → verify result)

**Performance Testing:**
- 1000+ customer batch operations < 60 seconds
- Key queries < 1 second
- Complex queries < 5 seconds

---

## Implementation Patterns & Consistency Rules

**CRITICAL**: All AI agents MUST follow these patterns to prevent conflicts.

### Naming Conventions

| Domain | Convention | Example |
|--------|------------|---------|
| **Database Tables** | snake_case (plural) | `customers`, `pricing_configs` |
| **Database Columns** | snake_case | `customer_id`, `created_at` |
| **Database Indexes** | `idx_{table}_{column}` | `idx_customers_email` |
| **API Endpoints** | `/api/v1/{resource-plural}` | `/api/v1/customers`, `/api/v1/pricing-configs` |
| **Python Files** | snake_case | `pricing_config.py`, `settlement_service.py` |
| **Python Classes** | PascalCase | `class PricingConfig`, `class SettlementService` |
| **Python Functions** | snake_case | `def get_pricing_config()`, `def calculate_settlement()` |
| **Python Variables** | snake_case | `customer_id`, `pricing_mode` |
| **TypeScript Components** | PascalCase | `<UserCard />`, `<PricingConfigForm />` |
| **TypeScript Functions** | camelCase | `const getUserData = () => {}` |
| **TypeScript Types** | PascalCase | `interface Customer { id: number }` |
| **JSON Fields** | snake_case | `{ "customer_code": "C001" }` |
| **Pinia Stores** | camelCase + module | `useCustomerStore()`, `usePricingStore()` |

### Project Structure

**Backend Structure:**
```
backend/
├── app/
│   ├── main.py                 # Sanic app entry
│   ├── config.py               # Configuration
│   ├── models/                 # SQLAlchemy models
│   │   ├── customer.py
│   │   ├── pricing.py
│   │   └── settlement.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── customer.py
│   │   ├── pricing.py
│   │   └── settlement.py
│   ├── services/               # Business logic
│   │   ├── customer_service.py
│   │   ├── pricing_service.py
│   │   └── settlement_service.py
│   ├── routes/                 # API routes
│   │   ├── customer_routes.py
│   │   ├── pricing_routes.py
│   │   └── settlement_routes.py
│   ├── tasks/                  # Celery tasks
│   │   ├── pricing_tasks.py
│   │   └── settlement_tasks.py
│   ├── middleware/             # Middleware
│   │   ├── auth_middleware.py
│   │   └── error_middleware.py
│   └── utils/                  # Utilities
│       ├── validators.py
│       └── formatters.py
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/                 # Alembic migrations
└── Dockerfile
```

**Frontend Structure:**
```
frontend/
├── src/
│   ├── api/                    # API client
│   │   ├── customer.ts
│   │   ├── pricing.ts
│   │   └── settlement.ts
│   ├── components/
│   │   ├── base/               # Base components (Arco wrappers)
│   │   ├── business/           # Business components
│   │   │   ├── customer/
│   │   │   ├── pricing/
│   │   │   └── settlement/
│   │   └── layout/             # Layout components
│   ├── stores/                 # Pinia stores
│   │   ├── auth.ts
│   │   ├── customer.ts
│   │   ├── pricing.ts
│   │   └── ui.ts
│   ├── router/
│   ├── types/                  # TypeScript types
│   ├── utils/
│   ├── views/                  # Page views
│   └── assets/
├── tests/
└── Dockerfile
```

### API Response Format

**Success Response:**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "abc-123-def",
    "timestamp": "2026-02-27T10:30:00Z"
  }
}
```

**List Response:**
```json
{
  "data": [...],
  "meta": {
    "total": 1320,
    "page": 1,
    "page_size": 20,
    "total_pages": 66,
    "request_id": "abc-123-def",
    "timestamp": "2026-02-27T10:30:00Z"
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "customer_code",
        "message": "客户编码已存在"
      }
    ],
    "request_id": "abc-123-def",
    "timestamp": "2026-02-27T10:30:00Z"
  }
}
```

**Async Task Response:**
```json
{
  "task_id": "abc-123-def",
  "status": "PROCESSING",
  "status_url": "/api/v1/tasks/abc-123-def/status"
}
```

### Error Handling Pattern

**Backend (Global Exception Handler):**
```python
@app.exception(Exception)
async def handle_exception(request, exception):
    if isinstance(exception, ValidationError):
        return json({"error": {"code": "VALIDATION_ERROR", ...}}, status=400)
    elif isinstance(exception, NotFoundError):
        return json({"error": {"code": "NOT_FOUND", ...}}, status=404)
    else:
        logger.error(f"Unhandled exception: {exception}")
        return json({"error": {"code": "INTERNAL_ERROR", ...}}, status=500)
```

**Frontend (Unified Request Wrapper):**
```typescript
export const request = async (url: string, options?: RequestInit) => {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
      throw new ApiError(data.error.code, data.error.message);
    }
    return data.data;
  } catch (error) {
    if (error instanceof ApiError) {
      showMessage('error', error.message);
    }
    throw error;
  }
};
```

### Authentication Flow

```
Login → POST /api/v1/auth/login → { access_token, refresh_token }
  ↓
Store in localStorage + Pinia
  ↓
Requests: Authorization: Bearer {access_token}
  ↓
401 → Auto refresh token → POST /api/v1/auth/refresh
  ↓
Retry original request
```

**Rules:**
- Token storage: `localStorage` + Pinia Store
- Auto refresh: Max 1 retry
- Session timeout: 30 minutes inactivity

### Batch Operation Flow

```
Trigger batch → POST /api/v1/pricing/batch-apply-async → 202 Accepted
  ↓
Return: { task_id, status: "PROCESSING" }
  ↓
Poll every 2s → GET /api/v1/tasks/{task_id}/status
  ↓
Show progress bar (percentage + success/failed count)
  ↓
Completed → Show result modal + Download failed CSV
```

**Rules:**
- Batch operations: ALWAYS async (return 202)
- Polling interval: 2 seconds
- Progress display: Percentage + success/failed count
- Failure handling: Downloadable CSV + Retry option
