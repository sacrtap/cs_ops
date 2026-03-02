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

### 🐳 Docker 一键部署（推荐）

> **适用场景**: 部署到本地服务器或生产环境  
> **前提条件**: 服务器已安装 Docker 和 Docker Compose

---

#### 📦 部署步骤

**1️⃣ 克隆项目到服务器**

```bash
# SSH 登录到服务器
ssh user@your-server-ip

# 克隆项目（或上传项目文件）
git clone https://github.com/sacrtap/cs_ops.git
cd cs_ops
```

**2️⃣ 配置环境变量**

```bash
# 复制环境配置模板
cp .env.docker .env

# 自动生成 JWT_SECRET_KEY（32 字符随机密钥）
JWT_KEY=$(openssl rand -hex 32) && sed -i "s/CHANGE_ME_GENERATE_SECURE_32_CHAR_RANDOM_STRING/$JWT_KEY/" .env

# 自动生成数据库密码（24 字符随机密码）
DB_PASS=$(openssl rand -base64 24) && sed -i "s/change_me_in_production/$DB_PASS/" .env

# 或者手动编辑配置文件
vim .env
```

> **⚠️ 重要**: 至少修改以下配置：
>
> ```bash
> JWT_SECRET_KEY=生成的 32 字符随机密钥
> POSTGRES_PASSWORD=强密码
> ```

**3️⃣ 一键启动**

```bash
# 启动所有服务（数据库 + 后端 + 前端）
docker-compose up -d

# 执行数据库迁移
docker-compose --profile migrate up migrate
```

**4️⃣ 验证部署**

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试访问
curl http://localhost:80/health
curl http://localhost:8000/health
```

---

#### 🎯 访问服务

部署完成后，可通过以下地址访问：

| 服务     | 地址                       | 说明               |
| -------- | -------------------------- | ------------------ |
| 前端     | http://your-server-ip:80   | Web 界面           |
| 后端 API | http://your-server-ip:8000 | API 接口（含文档） |
| 数据库   | localhost:5432             | PostgreSQL         |

**API 文档**: http://your-server-ip:8000/docs

---

#### 🔧 常用命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看日志
docker-compose logs -f              # 所有服务
docker-compose logs -f backend      # 只看后端
docker-compose logs -f frontend     # 只看前端

# 重启服务
docker-compose restart backend
docker-compose restart frontend

# 停止所有服务
docker-compose down

# 重新部署（更新代码后）
git pull
docker-compose build
docker-compose up -d
docker-compose --profile migrate up migrate
```

---

#### 🗄️ 数据库管理

```bash
# 备份数据库
docker-compose exec db pg_dump -U cs_ops_user cs_ops > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U cs_ops_user cs_ops < backup.sql

# 进入数据库命令行
docker-compose exec db psql -U cs_ops_user cs_ops
```

---

#### 🔐 安全配置

**必须修改的配置** (编辑 `.env` 文件):

```bash
# 1. 自动生成 JWT 密钥（32 字符以上）
JWT_KEY=$(openssl rand -hex 32) && echo "JWT_SECRET_KEY=$JWT_KEY"

# 或者直接替换配置文件中的占位符
JWT_KEY=$(openssl rand -hex 32) && \
  sed -i "s/CHANGE_ME_GENERATE_SECURE_32_CHAR_RANDOM_STRING/$JWT_KEY/" .env

# 2. 自动生成强数据库密码（24 字符）
DB_PASS=$(openssl rand -base64 24) && echo "POSTGRES_PASSWORD=$DB_PASS"

# 或者直接替换配置文件中的占位符
DB_PASS=$(openssl rand -base64 24) && \
  sed -i "s/change_me_in_production/$DB_PASS/" .env

# 3. 一键生成所有安全配置（推荐）
cat >> .env << EOF
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24)
EOF
```

> **💡 提示**: 运行以上命令后，使用 `vim .env` 查看并确认配置已更新

**防火墙配置** (Ubuntu 示例):

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS（如果配置 SSL）
sudo ufw enable
```

**HTTPS 配置**（推荐）:

使用 Nginx 反向代理 + Let's Encrypt SSL 证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

---

#### 🐛 故障排除

**1. 服务启动失败**

```bash
# 查看详细日志
docker-compose logs backend

# 检查端口占用
sudo lsof -i :80
sudo lsof -i :8000
```

**2. 数据库连接失败**

```bash
# 检查数据库是否运行
docker-compose ps db

# 重启数据库
docker-compose restart db

# 等待数据库就绪后重新迁移
docker-compose --profile migrate up migrate
```

**3. 内存不足**

```bash
# 查看资源使用
docker stats

# 减少后端工作进程数（编辑 .env）
API_WORKERS=2
```

**4. 重置部署**

```bash
# 停止并删除所有容器和数据卷（⚠️ 会删除所有数据）
docker-compose down -v

# 重新启动
docker-compose up -d
docker-compose --profile migrate up migrate
```

---

#### 📊 监控与维护

**查看资源使用**:

```bash
# 实时查看容器资源占用
docker stats

# 查看容器状态
docker-compose ps
```

**日志管理**:

```bash
# 查看最近 100 行日志
docker-compose logs --tail=100

# 查看特定时间后的日志
docker-compose logs --since="2026-03-02"
```

**自动重启**:

所有服务已配置 `restart: always`，服务器重启后自动启动：

```bash
# 重启服务器后，检查服务是否自动启动
docker-compose ps

# 如果没有启动
docker-compose up -d
```

---

### 📝 环境配置说明

**`.env` 配置文件**:

```bash
# 数据库配置
POSTGRES_DB=cs_ops                  # 数据库名
POSTGRES_USER=cs_ops_user           # 数据库用户
POSTGRES_PASSWORD=你的强密码        # ⚠️ 使用 openssl rand -base64 24 生成
DB_PORT=5432                        # 数据库端口

# 后端配置
JWT_SECRET_KEY=生成的 32 字符密钥   # ⚠️ 使用 openssl rand -hex 32 生成
API_PORT=8000                       # 后端 API 端口
API_WORKERS=4                       # Gunicorn 工作进程数

# 前端配置
FRONTEND_PORT=80                    # 前端端口
```

**🔧 一键自动生成所有安全配置**:

```bash
# 方法 1: 使用 sed 替换占位符
JWT_KEY=$(openssl rand -hex 32) && \
  sed -i "s/CHANGE_ME_GENERATE_SECURE_32_CHAR_RANDOM_STRING/$JWT_KEY/" .env

DB_PASS=$(openssl rand -base64 24) && \
  sed -i "s/change_me_in_production/$DB_PASS/" .env

# 方法 2: 直接追加配置（推荐）
cat >> .env << EOF
# 自动生成的安全配置
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 24)
EOF

# 验证配置
grep -E "JWT_SECRET_KEY|POSTGRES_PASSWORD" .env
```

---

### 🎓 下一步

1. ✅ **创建管理员账户** - 通过 API 或管理界面
2. ✅ **配置 SSL 证书** - 使用 Let's Encrypt
3. ✅ **设置自动备份** - 配置数据库定时备份
4. ✅ **配置监控系统** - 日志收集、告警通知

**详细文档**:

- 部署快速参考：`docs/DEPLOYMENT_QUICKSTART.md`
- 完整检查清单：`docs/DEPLOYMENT_CHECKLIST.md`

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
