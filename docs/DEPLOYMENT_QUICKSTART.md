# 🚀 CS Ops 部署快速参考

> 一键部署指南 - 3 分钟快速上手

---

## ⚡ 快速开始

### 方式 1: 一键部署脚本（推荐）

```bash
# 1. 准备配置
cd backend
cp .env.example .env.production
# 编辑 .env.production 配置数据库和 JWT 密钥

# 2. 执行部署
chmod +x scripts/deploy-prod.sh
./scripts/deploy-prod.sh
```

**部署完成后**:

- ✅ 后端 API: http://localhost:8000
- ✅ 健康检查：http://localhost:8000/health
- ✅ 日志目录：`/var/log/cs_ops/`

---

### 方式 2: Docker Compose 部署

```bash
# 1. 配置环境变量
cp .env.docker .env
# 编辑 .env，修改 JWT_SECRET_KEY

# 2. 一键启动
docker-compose up -d
docker-compose --profile migrate up migrate

# 3. 查看状态
docker-compose ps
docker-compose logs -f
```

**服务端口**:

- 前端：http://localhost:80
- 后端：http://localhost:8000
- 数据库：localhost:5432

---

### 方式 3: Make 命令部署

```bash
# 开发环境
make deploy-dev

# 生产环境
make deploy-prod

# Docker 部署
make deploy-docker

# 查看帮助
make help
```

---

## 📋 部署前检查清单

### 环境要求

- [ ] Python 3.11+
- [ ] Node.js 18+
- [ ] PostgreSQL 15+
- [ ] Git

### 配置检查

- [ ] `.env.production` 已创建并配置
- [ ] `JWT_SECRET_KEY` 已更换（32+ 字符）
- [ ] `APP_DEBUG=false`（生产环境）
- [ ] 数据库连接字符串正确
- [ ] 数据库已创建

### 快速验证命令

```bash
# 检查 Python 版本
python3 --version

# 检查 Node 版本
node --version

# 检查 PostgreSQL
psql --version

# 检查 Git
git --version
```

---

## 🔧 常用命令

### 服务管理

```bash
# 查看服务状态
sudo systemctl status cs_ops_backend

# 重启服务
sudo systemctl restart cs_ops_backend

# 停止服务
sudo systemctl stop cs_ops_backend

# 查看日志
tail -f /var/log/cs_ops/error.log
tail -f /var/log/cs_ops/access.log
```

### Docker 管理

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 进入容器
docker-compose exec backend bash
```

### 数据库管理

```bash
# 执行迁移
cd backend && source .venv/bin/activate
alembic upgrade head

# 查看迁移状态
alembic current

# 回滚迁移
alembic downgrade -1

# 备份数据库
pg_dump -h localhost -U cs_ops_user cs_ops > backup.sql

# 恢复数据库
psql -h localhost -U cs_ops_user cs_ops < backup.sql
```

---

## 🧪 验证部署

### 健康检查

```bash
# 检查健康状态
curl http://localhost:8000/health

# 期望响应
# {"status": "healthy", "timestamp": "...", "version": "0.1.0"}
```

### 功能测试

```bash
# 1. 用户注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","email":"test@example.com"}'

# 2. 用户登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 3. 获取 Token
# 响应应包含 access_token 和 refresh_token

# 4. 访问受保护资源
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 性能测试

```bash
# 使用 ab 进行压力测试
ab -n 1000 -c 10 http://localhost:8000/health

# 期望结果
# Requests per second: > 1000
# Time per request: < 10ms
```

---

## 🔐 安全配置

### 必须完成的安全项

- [ ] **JWT 密钥**: 使用 32+ 字符强随机密钥

  ```bash
  openssl rand -hex 32
  ```

- [ ] **关闭 DEBUG**: `APP_DEBUG=false`

- [ ] **数据库密码**: 使用强密码

- [ ] **HTTPS**: 配置 SSL 证书

- [ ] **防火墙**: 只开放 80, 443 端口

- [ ] **备份**: 配置定时备份

### 生成安全密钥

```bash
# JWT 密钥
openssl rand -hex 32

# 数据库密码
openssl rand -base64 24

# 或使用 Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 故障排除

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查数据库是否运行
pg_isready -h localhost -p 5432

# 测试连接
psql $DATABASE_URL -c "SELECT 1"

# 检查防火墙
sudo ufw status
```

#### 2. 端口被占用

```bash
# 查看端口占用
lsof -i :8000

# 杀死占用端口的进程
kill -9 $(lsof -t -i:8000)
```

#### 3. 迁移失败

```bash
# 查看当前版本
alembic current

# 回滚
alembic downgrade -1

# 重新迁移
alembic upgrade head
```

#### 4. 应用启动失败

```bash
# 查看详细日志
tail -f /var/log/cs_ops/error.log

# 检查依赖
cd backend && source .venv/bin/activate
pip check

# 手动启动调试
python -m app.main
```

#### 5. Docker 问题

```bash
# 查看容器状态
docker-compose ps

# 查看容器日志
docker-compose logs backend

# 重建容器
docker-compose up -d --force-recreate

# 清理网络
docker network prune
```

---

## 📊 监控配置

### 日志监控

```bash
# 实时查看错误日志
tail -f /var/log/cs_ops/error.log | grep -i error

# 查看访问日志
tail -f /var/log/cs_ops/access.log

# 统计错误数量
grep -c "ERROR" /var/log/cs_ops/error.log
```

### 性能监控

**关键指标**:

- CPU 使用率：`top -p $(cat /tmp/cs_ops_backend.pid)`
- 内存使用率：`ps -p $(cat /tmp/cs_ops_backend.pid) -o %mem`
- 响应时间：查看访问日志

**告警阈值**:

- CPU > 80%
- 内存 > 80%
- 错误率 > 1%
- P95 响应时间 > 500ms

---

## 🔄 部署流程

### 标准部署流程

```
1. 代码审查完成
   ↓
2. 运行测试 (make ci-test)
   ↓
3. 提交到 Git
   ↓
4. 拉取最新代码
   ↓
5. 备份数据库
   ↓
6. 执行部署脚本
   ↓
7. 健康检查
   ↓
8. 功能验证
   ↓
9. 监控告警配置
   ↓
10. 部署完成
```

### 回滚流程

```bash
# 1. 停止服务
sudo systemctl stop cs_ops_backend

# 2. 恢复代码
git reset --hard HEAD~1

# 3. 恢复数据库
pg_dump -h localhost -U cs_ops_user cs_ops > backups/$(date +%Y%m%d_%H%M%S).sql

# 4. 重启服务
sudo systemctl start cs_ops_backend

# 5. 验证服务
curl http://localhost:8000/health
```

---

## 📖 相关文档

- **完整部署检查清单**: `docs/DEPLOYMENT_CHECKLIST.md`
- **架构文档**: `docs/architecture.md`
- **开发指南**: `docs/development.md`
- **项目 README**: `README.md`

---

## 🆘 获取帮助

### 内部资源

- **部署脚本**: `scripts/deploy-prod.sh`
- **环境配置**: `backend/.env.example`
- **Docker 配置**: `docker-compose.yml`
- **Make 命令**: `Makefile`

### 外部资源

- **PostgreSQL 文档**: https://www.postgresql.org/docs/
- **Sanic 文档**: https://sanic.dev/
- **Docker 文档**: https://docs.docker.com/
- **Gunicorn 文档**: https://docs.gunicorn.org/

---

**文档版本**: 1.0  
**最后更新**: 2026-03-02  
**维护者**: Sacrtap
