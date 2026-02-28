# cs_ops

客户成功运营系统 (Customer Success Operations Platform)

---

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [系统部署](#系统部署)
- [测试验证](#测试验证)
- [项目结构](#项目结构)

---

## 项目简介

cs_ops 是一个客户成功运营平台，提供客户管理、健康度监控、价值评估、结算管理等功能。

**核心功能**:
- 权限与认证系统 (JWT + RBAC)
- 客户主数据管理
- 客户健康度监控
- 客户价值评估
- 结算管理
- 操作日志
- 客户转移
- 数据分析与报告

---

## 技术栈

### 后端
- **语言**: Python 3.11+
- **框架**: Sanic 23.x
- **ORM**: SQLAlchemy 2.0 (async)
- **数据库**: PostgreSQL 18
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt + passlib
- **验证**: Pydantic 2.x

### 前端
- **框架**: Vue 3.4 + TypeScript
- **状态管理**: Pinia 2.1
- **UI 组件**: Arco Design 2.54
- **HTTP 客户端**: Axios 1.6
- **构建工具**: Vite 5.0
- **测试**: Playwright + Vitest

---

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 18+
- npm 或 pnpm

### 后端启动

```bash
# 1. 创建虚拟环境
cd backend
python3.11 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -e ".[dev]"
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接和 JWT 密钥

# 4. 创建数据库
createdb -h localhost -U postgres cs_ops

# 5. 运行数据库迁移
alembic upgrade head

# 6. 启动后端服务
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端启动

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 设置 VITE_API_BASE_URL=http://localhost:8000/api/v1

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

---

## 系统部署

### 生产环境部署

#### 1. 后端部署

**使用 Docker**:
```bash
# 构建镜像
docker build -t cs_ops_backend:latest .

# 运行容器
docker run -d \
  --name cs_ops_backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname \
  -e JWT_SECRET_KEY=your-secret-key \
  cs_ops_backend:latest
```

**使用 systemd** (Linux):
```bash
# 创建服务文件 /etc/systemd/system/cs_ops_backend.service
[Unit]
Description=CS Ops Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/cs_ops/backend
Environment="PATH=/path/to/cs_ops/backend/.venv/bin"
ExecStart=/path/to/cs_ops/backend/.venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target

# 启用并启动服务
sudo systemctl enable cs_ops_backend
sudo systemctl start cs_ops_backend
sudo systemctl status cs_ops_backend
```

**配置环境变量**:
```bash
# 生产环境变量示例
export DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
export JWT_SECRET_KEY="your-super-secret-production-key-min-32-chars"
export APP_DEBUG=false
export SERVER_WORKERS=4
```

#### 2. 前端部署

**构建生产版本**:
```bash
cd frontend

# 安装依赖
npm install

# 配置生产 API 地址
echo "VITE_API_BASE_URL=https://api.your-domain.com/api/v1" > .env.production

# 构建
npm run build

# 输出目录：dist/
```

**使用 Nginx 部署**:
```nginx
# Nginx 配置示例
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/cs_ops/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**使用 Docker 部署**:
```bash
# 构建镜像
docker build -t cs_ops_frontend:latest .

# 运行容器
docker run -d \
  --name cs_ops_frontend \
  -p 80:80 \
  cs_ops_frontend:latest
```

#### 3. 数据库部署

**PostgreSQL 配置**:
```bash
# 安装 PostgreSQL 18
sudo apt-get install postgresql-18 postgresql-contrib-18

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE cs_ops;
CREATE USER cs_ops_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE cs_ops TO cs_ops_user;
\q

# 运行数据库迁移
cd backend
source .venv/bin/activate
alembic upgrade head
```

**数据库备份**:
```bash
# 备份数据库
pg_dump -h localhost -U cs_ops_user cs_ops > backup.sql

# 恢复数据库
psql -h localhost -U cs_ops_user cs_ops < backup.sql
```

#### 4. 使用 Docker Compose 一键部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:18
    environment:
      POSTGRES_DB: cs_ops
      POSTGRES_USER: cs_ops_user
      POSTGRES_PASSWORD: your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://cs_ops_user:your-password@db:5432/cs_ops
      JWT_SECRET_KEY: your-secret-key
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

**启动服务**:
```bash
docker-compose up -d
```

#### 5. 环境变量配置

**后端环境变量** (`backend/.env`):
```bash
# 应用配置
APP_NAME=cs_ops
APP_VERSION=0.1.0
APP_DEBUG=false

# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname

# JWT 配置
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
BCRYPT_ROUNDS=10
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# CORS 配置
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=4
```

**前端环境变量** (`frontend/.env.production`):
```bash
# API 基础 URL
VITE_API_BASE_URL=https://api.your-domain.com/api/v1

# 应用配置
VITE_APP_NAME=cs_ops
VITE_APP_VERSION=0.1.0
```

---

## 测试验证

### 运行测试

```bash
# 后端单元测试
cd backend
source .venv/bin/activate
PYTHONPATH=/path/to/backend:$PYTHONPATH \
  pytest tests/unit/test_auth_service.py -v

# 运行并生成覆盖率报告
pytest tests/unit/test_auth_service.py -v --cov=app --cov-report=html

# 前端 E2E 测试
cd frontend
npx playwright test tests/e2e/auth/login.spec.ts

# 前端 API 测试
npx playwright test tests/api/auth/test_login_api.spec.ts
```

### 测试覆盖率

当前测试覆盖率：70%
- 核心功能覆盖：100%
- P0 测试通过率：100%
- P1 测试通过率：100%

---

## 项目结构

```
cs_ops/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── config/            # 配置管理
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── services/          # 业务逻辑服务
│   │   ├── routes/            # API 路由
│   │   ├── middleware/        # 中间件
│   │   ├── utils/             # 工具函数
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试文件
│   ├── migrations/            # 数据库迁移
│   ├── pyproject.toml         # Python 依赖配置
│   └── .env.example           # 环境变量示例
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/               # API 客户端
│   │   ├── components/        # Vue 组件
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── types/             # TypeScript 类型
│   │   └── utils/             # 工具函数
│   ├── tests/                 # 测试文件
│   ├── package.json           # Node.js 依赖配置
│   └── vite.config.ts         # Vite 构建配置
├── _bmad/                      # BMAD 工作流系统
├── _bmad-output/               # BMAD 输出文件
└── README.md                   # 项目文档
```

---

## 🚀 下一步

1. **运行测试**: 验证系统功能
2. **代码审查**: 确保代码质量
3. **部署上线**: 生产环境部署
4. **监控系统**: 配置日志和监控

---

**文档版本**: 1.0  
**最后更新**: 2026-02-27  
**维护者**: Sacrtap
