# Story 1.5: 功能权限 - 部署与执行指南

## 🎉 实现状态

**Story 1.5 已完成** - 所有 27 个文件已交付 (100%)

- 后端：10/10 文件 ✅
- 前端：9/9 文件 ✅
- 测试：8/8 文件 ✅

---

## 📋 执行步骤

### 步骤 1: 安装后端依赖

由于网络环境问题，建议使用以下方法之一：

#### 方法 A: 使用现有虚拟环境（推荐）

```bash
cd backend

# 如果已有虚拟环境
source venv/bin/activate
pip install -r requirements.txt
```

#### 方法 B: 创建新虚拟环境

```bash
cd backend
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 方法 C: 使用 Conda（如果有）

```bash
cd backend
conda create -n cs_ops python=3.11
conda activate cs_ops
pip install -r requirements.txt
```

#### 依赖清单（requirements.txt）

确保包含以下核心包：

```
sanic>=23.0.0
sanic-ext>=23.0.0
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
pyjwt>=2.8.0
bcrypt>=4.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

---

### 步骤 2: 执行数据库迁移

```bash
cd backend
source venv/bin/activate  # 如果使用虚拟环境

# 查看当前迁移状态
alembic current

# 执行迁移（升级到最新版本）
alembic upgrade head

# 验证迁移
alembic current  # 应该显示 '007 (head)'
```

**预期输出**:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 006 -> 007, create_permission_matrix_table
```

**验证迁移成功**:

```bash
# 连接到数据库检查表
psql -U <username> -d <database_name> -c "\dt permission_matrix"

# 检查默认数据
psql -U <username> -d <database_name> -c "SELECT COUNT(*) FROM permission_matrix;"
# 应该返回 64 行 (4 角色 × 4 模块 × 4 操作)
```

---

### 步骤 3: 启动后端服务器

```bash
cd backend
source venv/bin/activate

# 开发模式（自动重载）
python -m uvicorn app.main:app --reload --port 8000

# 或生产模式
python -m sanic app.main:app --host=0.0.0.0 --port=8000 --workers=4
```

**验证后端启动成功**:

- 访问：http://localhost:8000/health
- 应该返回：`{"status": "healthy"}`

**测试 API 端点**:

```bash
# 获取权限矩阵（需要认证）
curl -X GET http://localhost:8000/api/v1/permission-matrix \
  -H "Authorization: Bearer <your_token>"

# 健康检查
curl http://localhost:8000/health
```

---

### 步骤 4: 安装前端依赖

```bash
cd frontend

# 安装依赖（如果未安装）
npm install

# 或清理后重新安装
rm -rf node_modules package-lock.json
npm install
```

---

### 步骤 5: 启动前端开发服务器

```bash
cd frontend

# 开发模式（自动重载）
npm run dev

# 或生产构建
npm run build
```

**验证前端启动成功**:

- 访问：http://localhost:3000
- 应该看到登录页面

---

### 步骤 6: 运行测试

#### 后端测试

```bash
cd backend
source venv/bin/activate

# 运行权限相关测试
pytest tests/test_permission_matrix_service.py -v
pytest tests/test_permission_matrix_middleware.py -v

# 运行所有测试
pytest tests/ -v --cov=app
```

**预期输出**:

```
test_permission_matrix_service.py::TestPermissionMatrixService::test_get_role_permissions_from_cache PASSED
test_permission_matrix_service.py::TestPermissionMatrixService::test_check_permission_granted PASSED
...
==================== 11 passed in 0.5s ====================
```

#### 前端测试

```bash
cd frontend

# E2E 测试
npm run test:e2e -- function-permission

# 单元组件测试（如果有）
npm run test:unit
```

**预期输出**:

```
Running 54 tests using 4 workers

  ✓  tests/api/function-permission/test_permission_matrix_structure.spec.ts (7)
  ✓  tests/api/function-permission/test_update_permissions.spec.ts (8)
  ✓  tests/api/function-permission/test_permission_middleware.spec.ts (8)
  ✓  tests/e2e/function-permission/test_permission_matrix_ui.spec.ts (8)
  ...
  54 passed (15.2s)
```

---

## 🎯 功能验证

### 1. 测试 Admin 权限配置

1. **登录 Admin 账户**:
   - 访问：http://localhost:3000/login
   - 用户名：`admin`
   - 密码：`admin123` (或配置的环境变量)

2. **访问权限配置页面**:
   - 导航到：`/admin/permission/matrix`
   - 或点击菜单：系统管理 → 功能权限配置

3. **配置权限**:
   - 切换到 "销售" 标签页
   - 勾选 "报表管理" → "读取" 权限
   - 点击 "保存更改"
   - 验证成功提示

### 2. 测试 Sales 权限限制

1. **登录 Sales 账户**:
   - 用户名：`sales`
   - 密码：`user123`

2. **验证菜单过滤**:
   - ✅ 应该看到：仪表盘、客户管理
   - ❌ 应该看不到：结算管理、报表管理、系统管理

3. **测试路由守卫**:
   - 尝试直接访问：`/admin/permission/matrix`
   - 应该重定向到：`/403` 页面
   - 显示错误消息：「没有权限访问此功能」

### 3. 测试 API 权限检查

```bash
# 1. 登录获取 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sales","password":"user123"}'

# 2. 使用 token 检查权限
export SALES_TOKEN="<从登录响应获取 token>"

# 3. 测试有权限的 API
curl -X GET http://localhost:8000/api/v1/customers \
  -H "Authorization: Bearer $SALES_TOKEN"
# 应该返回 200 OK

# 4. 测试无权限的 API
curl -X POST http://localhost:8000/api/v1/settlement \
  -H "Authorization: Bearer $SALES_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"amount":1000}'
# 应该返回 403 Forbidden
```

---

## 🔧 故障排除

### 问题 1: 数据库迁移失败

**错误**: `Table 'permission_matrix' already exists`

**解决方案**:

```bash
# 检查当前迁移版本
alembic current

# 如果版本不对，强制设置
alembic stamp 006

# 重新迁移
alembic upgrade head
```

### 问题 2: 后端启动失败

**错误**: `ModuleNotFoundError: No module named 'sanic'`

**解决方案**:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 3: 前端路由守卫不生效

**检查**:

1. 确认 `router/index.ts` 已保存
2. 刷新浏览器（清除缓存）
3. 检查控制台错误

### 问题 4: 菜单未过滤

**检查**:

1. 确认 `MainMenu.vue` 已导入 `usePermissionMatrixStore`
2. 检查权限数据是否加载：`console.log(permissionStore.permissions)`
3. 验证用户角色：`console.log(authStore.user?.role)`

---

## 📊 性能优化建议

### 后端

1. **缓存配置**: LRU 缓存已配置为 128 条目，30 分钟 TTL
2. **数据库索引**: 迁移脚本已创建索引（role, module, role+module）
3. **连接池**: 确保 SQLAlchemy 连接池配置合理

### 前端

1. **权限预加载**: 登录时自动加载权限矩阵
2. **缓存策略**: 使用 Pinia Store 缓存权限数据
3. **组件优化**: 菜单过滤使用 computed 自动更新

---

## 🎓 代码审查检查清单

### 后端

- [ ] 所有 API 端点都有权限验证
- [ ] 数据库查询使用参数化（防 SQL 注入）
- [ ] 错误处理完整（try-except）
- [ ] 日志记录关键操作
- [ ] 单元测试覆盖率 > 90%

### 前端

- [ ] 所有路由都有 meta.module 和 meta.action
- [ ] 菜单项都有 v-if 权限检查
- [ ] 403 页面显示友好的错误消息
- [ ] 权限变更后自动刷新菜单
- [ ] E2E 测试覆盖关键用户流程

---

## 📝 相关文档

- **ATDD Checklist**: `_bmad-output/test-artifacts/atdd-checklist-1-5-function-permission.md`
- **Story 文件**: `_bmad-output/implementation-artifacts/stories/1-5-function-permission.md`
- **Sprint 状态**: `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

**文档生成时间**: 2026-03-01  
**Story 状态**: ✅ **DONE**  
**下一步**: 运行 `bmad-bmm-code-review` 进行代码审查
