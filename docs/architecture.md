# 架构设计

**最后更新**: 2026-02-28  
**版本**: 0.1.0

---

## 📋 目录

1. [系统架构](#系统架构)
2. [技术架构](#技术架构)
3. [数据架构](#数据架构)
4. [安全架构](#安全架构)
5. [部署架构](#部署架构)

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                                │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Web 浏览器     │   移动端         │   第三方系统             │
└────────┬────────┴────────┬────────┴──────────┬──────────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 网关层                               │
│              (Sanic Router + CORS + Rate Limiting)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────────┐ ┌─────────────┐ ┌──────────────┐
│   认证服务       │ │  业务服务    │ │  工具服务     │
│  (AuthService)  │ │ (Services)  │ │ (Utils)      │
└────────┬────────┘ └──────┬──────┘ └──────┬───────┘
         │                 │                │
         ▼                 ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层                               │
│            (SQLAlchemy 2.0 Async + Repository Pattern)      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层                               │
│              (PostgreSQL 18 + Redis Cache)                  │
└─────────────────────────────────────────────────────────────┘
```

### 分层架构

#### 1. 表现层 (Presentation Layer)

- **前端**: Vue 3 + TypeScript + Arco Design
- **路由**: Vue Router with Auth Guards
- **状态**: Pinia Store
- **通信**: Axios HTTP Client

#### 2. API 层 (API Layer)

- **框架**: Sanic 23.0+ (异步 Web 框架)
- **路由**: Blueprint 组织
- **验证**: Pydantic 2.0
- **认证**: JWT Token

#### 3. 业务层 (Business Layer)

- **服务**: Service Classes
- **逻辑**: 业务规则实现
- **异常**: 自定义异常层次

#### 4. 数据层 (Data Layer)

- **ORM**: SQLAlchemy 2.0 Async
- **模型**: Declarative Base
- **迁移**: Alembic

#### 5. 存储层 (Storage Layer)

- **数据库**: PostgreSQL 18
- **缓存**: Redis (可选)
- **文件**: 本地存储 / 云存储

---

## 💻 技术架构

### 后端技术栈

#### 核心框架

```
Sanic 23.0+
├── 异步请求处理
├── Blueprint 路由组织
├── Middleware 支持
├── WebSocket 支持
└── 内置性能优化
```

#### 数据库 ORM

```
SQLAlchemy 2.0+
├── AsyncSession 异步支持
├── DeclarativeBase 模型定义
├── Relationship 关系映射
├── Index 索引配置
└── Migration 迁移管理 (Alembic)
```

#### 认证授权

```
JWT Authentication
├── python-jose (Token 生成/验证)
├── passlib (密码哈希)
├── bcrypt (加密算法)
└── 基于角色的访问控制 (RBAC)
```

### 前端技术栈

#### 核心框架

```
Vue 3.4+
├── Composition API
├── <script setup> 语法
├── 响应式系统
└── 组件化开发
```

#### 状态管理

```
Pinia 2.1+
├── Store 定义
├── State 状态
├── Getters 计算属性
├── Actions 动作
└── 模块化支持
```

#### UI 组件

```
Arco Design 2.54+
├── 基础组件 (Button, Input, Form)
├── 数据展示 (Table, List, Card)
├── 导航组件 (Menu, Breadcrumb)
├── 反馈组件 (Modal, Message)
└── 主题定制
```

---

## 🗄️ 数据架构

### 数据库设计

#### 用户表 (users)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
```

#### ER 图

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ PK  id          │
│     email       │
│     username    │
│     password    │
│     role        │
│     status      │
│     timestamps  │
└─────────────────┘
```

### 数据模型

#### SQLAlchemy 模型

```python
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
```

### 数据流

#### 创建用户流程

```
用户注册
  │
  ▼
前端表单验证
  │
  ▼
API 请求 (POST /api/v1/auth/register)
  │
  ▼
请求体验证 (Pydantic)
  │
  ▼
业务逻辑 (AuthService)
  │
  ▼
密码哈希 (bcrypt)
  │
  ▼
数据库插入 (SQLAlchemy)
  │
  ▼
返回用户信息 (不含密码)
  │
  ▼
前端更新状态 (Pinia)
```

---

## 🔐 安全架构

### 认证流程

#### JWT Token 认证

```
┌─────────┐      登录请求       ┌─────────┐
│  Client │ ─────────────────► │  Server │
└─────────┘                    └────┬────┘
                                   │
                          验证用户名密码
                                   │
                                   ▼
                          生成 Access Token
                          生成 Refresh Token
                                   │
┌─────────┐      返回 Token      ┌─┴────┐
│  Client │ ◄────────────────── │      │
└────┬────┘                     └──────┘
     │
     │ 存储 Token (localStorage)
     │
     ▼
后续请求携带 Token
```

### 安全策略

#### 1. 密码安全

```python
# 密码哈希配置
BCRYPT_ROUNDS = 10  # 加密轮数
MIN_PASSWORD_LENGTH = 6  # 最小密码长度

# 密码策略
- 至少 6 个字符
- 包含大小写字母
- 包含数字或特殊字符
```

#### 2. Token 安全

```python
# JWT 配置
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 120
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_SECRET_KEY = "强密钥（生产环境必须更换）"
```

#### 3. 账户保护

```python
# 登录失败限制
MAX_LOGIN_ATTEMPTS = 5  # 最大尝试次数
LOCKOUT_DURATION_MINUTES = 15  # 锁定时长

# 防止暴力破解
- 记录登录失败次数
- 达到限制后锁定账户
- 定时自动解锁
```

#### 4. CORS 配置

```python
# 跨域资源共享
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# 生产环境配置
CORS_ORIGINS = [
    "https://app.your-domain.com",
]
```

---

## 🚀 部署架构

### 开发环境

```
┌──────────────────┐
│  本地开发机器     │
├──────────────────┤
│  Frontend        │
│  (Vite Dev Svr)  │
│  :5173           │
├──────────────────┤
│  Backend         │
│  (Sanic)         │
│  :8000           │
├──────────────────┤
│  PostgreSQL      │
│  :5432           │
└──────────────────┘
```

### 生产环境

```
┌─────────────────────────────────────────┐
│              Load Balancer              │
│              (Nginx/ALB)                │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌─────────────────┐ ┌─────────────────┐
│   Frontend      │ │   Backend       │
│   (Static)      │ │   (Sanic)       │
│   CDN/Nginx     │ │   Docker        │
│                 │ │   :8000         │
└─────────────────┘ └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (RDS/本地)    │
                    └─────────────────┘
```

### Docker 部署（可选）

#### Dockerfile - Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["python", "-m", "app.main"]
```

#### Dockerfile - Frontend

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
```

#### Docker Compose

```yaml
version: "3.8"

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/cs_ops
    depends_on:
      - db

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"

  db:
    image: postgres:18
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=cs_ops
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 📊 性能优化

### 后端优化

#### 1. 数据库连接池

```python
# 配置
pool_size = 20  # 连接池大小
max_overflow = 40  # 最大溢出连接数
pool_pre_ping = True  # 连接健康检查
```

#### 2. 异步 IO

```python
# 使用异步数据库操作
async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
```

#### 3. 缓存策略

```python
# Redis 缓存（可选）
- 用户会话缓存
- Token 黑名单
- 频繁查询结果
```

### 前端优化

#### 1. 代码分割

```typescript
// 懒加载路由
const routes = [
  {
    path: "/dashboard",
    component: () => import("@/views/DashboardView.vue"),
  },
];
```

#### 2. 组件优化

```typescript
// 使用 computed 缓存计算结果
const filteredList = computed(() => {
  return list.value.filter((item) => item.active);
});
```

#### 3. 构建优化

```javascript
// vite.config.ts
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["vue", "pinia", "vue-router"],
          arco: ["@arco-design/web-vue"],
        },
      },
    },
  },
};
```

---

## 🔄 扩展性设计

### 模块化设计

#### 后端模块

```
backend/app/
├── config/           # 配置模块
├── models/           # 数据模型模块
├── routes/           # API 路由模块
├── schemas/          # 数据验证模块
├── services/         # 业务逻辑模块
└── utils/            # 工具函数模块
```

#### 前端模块

```
frontend/src/
├── api/              # API 客户端模块
├── stores/           # 状态管理模块
├── views/            # 页面模块
├── components/       # 组件模块
├── router/           # 路由模块
└── utils/            # 工具函数模块
```

### 微服务准备

当前采用单体架构，但设计了清晰的模块边界，便于未来拆分为微服务：

1. **认证服务** - AuthService 独立
2. **用户服务** - UserService 独立
3. **客户服务** - CustomerService 独立
4. **账单服务** - BillingService 独立

---

## 📈 监控与日志

### 日志策略

#### 日志级别

```python
DEBUG    # 调试信息
INFO     # 一般信息
WARNING  # 警告信息
ERROR    # 错误信息
CRITICAL # 严重错误
```

#### 日志格式

```python
"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 监控指标

#### 后端监控

- API 响应时间
- 数据库查询时间
- 错误率
- QPS（每秒请求数）

#### 前端监控

- 页面加载时间
- API 请求成功率
- 用户行为追踪
- JavaScript 错误

---

## 📚 相关文档

- [项目概述](README.md)
- [开发指南](development.md)
- [API 文档](api.md)
- [部署指南](deployment.md)
- [数据库设计](database.md)

---

**最后更新**: 2026-02-28  
**维护者**: Sacrtap
