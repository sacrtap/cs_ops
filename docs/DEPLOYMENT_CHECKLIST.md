# 🚀 CS Ops 部署检查清单

> Story 1.2: JWT Token 管理 - 部署准备文档

---

## ✅ 部署前检查

### 1. 环境配置验证

**检查结果**: ✅ 通过

| 配置项                 | 当前值                | 生产建议                 | 状态 |
| ---------------------- | --------------------- | ------------------------ | ---- |
| 数据库连接             | localhost:5432/cs_ops | 生产数据库地址           | ⚠️   |
| JWT 密钥长度           | 36 字符               | ≥32 字符                 | ✅   |
| Access Token 过期时间  | 120 分钟（2 小时）    | 15-60 分钟（更安全）     | ⚠️   |
| Refresh Token 过期时间 | 7 天                  | 7-30 天                  | ✅   |
| Token 刷新速率限制     | 3 次/60 秒            | 3-5 次/分钟              | ✅   |
| Bcrypt 轮数            | 10                    | 12-14（更安全）          | ⚠️   |
| APP_DEBUG              | true                  | **false** (生产必须关闭) | 🔴   |

**生产环境必须修改**:

```bash
# .env 文件
APP_DEBUG=false                                    # 🔴 必须关闭
DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/cs_ops  # ⚠️ 修改为生产数据库
JWT_SECRET_KEY=更换为新的 32+ 字符随机密钥              # ⚠️ 必须更换
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30                 # ⚠️ 建议缩短
BCRYPT_ROUNDS=12                                   # ⚠️ 建议提高安全性
```

---

### 2. 数据库迁移检查

**迁移文件**:

```
✅ 001_create_users_table.py (Story 1.1)
✅ 002_create_token_blacklist_table.py (Story 1.2)
```

**执行迁移**:

```bash
cd backend
source .venv/bin/activate

# 查看当前迁移状态
alembic current

# 升级到最新版本
alembic upgrade head

# 验证迁移
alembic current
# 应显示：002 (head)
```

**迁移验证 SQL**:

```sql
-- 验证表是否存在
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('users', 'token_blacklists');

-- 验证枚举类型
SELECT typname FROM pg_type
WHERE typtype = 'e'
AND typname IN ('user_role', 'user_status', 'token_blacklist_type', 'blacklist_reason');

-- 验证索引
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename = 'token_blacklists';
```

---

### 3. 依赖安装检查

**Python 依赖**:

```bash
cd backend
source .venv/bin/activate

# 验证依赖
pip check

# 更新依赖（如果需要）
pip install -r requirements.txt --upgrade

# 冻结当前依赖
pip freeze > requirements.lock.txt
```

**新增依赖** (Story 1.2):

```
# 已在 requirements.txt 中
python-jose[cryptography]  # JWT 支持
```

**前端依赖**:

```bash
cd frontend

# 验证依赖
npm check

# 安装依赖
npm install

# 构建生产版本
npm run build
```

---

### 4. 测试验证

**单元测试**:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=/path/to/backend pytest tests/unit/ -v

# 期望结果：41 passed, 1 warning
```

**集成测试**:

```bash
# 需要运行中的应用
pytest tests/integration/test_token_refresh_flow.py -v

# 测试覆盖:
# - Token 刷新流程
# - 单次使用验证
# - 速率限制
```

**测试覆盖率**:

```bash
# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html

# 目标：核心模块 > 80%
```

---

### 5. 应用启动验证

**开发环境启动**:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**生产环境启动**:

```bash
# 使用 gunicorn (推荐)
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/cs_ops/access.log \
  --error-logfile /var/log/cs_ops/error.log \
  --capture-output \
  --preload
```

**健康检查端点**:

```bash
# 检查应用是否启动
curl http://localhost:8000/health

# 期望响应
{
  "status": "healthy",
  "timestamp": "2026-02-28T10:30:00Z",
  "version": "0.1.0"
}
```

---

## 🚀 部署步骤

### 方案 1: Docker 部署（推荐）

**1. 创建 Dockerfile**:

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV APP_DEBUG=false

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**2. 创建 docker-compose.yml**:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/cs_ops
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=cs_ops
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

**3. 部署**:

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 执行数据库迁移
docker-compose exec backend alembic upgrade head
```

---

### 方案 2: 传统部署

**1. 准备服务器**:

```bash
# 安装依赖
sudo apt update
sudo apt install -y python3.11 python3.11-venv postgresql nginx

# 创建用户
sudo useradd -m -s /bin/bash csops
sudo su - csops
```

**2. 部署代码**:

```bash
# 克隆仓库
git clone https://github.com/sacrtap/cs_ops.git
cd cs_ops/backend

# 创建虚拟环境
python3.11 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
# 编辑 .env 文件，更新配置
```

**3. 数据库迁移**:

```bash
# 创建数据库
createdb cs_ops

# 执行迁移
alembic upgrade head
```

**4. 配置 systemd 服务**:

```ini
# /etc/systemd/system/cs_ops.service
[Unit]
Description=CS Ops Backend
After=network.target

[Service]
Type=notify
User=csops
Group=csops
WorkingDirectory=/home/csops/cs_ops/backend
Environment="PATH=/home/csops/cs_ops/backend/.venv/bin"
ExecStart=/home/csops/cs_ops/backend/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**5. 启动服务**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cs_ops
sudo systemctl start cs_ops
sudo systemctl status cs_ops
```

**6. 配置 Nginx**:

```nginx
# /etc/nginx/sites-available/cs_ops
server {
    listen 80;
    server_name api.cs-ops.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 方案 3: 云平台部署

#### AWS Elastic Beanstalk

**1. 创建 application.yml**:

```yaml
# .platform/confighooks/predeploy/01_migrate_db.sh
#!/bin/bash
source $VIRTUAL_ENV/bin/activate
cd $WEBAPP_DIR/backend
alembic upgrade head
```

**2. 配置 ebextensions**:

```yaml
# .ebextensions/01_env.config
option_settings:
  aws:elasticbeanstalk:application:environment:
    APP_DEBUG: false
    DATABASE_URL: "${DATABASE_URL}"
    JWT_SECRET_KEY: "${JWT_SECRET_KEY}"
```

**3. 部署**:

```bash
eb init
eb create production
eb open production
```

---

## 🔐 安全检查清单

### 必须完成的安全配置

- [ ] **JWT 密钥更换**: 使用至少 32 字符的强随机密钥
- [ ] **关闭 DEBUG 模式**: 生产环境必须设置 `APP_DEBUG=false`
- [ ] **数据库密码**: 使用强密码，不要使用默认密码
- [ ] **HTTPS 配置**: 配置 SSL 证书，强制 HTTPS
- [ ] **CORS 配置**: 限制允许的来源域名
- [ ] **防火墙配置**: 只开放必要端口（80, 443）
- [ ] **日志配置**: 配置日志轮转，避免磁盘占满
- [ ] **备份策略**: 配置数据库定时备份

### 生成强 JWT 密钥

```bash
# 方法 1: 使用 openssl
openssl rand -hex 32

# 方法 2: 使用 python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法 3: 使用 /dev/urandom
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
```

**示例**:

```bash
# 生成并更新到 .env
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
echo "JWT_SECRET_KEY=$JWT_SECRET" >> .env
```

---

## 📊 监控配置

### 1. 应用监控

**Prometheus + Grafana**:

```yaml
# 添加 prometheus-client 到 requirements.txt
prometheus-client==0.19.0
```

**添加监控端点**:

```python
# app/routes/metrics.py
from prometheus_client import generate_latest, CONTENT_TYPE

@app.route("/metrics")
async def metrics(request):
    return HTTPResponse(
        generate_latest(),
        content_type=CONTENT_TYPE
    )
```

### 2. 日志配置

**结构化日志**:

```python
# app/utils/logging_config.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
        }
        return json.dumps(log_data)
```

### 3. 告警配置

**关键指标**:

- CPU 使用率 > 80%
- 内存使用率 > 80%
- 错误率 > 1%
- 响应时间 P95 > 500ms
- Token 刷新失败率 > 5%

---

## 🧪 部署后验证

### 功能验证清单

```bash
# 1. 健康检查
curl http://api.cs-ops.com/health

# 2. 用户注册
curl -X POST http://api.cs-ops.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","email":"test@example.com"}'

# 3. 用户登录
curl -X POST http://api.cs-ops.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 4. Token 刷新
curl -X POST http://api.cs-ops.com/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJ..."}'

# 5. 受保护资源访问
curl http://api.cs-ops.com/api/v1/users/me \
  -H "Authorization: Bearer eyJ..."

# 6. 用户登出
curl -X POST http://api.cs-ops.com/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJ..."}'
```

### 性能验证

```bash
# 使用 wrk 进行压力测试
wrk -t12 -c400 -d30s http://api.cs-ops.com/api/v1/auth/login

# 期望结果:
# Latency: P50 < 50ms, P95 < 200ms, P99 < 500ms
# Throughput: > 1000 req/s
```

---

## 📝 部署检查清单

### 部署前

- [ ] 代码审查完成
- [ ] 所有测试通过（41/41）
- [ ] 代码覆盖率 > 80%
- [ ] Git 提交并推送
- [ ] .env 文件配置正确
- [ ] JWT 密钥已更换（生产）
- [ ] DEBUG 模式已关闭
- [ ] 数据库迁移脚本准备就绪
- [ ] 依赖安装脚本准备就绪

### 部署中

- [ ] 依赖安装完成
- [ ] 数据库迁移成功
- [ ] 应用启动成功
- [ ] 健康检查通过
- [ ] 日志正常输出
- [ ] 监控系统连接

### 部署后

- [ ] 功能验证通过（6 个端点测试）
- [ ] 性能验证通过（压力测试）
- [ ] 安全配置验证
- [ ] 备份策略配置
- [ ] 监控告警配置
- [ ] 文档更新

---

## 🆘 故障排除

### 常见问题

**问题 1: 数据库连接失败**

```bash
# 检查数据库是否运行
pg_isready -h localhost -p 5432

# 检查连接字符串
echo $DATABASE_URL

# 测试连接
psql $DATABASE_URL -c "SELECT 1"
```

**问题 2: 迁移失败**

```bash
# 查看当前迁移状态
alembic current

# 回滚到上一个版本
alembic downgrade -1

# 重新迁移
alembic upgrade head
```

**问题 3: Token 验证失败**

```bash
# 检查 JWT 密钥是否一致
grep JWT_SECRET_KEY .env

# 检查 Token 过期时间
python -c "from app.config.settings import settings; print(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)"

# 查看日志
tail -f /var/log/cs_ops/error.log | grep -i token
```

**问题 4: 速率限制触发**

```bash
# 检查配置
grep TOKEN_REFRESH_RATE_LIMIT .env

# 查看黑名单记录
psql $DATABASE_URL -c "SELECT count(*) FROM token_blacklists WHERE blacklisted_at > NOW() - INTERVAL '1 hour'"
```

---

## 📞 支持

- **技术文档**: `/docs/deployment.md`
- **部署脚本**: `/scripts/deploy.sh`
- **监控面板**: `http://grafana.cs-ops.com`
- **日志系统**: `http://logs.cs-ops.com`

---

**部署版本**: 0.1.0  
**更新日期**: 2026-02-28  
**Story 1.2**: JWT Token 管理 ✅
