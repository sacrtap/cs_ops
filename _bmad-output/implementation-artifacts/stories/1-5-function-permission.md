# Story 1.5: 功能权限 (Function Permission)

**Status**: ready-for-dev  
**Epic**: 1 - 权限与认证 (基础设施 - 优先实施)  
**Story ID**: 1.5  
**Story Key**: 1-5-function-permission  
**Priority**: HIGH  
**Estimated Effort**: Medium

---

## Story

**As a** Admin 用户，  
**I want** 通过权限矩阵配置用户对功能的访问权限，  
**So that** 实现精细化的功能权限控制，确保用户只能访问其角色授权的功能。

---

## Acceptance Criteria

### AC1: 权限矩阵数据结构

```gherkin
Given Admin 用户进入权限配置页面
When 查看权限矩阵
Then 显示所有功能模块（客户管理、结算管理、数据权限等）
And 每个功能支持 4 级操作权限（read/create/update/delete）
And 每个角色（Admin/经理/专员/销售）可独立配置
```

### AC2: 权限配置保存

```gherkin
Given Admin 用户修改了某个角色的权限
When 点击"保存权限配置"
Then 验证权限矩阵完整性（每个角色至少有一个功能权限）
And 保存到 permission_matrix 表
And 记录操作日志到 audit_logs
And 权限立即生效
```

### AC3: 前端功能权限控制

```gherkin
Given 用户登录系统
When 加载菜单和页面
Then 根据用户角色查询权限矩阵
And 有权限的功能显示菜单入口
And 无权限的功能隐藏菜单或显示灰色不可点击
And 直接访问 URL 也进行权限检查
```

### AC4: 后端 API 权限验证

```gherkin
Given 用户请求受保护的 API
When 请求通过 permission_middleware
Then 检查用户角色是否有该 API 的操作权限
And 有权限则继续处理请求
And 无权限则返回 403 PERMISSION_DENIED
And 记录越权访问日志
```

### AC5: 权限缓存与刷新

```gherkin
Given 权限配置已保存
When 用户下次请求 API
Then 从缓存读取权限矩阵（提高性能）
And 缓存过期时间 30 分钟
And Admin 修改权限后清除相关缓存
And 用户下次请求自动应用新权限
```

### AC6: 默认权限矩阵

```gherkin
Given 系统初始化或权限表为空
When 首次加载权限矩阵
Then 应用默认权限配置：
  - Admin: 所有功能的所有操作
  - 经理：大部分功能的 read/update
  - 专员：大部分功能的 read/create/update
  - 销售：仅客户相关功能的 read
And 默认权限可被 Admin 修改
```

---

## Technical Requirements

### 权限矩阵数据模型

**权限表结构** (`permission_matrix` 表):

```sql
CREATE TABLE permission_matrix (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,              -- 角色：admin/manager/specialist/sales
    module VARCHAR(100) NOT NULL,           -- 功能模块：customer/settlement/reporting
    action VARCHAR(20) NOT NULL,            -- 操作：read/create/update/delete
    granted BOOLEAN NOT NULL DEFAULT true,  -- 是否授权
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(role, module, action)
);

-- 索引优化
CREATE INDEX idx_permission_role ON permission_matrix(role);
CREATE INDEX idx_permission_module ON permission_matrix(module);
CREATE INDEX idx_permission_role_module ON permission_matrix(role, module);
```

**权限矩阵默认值**:

| 角色  | 模块         | read | create | update | delete |
| ----- | ------------ | ---- | ------ | ------ | ------ |
| Admin | **所有模块** | ✅   | ✅     | ✅     | ✅     |
| 经理  | customer     | ✅   | ✅     | ✅     | ❌     |
| 经理  | settlement   | ✅   | ❌     | ✅     | ❌     |
| 经理  | reporting    | ✅   | ❌     | ❌     | ❌     |
| 专员  | customer     | ✅   | ✅     | ✅     | ❌     |
| 专员  | settlement   | ✅   | ✅     | ✅     | ❌     |
| 专员  | reporting    | ✅   | ❌     | ❌     | ❌     |
| 销售  | customer     | ✅   | ❌     | ✅     | ❌     |
| 销售  | settlement   | ✅   | ❌     | ❌     | ❌     |
| 销售  | reporting    | ❌   | ❌     | ❌     | ❌     |

### 后端技术栈要求

**必须遵循的技术规范** (来自 project-context.md):

- ✅ **Python 3.11+** async/await 用于所有 I/O 操作
- ✅ **SQLAlchemy 2.0+** 使用 async_session 和 select() 语法
- ✅ **Sanic** 异步请求处理，使用 Blueprints 组织路由
- ✅ **Pydantic** 用于请求/响应验证
- ✅ **类型注解** 所有函数必须有类型提示
- ✅ **Redis 缓存** 用于权限矩阵缓存（可选，LRU cache 作为备选）

**权限服务接口**:

```python
from typing import Dict, List, Optional
from app.models.permission_matrix import PermissionMatrix

class PermissionMatrixService:
    async def get_role_permissions(self, role: str) -> Dict[str, Dict[str, bool]]:
        """获取角色的所有权限（模块 → 操作 → 是否授权）"""
        pass

    async def check_permission(self, role: str, module: str, action: str) -> bool:
        """检查角色是否有某功能的某操作权限"""
        pass

    async def update_permission(self, role: str, module: str, action: str, granted: bool) -> None:
        """更新单个权限配置"""
        pass

    async def bulk_update_permissions(self, permissions: List[Dict]) -> None:
        """批量更新权限配置"""
        pass

    async def get_default_permissions(self) -> List[Dict]:
        """获取默认权限矩阵"""
        pass
```

**权限中间件增强** (在 Story 1.3 基础上):

```python
from sanic import Request
from sanic.exceptions import HTTPException
from app.services.permission_matrix_service import PermissionMatrixService

async def permission_matrix_middleware(request: Request):
    """功能权限验证中间件"""
    # 跳过公开 API
    if request.path in PUBLIC_ENDPOINTS:
        return

    # 获取用户角色（从 JWT）
    user = request.ctx.user
    role = user.role

    # 解析权限需求（从路由元数据或配置）
    required_module, required_action = extract_permission_requirement(request)

    # 检查权限
    service = PermissionMatrixService()
    has_permission = await service.check_permission(role, required_module, required_action)

    if not has_permission:
        # 记录越权访问
        await log_permission_denied(user, required_module, required_action)

        raise HTTPException(
            status_code=403,
            message=f"您没有权限访问此功能",
            context={
                "required_module": required_module,
                "required_action": required_action,
                "user_role": role
            }
        )
```

**标准响应格式**:

```python
# 成功响应 - 获取权限矩阵
{
    "data": {
        "admin": {
            "customer": {"read": true, "create": true, "update": true, "delete": true},
            "settlement": {"read": true, "create": true, "update": true, "delete": true},
            ...
        },
        "manager": {...},
        "specialist": {...},
        "sales": {...}
    },
    "meta": {
        "total": 4,
        "timestamp": "2026-03-01T10:30:00.000Z",
        "request_id": "req-xxx"
    },
    "error": None
}

# 越权访问错误
{
    "data": None,
    "meta": {...},
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "您没有权限访问此功能",
        "details": {
            "required_module": "settlement",
            "required_action": "create",
            "user_role": "sales"
        }
    }
}
```

---

## Dev Agent Guardrails

### Technical Requirements

**后端实现清单**:

- [ ] `backend/app/models/permission_matrix.py` - 权限矩阵模型 (新增)
- [ ] `backend/app/services/permission_matrix_service.py` - 权限矩阵服务 (新增)
- [ ] `backend/app/routes/permission_matrix_routes.py` - 权限矩阵路由 (新增)
- [ ] `backend/app/middleware/permission_matrix_middleware.py` - 功能权限中间件 (新增或 Story 1.3 已有)
- [ ] `backend/alembic/versions/007_create_permission_matrix.py` - 数据库迁移 (新增)
- [ ] `backend/tests/test_permission_matrix_service.py` - 服务测试 (新增)
- [ ] `backend/tests/test_permission_matrix_middleware.py` - 中间件测试 (新增)
- [ ] `backend/app/utils/permission_cache.py` - 权限缓存工具 (新增)

**前端实现清单**:

- [ ] `frontend/src/types/permission-matrix.ts` - 类型定义 (新增)
- [ ] `frontend/src/api/permission-matrix.ts` - API 客户端 (新增)
- [ ] `frontend/src/stores/permission-matrix.ts` - Pinia Store (新增)
- [ ] `frontend/src/utils/permission-check.ts` - 权限检查工具 (新增)
- [ ] `frontend/src/views/admin/permission/MatrixConfig.vue` - 权限矩阵配置页面 (新增)
- [ ] `frontend/src/components/business/permission/PermissionMatrixEditor.vue` - 权限编辑组件 (新增)
- [ ] `frontend/src/components/business/permission/FunctionAccessGuard.vue` - 功能访问守卫组件 (新增)
- [ ] `frontend/src/router/index.ts` - 路由权限集成 (修改)
- [ ] `frontend/src/layout/MainMenu.vue` - 菜单权限过滤 (修改)

### Architecture Compliance

**必须遵循的架构规则**:

1. **权限验证流程**:

   ```
   请求 → JWT 验证 → 功能权限中间件 → 数据权限中间件 → 路由处理器
                        ↓
                解析权限需求 (module, action)
                        ↓
                查询权限矩阵缓存
                        ↓
                验证角色是否有权限
                        ↓
           有权限 → 继续 | 无权限 → 403 错误
   ```

2. **权限缓存策略**:

   ```python
   # 使用 LRU cache 或 Redis
   from functools import lru_cache
   from typing import Dict

   class PermissionMatrixService:
       @lru_cache(maxsize=128)
       async def get_role_permissions(self, role: str) -> Dict:
           # 从数据库查询
           permissions = await self._query_from_db(role)
           return permissions

       async def clear_cache(self, role: Optional[str] = None):
           """清除权限缓存"""
           if role:
               self.get_role_permissions.cache_clear()
           else:
               # 清除所有角色缓存
               self.get_role_permissions.cache_clear()
   ```

3. **路由权限元数据定义**:

   ```python
   # 在路由定义时声明权限需求
   from app.middleware.permission_matrix_middleware import require_permission

   @permission_bp.route("/settlement", methods=["POST"])
   @require_permission(module="settlement", action="create")
   async def create_settlement(request):
       # 只有有 settlement.create 权限的角色可访问
       pass

   @customer_bp.route("/", methods=["GET"])
   @require_permission(module="customer", action="read")
   async def list_customers(request):
       # 只有有 customer.read 权限的角色可访问
       pass
   ```

4. **前端路由守卫**:

   ```typescript
   // router/index.ts
   import { useAuthStore } from "@/stores/auth";
   import { usePermissionMatrixStore } from "@/stores/permission-matrix";

   router.beforeEach(async (to, from, next) => {
     const authStore = useAuthStore();
     const permissionStore = usePermissionMatrixStore();

     // 跳过公开路由
     if (to.meta.public) {
       return next();
     }

     // 检查登录
     if (!authStore.isAuthenticated) {
       return next("/login");
     }

     // 检查功能权限
     const requiredModule = to.meta.module as string;
     const requiredAction = (to.meta.action as string) || "read";

     if (requiredModule) {
       const hasPermission = permissionStore.hasPermission(
         requiredModule,
         requiredAction,
       );
       if (!hasPermission) {
         return next("/403");
       }
     }

     next();
   });
   ```

5. **前端菜单权限过滤**:

   ```typescript
   // components/layout/MainMenu.vue
   import { computed } from "vue";
   import { usePermissionMatrixStore } from "@/stores/permission-matrix";

   const permissionStore = usePermissionMatrixStore();

   const filteredMenuItems = computed(() => {
     return menuItems.filter((item) => {
       // 检查菜单项是否需要权限
       if (!item.module) return true;

       // 检查用户是否有该模块的 read 权限
       return permissionStore.hasPermission(item.module, "read");
     });
   });
   ```

### Library/Framework Requirements

**后端依赖** (使用现有库):

```
# Story 1.3 已有依赖
sanic>=23.0.0
sqlalchemy[asyncio]>=2.0.0
python-jose[cryptography]>=3.3.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0

# 可选：Redis 缓存（如果没有，使用 LRU cache）
redis>=5.0.0
```

### File Structure Requirements

**后端目录结构**:

```
backend/
├── app/
│   ├── models/
│   │   ├── permission_matrix.py       # 新增 - 权限矩阵模型
│   │   └── user.py                    # 已有，包含 role 字段
│   ├── services/
│   │   ├── permission_matrix_service.py  # 新增 - 权限矩阵服务
│   │   └── permission_service.py      # Story 1.3 已有
│   ├── routes/
│   │   ├── permission_matrix_routes.py   # 新增 - 权限矩阵路由
│   │   └── permission_routes.py       # Story 1.3 已有
│   ├── middleware/
│   │   ├── auth_middleware.py         # Story 1.1 已有
│   │   ├── permission_middleware.py   # Story 1.3 已有
│   │   └── permission_matrix_middleware.py # 新增 - 功能权限中间件
│   └── utils/
│       └── permission_cache.py        # 新增 - 权限缓存工具
├── alembic/
│   └── versions/
│       └── 007_create_permission_matrix.py # 新增
└── tests/
    ├── test_permission_matrix_service.py  # 新增
    └── test_permission_matrix_middleware.py # 新增
```

**前端目录结构**:

```
frontend/
├── src/
│   ├── types/
│   │   └── permission-matrix.ts       # 新增
│   ├── api/
│   │   └── permission-matrix.ts       # 新增
│   ├── stores/
│   │   ├── auth.ts                    # Story 1.1 已有
│   │   ├── permission.ts              # Story 1.3 已有
│   │   └── permission-matrix.ts       # 新增
│   ├── utils/
│   │   └── permission-check.ts        # 新增
│   ├── components/
│   │   └── business/
│   │       └── permission/
│   │           ├── MatrixConfig.vue          # 新增 - 配置页面
│   │           ├── PermissionMatrixEditor.vue # 新增 - 编辑组件
│   │           └── FunctionAccessGuard.vue    # 新增 - 访问守卫
│   ├── views/
│   │   └── admin/
│   │       └── permission/
│   │           └── MatrixConfig.vue   # 新增 - Admin 配置页
│   ├── router/
│   │   └── index.ts                   # 修改 - 添加权限守卫
│   └── layout/
│       └── MainMenu.vue               # 修改 - 菜单权限过滤
```

### Testing Requirements

**后端测试场景** (pytest):

```python
# test_permission_matrix_service.py
import pytest
from app.services.permission_matrix_service import PermissionMatrixService
from app.models.permission_matrix import PermissionMatrix

@pytest.mark.asyncio
async def test_check_permission_admin_all_access():
    """Admin 角色拥有所有权限"""
    service = PermissionMatrixService()

    # Admin 应该有所有权限
    assert await service.check_permission('admin', 'customer', 'read') is True
    assert await service.check_permission('admin', 'customer', 'create') is True
    assert await service.check_permission('admin', 'settlement', 'delete') is True

@pytest.mark.asyncio
async def test_check_permission_sales_limited_access():
    """销售角色权限受限"""
    service = PermissionMatrixService()

    # 销售只能 read 客户
    assert await service.check_permission('sales', 'customer', 'read') is True
    assert await service.check_permission('sales', 'customer', 'create') is False
    assert await service.check_permission('sales', 'settlement', 'read') is False

@pytest.mark.asyncio
async def test_update_permission():
    """测试权限更新"""
    service = PermissionMatrixService()

    # 初始状态
    initial = await service.check_permission('sales', 'reporting', 'read')

    # 更新权限
    await service.update_permission('sales', 'reporting', 'read', True)

    # 验证更新后
    updated = await service.check_permission('sales', 'reporting', 'read')
    assert updated is True

    # 清理：恢复原状
    await service.update_permission('sales', 'reporting', 'read', initial)

@pytest.mark.asyncio
async def test_get_role_permissions():
    """获取角色所有权限"""
    service = PermissionMatrixService()

    permissions = await service.get_role_permissions('manager')

    assert 'customer' in permissions
    assert 'settlement' in permissions
    assert permissions['customer']['read'] is True
    assert permissions['customer']['delete'] is False  # 经理不能删除

# test_permission_matrix_middleware.py
@pytest.mark.asyncio
async def test_permission_middleware_allow_access():
    """中间件允许有权限的请求"""
    # 创建有权限的用户
    user = User(id=1, role='admin')
    request = MockRequest(path='/api/v1/customers', user=user)

    # 执行中间件
    await permission_matrix_middleware(request)

    # 应该不抛异常，继续处理

@pytest.mark.asyncio
async def test_permission_middleware_deny_access():
    """中间件拒绝无权限的请求"""
    # 创建无权限的用户
    user = User(id=1, role='sales')
    request = MockRequest(path='/api/v1/settlement', method='POST', user=user)

    # 执行中间件应该抛 403
    with pytest.raises(HTTPException) as exc_info:
        await permission_matrix_middleware(request)

    assert exc_info.value.status == 403
    assert exc_info.value.message == "您没有权限访问此功能"
```

**前端测试场景** (Vitest):

```typescript
// permission-matrix.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { usePermissionMatrixStore } from "@/stores/permission-matrix";
import { hasFunctionPermission } from "@/utils/permission-check";

describe("Permission Matrix Store", () => {
  let store: ReturnType<typeof usePermissionMatrixStore>;

  beforeEach(() => {
    store = usePermissionMatrixStore();
    // 设置测试数据
    store.setPermissions({
      sales: {
        customer: { read: true, create: false, update: true, delete: false },
        settlement: {
          read: false,
          create: false,
          update: false,
          delete: false,
        },
      },
    });
  });

  it("check permission for sales role", () => {
    store.setRole("sales");

    expect(store.hasPermission("customer", "read")).toBe(true);
    expect(store.hasPermission("customer", "create")).toBe(false);
    expect(store.hasPermission("settlement", "read")).toBe(false);
  });

  it("update permission", async () => {
    await store.updatePermission("sales", "settlement", "read", true);

    expect(store.hasPermission("settlement", "read")).toBe(true);
  });
});

describe("Permission Check Utils", () => {
  it("check function access", () => {
    const user = { role: "sales" };
    const permissions = {
      sales: {
        customer: { read: true, create: false },
      },
    };

    expect(hasFunctionPermission(user, "customer", "read", permissions)).toBe(
      true,
    );
    expect(hasFunctionPermission(user, "customer", "create", permissions)).toBe(
      false,
    );
  });
});
```

**测试覆盖率要求**:

- 后端：90%+ (权限矩阵服务 + 中间件核心逻辑 100%)
- 前端：80%+ (Store + 工具函数 + 组件)

---

## Previous Story Intelligence

### 来自 Story 1.4 (数据权限)

**已实现功能**:

- ✅ 数据权限过滤器（基于 org_id 和 sales_rep_id）
- ✅ 客户模型和组织模型
- ✅ 数据权限中间件（自动应用 WHERE 条件）

**复用代码**:

```python
# 从 Story 1.4 复用
from app.middleware.permission_matrix_middleware import require_permission

# 与数据权限中间件集成
app.register_middleware(auth_middleware)           # 第 1：验证 JWT
app.register_middleware(permission_matrix_middleware)  # 第 2：验证功能权限
app.register_middleware(data_permission_middleware)    # 第 3：应用数据过滤
```

**集成点**:

- 功能权限验证在数据权限之前执行
- 功能权限决定"能否访问此功能"
- 数据权限决定"能看到哪些数据"

### 来自 Story 1.3 (权限管理 - RBAC)

**已实现功能**:

- ✅ 4 级 RBAC 角色模型（Admin/经理/专员/销售）
- ✅ 用户表 `role` 字段
- ✅ 权限服务：`permission_service.py`
- ✅ 权限中间件基础框架

**待改进点** (来自 Story 1.3 Review):

- ⚠️ 角色层级验证逻辑重复 → **本 Story 使用权限矩阵统一管理**
- ⚠️ 权限缓存未设置过期时间 → **本 Story 实现 LRU cache**
- ✅ 权限中间件基础框架已就绪 → **本 Story 增强为矩阵验证**

### 来自 Story 1.2 (JWT Token 管理)

**已实现功能**:

- ✅ Token claims 包含 `role` 字段
- ✅ Token 服务：`token_service.py`
- ✅ 前端 Auth Store 已存储用户角色

**集成点**:

```python
# JWT claims 示例
claims = {
    "sub": str(user.id),
    "username": user.username,
    "role": user.role,        # ← 用于功能权限验证
    "org_id": user.org_id,    # ← 用于数据权限
    "type": "access",
    "exp": datetime.utcnow() + timedelta(minutes=120)
}
```

---

## Git Intelligence Summary

**最近提交模式**:

```
920cb9a feat(data-permission): Story 1.4 complete ✅
9736d35 feat(jwt): Story 1.2 token management ✅
b87b69f feat(deploy): Story 1.2 deployment
...
```

**代码约定**:

- 提交信息：`feat({module}): description`
- 文件命名：snake_case (Python), PascalCase (Vue)
- 迁移文件：`{sequence}_{description}.py` (007_create_permission_matrix)
- 测试文件：`test_*.py`

---

## Latest Tech Information

**2026 年功能权限最佳实践**:

1. **基于策略的权限控制 (PBAC)**:
   - 比 RBAC 更灵活，支持动态条件
   - 适合复杂业务场景
   - 实现成本较高

2. **权限矩阵 + 缓存**:
   - 简单直接，性能优秀
   - 支持动态配置
   - 推荐：LRU cache + 定期刷新

3. **实时权限验证**:
   - 每次请求都查询数据库
   - 保证权限即时生效
   - 性能开销大，不推荐

**推荐方案**: 权限矩阵 + LRU cache (30 分钟过期) + Admin 修改后清除缓存

---

## Project Context Reference

**必读项目上下文**:

- 📄 `/_bmad-output/project-context.md` - 150+ 条关键规则

**关键规则摘要**:

```python
# SQLAlchemy 2.0 异步模式 (必须使用)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async with async_session() as session:
    result = await session.execute(select(PermissionMatrix))
    permissions = result.scalars().all()

# 类型注解 (必须)
from typing import Dict, List, Optional

async def check_permission(
    role: str,
    module: str,
    action: str
) -> bool:
    """检查角色是否有某功能的某操作权限"""
    ...

# 标准错误响应格式
from sanic.exceptions import HTTPException

raise HTTPException(
    status_code=403,
    message="您没有权限访问此功能",
    context={
        "required_module": "settlement",
        "required_action": "create"
    }
)
```

**Critical Don't-Miss Rules**:

- ✅ ALL API endpoints MUST require permission matrix check
- ✅ Users can ONLY access authorized functions
- ✅ Use LRU cache for permission matrix (30 min TTL)
- ✅ Test permission filtering in all API endpoints
- ✅ NEVER expose permission matrix to unauthorized users
- ✅ Admin role MUST have all permissions by default

---

## Story Completion Status

**实现检查清单**:

- [ ] **数据库迁移**
  - [ ] 创建 permission_matrix 表迁移 `007_create_permission_matrix.py`
  - [ ] 插入默认权限数据
  - [ ] 运行迁移并验证

- [ ] **后端实现**
  - [ ] 创建 PermissionMatrix 模型
  - [ ] 创建 PermissionMatrixService 服务
  - [ ] 创建权限矩阵路由
  - [ ] 创建功能权限中间件
  - [ ] 实现权限缓存工具
  - [ ] 编写服务测试
  - [ ] 编写中间件测试

- [ ] **前端实现**
  - [ ] 创建类型定义
  - [ ] 创建 API 客户端
  - [ ] 创建权限矩阵 Store
  - [ ] 创建权限检查工具
  - [ ] 创建权限配置页面
  - [ ] 创建权限编辑组件
  - [ ] 创建访问守卫组件
  - [ ] 集成路由守卫
  - [ ] 集成菜单权限过滤

- [ ] **代码审查**
  - [ ] 审查后端实现
  - [ ] 审查前端实现
  - [ ] 审查测试覆盖
  - [ ] 修复所有审查问题

- [ ] **测试验证**
  - [ ] 运行服务单元测试
  - [ ] 运行中间件集成测试
  - [ ] 运行 E2E 测试

- [ ] **文档更新**
  - [ ] 更新 API 文档说明权限矩阵行为
  - [ ] 更新部署清单

---

### Dev Agent Record

### Debug Log References

- Sprint status 分析：`_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics 需求来源：`_bmad-output/planning-artifacts/epics.md` (Story 1.5: 功能权限)
- 架构模式来源：`_bmad-output/planning-artifacts/architecture.md` (Session-level 权限过滤)
- 前序故事：`_bmad-output/implementation-artifacts/stories/1-4-data-permission.md`
- 前序故事：`_bmad-output/implementation-artifacts/stories/1-3-permission-management.md`

### Completion Notes List

- ✅ 功能权限矩阵基于 epics.md 中的 FR37 要求
- ✅ 使用权限矩阵表存储角色 - 模块 - 操作映射
- ✅ 集成 Story 1.3 的 RBAC 角色模型
- ✅ 集成 Story 1.4 的数据权限中间件（功能权限 → 数据权限顺序）
- ✅ 权限缓存使用 LRU cache（30 分钟过期）
- ✅ 前端菜单自动过滤无权限项
- ✅ 路由守卫阻止无权限访问

### File List

**待创建 - 后端文件** (8 个):

1. `backend/app/models/permission_matrix.py` - 权限矩阵模型
2. `backend/app/services/permission_matrix_service.py` - 权限矩阵服务
3. `backend/app/routes/permission_matrix_routes.py` - 权限矩阵路由
4. `backend/app/middleware/permission_matrix_middleware.py` - 功能权限中间件
5. `backend/app/utils/permission_cache.py` - 权限缓存工具
6. `backend/alembic/versions/007_create_permission_matrix.py` - 数据库迁移
7. `backend/tests/test_permission_matrix_service.py` - 服务测试
8. `backend/tests/test_permission_matrix_middleware.py` - 中间件测试

**待创建 - 前端文件** (9 个):

1. `frontend/src/types/permission-matrix.ts` - 类型定义
2. `frontend/src/api/permission-matrix.ts` - API 客户端
3. `frontend/src/stores/permission-matrix.ts` - Pinia Store
4. `frontend/src/utils/permission-check.ts` - 权限检查工具
5. `frontend/src/views/admin/permission/MatrixConfig.vue` - Admin 配置页
6. `frontend/src/components/business/permission/PermissionMatrixEditor.vue` - 编辑组件
7. `frontend/src/components/business/permission/FunctionAccessGuard.vue` - 访问守卫
8. `frontend/src/router/index.ts` - 路由权限集成 (修改)
9. `frontend/src/layout/MainMenu.vue` - 菜单权限过滤 (修改)

---

## Change Log

### YYYY-MM-DD - Story 待创建

**创建者**: BMAD Create-Story Workflow  
**创建范围**: 完整故事上下文引擎

**创建文件**:

- `_bmad-output/implementation-artifacts/stories/1-5-function-permission.md`

**内容来源**:

- ✅ Epics.md: Story 1.5 验收标准和技术要求
- ✅ Architecture.md: 权限矩阵架构模式
- ✅ Project-context.md: 150+ 条关键规则
- ✅ Story 1.4: 数据权限中间件集成
- ✅ Story 1.3: RBAC 角色模型
- ✅ Story 1.2: JWT Token 集成（role claims）

**关键特性**:

- ✅ 权限矩阵数据模型清晰定义
- ✅ LRU cache 实现模式
- ✅ 前端菜单权限过滤
- ✅ 路由守卫集成
- ✅ 完整的测试场景覆盖
- ✅ 前后端实现清单详细列出

**Sprint 状态更新**:

- Story 1.5 状态：`backlog` → `ready-for-dev`

---
