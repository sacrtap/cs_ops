# Story 1.6: 角色管理 (Role Management)

**Status**: ready-for-dev  
**Epic**: 1 - 权限与认证 (基础设施 - 优先实施)  
**Story ID**: 1.6  
**Story Key**: 1-6-role-management  
**Priority**: HIGH  
**Estimated Effort**: Medium

---

## Story

**As a** Admin 用户，  
**I want** 管理角色和权限映射，  
**So that** 灵活配置权限，实现角色级别权限管理。

---

## Acceptance Criteria

### AC1: 角色列表展示

```gherkin
Given Admin 用户进入角色管理页面
When 查看角色列表
Then 显示所有系统角色（Admin/经理/专员/销售）
And 每个角色显示关联的权限数量
And 支持按角色名称搜索和筛选
```

### AC2: 角色权限配置

```gherkin
Given Admin 用户点击某个角色的"配置权限"按钮
When 进入角色权限配置页面
Then 显示该角色的权限矩阵（模块 → 操作 → 是否授权）
And 支持勾选/取消勾选权限
And 权限矩阵包含所有功能模块和操作类型
```

### AC3: 角色权限保存

```gherkin
Given Admin 用户修改了角色的权限配置
When 点击"保存权限配置"按钮
Then 验证权限配置的完整性
And 保存到 permission_matrix 表
And 记录操作日志到 audit_logs
And 该角色所有用户的权限立即同步更新
```

### AC4: 角色创建与编辑

```gherkin
Given Admin 用户需要管理角色
When 点击"新建角色"或"编辑角色"
Then 显示角色信息表单（角色名称、描述、状态）
And 支持保存或取消操作
And 角色名称必须唯一
```

### AC5: 角色删除

```gherkin
Given Admin 用户需要删除某个角色
When 点击角色的"删除"按钮
Then 显示确认对话框
And 确认后删除角色及其所有权限配置
And 记录删除操作到 audit_logs
And 该角色的所有用户自动失去权限
```

---

## Technical Requirements

### 角色管理数据模型

**角色表结构** (`roles` 表):

```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,  -- 角色名称：admin/manager/specialist/sales
    description TEXT,                 -- 角色描述
    status VARCHAR(20) DEFAULT 'active', -- 状态：active/inactive
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive'))
);

-- 索引优化
CREATE INDEX idx_roles_status ON roles(status);
```

**角色-权限关联表** (`role_permissions` 表 - 可选，可与 permission_matrix 合并):

```sql
-- 此表可以与 permission_matrix 表合并，使用 role 字段作为外键
-- 但为了清晰性，也可以单独创建
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    module VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL,
    granted BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(role_id, module, action)
);

-- 索引优化
CREATE INDEX idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_module ON role_permissions(module);
CREATE INDEX idx_role_permissions_role_module ON role_permissions(role_id, module);
```

### 后端技术栈要求

**必须遵循的技术规范** (来自 project-context.md):

- ✅ **Python 3.11+** async/await 用于所有 I/O 操作
- ✅ **SQLAlchemy 2.0+** 使用 async_session 和 select() 语法
- ✅ **Sanic** 异步请求处理，使用 Blueprints 组织路由
- ✅ **Pydantic** 用于请求/响应验证
- ✅ **类型注解** 所有函数必须有类型提示

**角色管理服务接口**:

```python
from typing import Dict, List, Optional
from app.models.roles import Role
from app.models.permission_matrix import PermissionMatrix

class RoleManagementService:
    async def get_all_roles(self) -> List[Dict]:
        """获取所有角色列表"""
        pass

    async def get_role_by_id(self, role_id: int) -> Optional[Dict]:
        """通过 ID 获取角色信息"""
        pass

    async def get_role_by_name(self, role_name: str) -> Optional[Dict]:
        """通过名称获取角色信息"""
        pass

    async def create_role(self, role_data: Dict) -> Dict:
        """创建新角色"""
        pass

    async def update_role(self, role_id: int, role_data: Dict) -> Dict:
        """更新角色信息"""
        pass

    async def delete_role(self, role_id: int) -> None:
        """删除角色"""
        pass

    async def get_role_permissions(self, role_id: int) -> Dict[str, Dict[str, bool]]:
        """获取角色的所有权限"""
        pass

    async def update_role_permissions(self, role_id: int, permissions: Dict) -> None:
        """更新角色的权限配置"""
        pass

    async def get_default_permissions(self, role_name: str) -> Dict:
        """获取角色的默认权限配置"""
        pass
```

---

## Dev Agent Guardrails

### Technical Requirements

**后端实现清单**:

- [ ] `backend/app/models/roles.py` - 角色模型 (新增)
- [ ] `backend/app/services/role_management_service.py` - 角色管理服务 (新增)
- [ ] `backend/app/routes/role_management_routes.py` - 角色管理路由 (新增)
- [ ] `backend/app/schemas/role_management.py` - 角色管理 Pydantic 模式 (新增)
- [ ] `backend/alembic/versions/008_create_roles_table.py` - 角色表数据库迁移 (新增)
- [ ] `backend/tests/test_role_management_service.py` - 角色管理服务测试 (新增)
- [ ] `backend/tests/test_role_management_routes.py` - 角色管理路由测试 (新增)

**前端实现清单**:

- [ ] `frontend/src/types/role-management.ts` - 类型定义 (新增)
- [ ] `frontend/src/api/role-management.ts` - API 客户端 (新增)
- [ ] `frontend/src/stores/role-management.ts` - Pinia Store (新增)
- [ ] `frontend/src/views/admin/role/RoleList.vue` - 角色列表页面 (新增)
- [ ] `frontend/src/views/admin/role/RoleConfig.vue` - 角色权限配置页面 (新增)
- [ ] `frontend/src/components/business/role/RoleForm.vue` - 角色表单组件 (新增)
- [ ] `frontend/src/components/business/role/RolePermissionEditor.vue` - 角色权限编辑组件 (新增)

### Architecture Compliance

**必须遵循的架构规则**:

1. **角色管理流程**:

   ```
   请求 → JWT 验证 → 功能权限检查 → 角色管理操作
   ```

2. **权限同步机制**:

   ```python
   # 当角色权限更新时，需要清除相关缓存
   from app.utils.permission_cache import clear_permission_cache

   class RoleManagementService:
       async def update_role_permissions(self, role_id: int, permissions: Dict) -> None:
           # 更新权限配置
           await self._update_db_permissions(role_id, permissions)

           # 清除该角色的权限缓存
           role = await self.get_role_by_id(role_id)
           clear_permission_cache(role['name'])

           # 记录操作日志
           await self._log_audit(
               action='update_role_permissions',
               role_id=role_id,
               details=permissions
           )
   ```

3. **角色管理 API 设计**:

   ```python
   # 获取角色列表
   GET /api/v1/roles → { "data": [...], "meta": {...} }

   # 获取角色详情
   GET /api/v1/roles/{id} → { "data": {...} }

   # 获取角色权限
   GET /api/v1/roles/{id}/permissions → { "data": {...} }

   # 创建角色
   POST /api/v1/roles → { "data": {...} }

   # 更新角色
   PUT /api/v1/roles/{id} → { "data": {...} }

   # 更新角色权限
   PUT /api/v1/roles/{id}/permissions → { "data": {...} }

   # 删除角色
   DELETE /api/v1/roles/{id} → { "data": null }
   ```

### Testing Requirements

**后端测试场景** (pytest):

```python
# test_role_management_service.py
import pytest
from app.services.role_management_service import RoleManagementService
from app.models.roles import Role

@pytest.mark.asyncio
async def test_get_all_roles():
    """获取所有角色列表"""
    service = RoleManagementService()
    roles = await service.get_all_roles()

    assert len(roles) >= 4  # 至少包含系统默认角色
    assert any(role['name'] == 'admin' for role in roles)
    assert any(role['name'] == 'manager' for role in roles)

@pytest.mark.asyncio
async def test_create_and_delete_role():
    """创建和删除角色"""
    service = RoleManagementService()

    # 创建测试角色
    new_role = await service.create_role({
        'name': 'test_role',
        'description': '测试角色',
        'status': 'active'
    })

    assert new_role['name'] == 'test_role'

    # 删除测试角色
    await service.delete_role(new_role['id'])

    # 验证角色已删除
    deleted_role = await service.get_role_by_name('test_role')
    assert deleted_role is None

@pytest.mark.asyncio
async def test_update_role_permissions():
    """更新角色权限"""
    service = RoleManagementService()

    # 获取测试角色（使用 sales 角色进行测试）
    sales_role = await service.get_role_by_name('sales')

    # 原始权限
    original_permissions = await service.get_role_permissions(sales_role['id'])

    # 更新权限
    await service.update_role_permissions(sales_role['id'], {
        'customer': {
            'read': True,
            'create': True,
            'update': True,
            'delete': False
        },
        'reporting': {
            'read': True,
            'create': False,
            'update': False,
            'delete': False
        }
    })

    # 验证更新后权限
    updated_permissions = await service.get_role_permissions(sales_role['id'])

    # 销售角色现在应该有客户模块的 create 权限
    assert updated_permissions['customer']['create'] is True
    # 销售角色现在应该有报表模块的 read 权限
    assert updated_permissions['reporting']['read'] is True
```

**前端测试场景** (Vitest):

```typescript
// role-management.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { useRoleManagementStore } from "@/stores/role-management";

describe("Role Management Store", () => {
  let store: ReturnType<typeof useRoleManagementStore>;

  beforeEach(() => {
    store = useRoleManagementStore();
    // 设置测试数据
    store.setRoles([
      { id: 1, name: "admin", description: "管理员角色", status: "active" },
      { id: 2, name: "manager", description: "经理角色", status: "active" },
    ]);
  });

  it("fetch roles list", async () => {
    await store.fetchRoles();
    expect(store.roles.length).toBeGreaterThan(0);
    expect(store.roles.some((role) => role.name === "admin")).toBe(true);
  });

  it("update role status", async () => {
    await store.updateRole(2, { status: "inactive" });
    const updatedRole = store.roles.find((role) => role.id === 2);
    expect(updatedRole?.status).toBe("inactive");
  });

  it("check role permissions", async () => {
    const adminRole = await store.getRolePermissions(1);
    expect(adminRole.customer.read).toBe(true);
    expect(adminRole.customer.create).toBe(true);
    expect(adminRole.customer.update).toBe(true);
    expect(adminRole.customer.delete).toBe(true);
  });
});
```

---

## Previous Story Intelligence

### 来自 Story 1.5 (功能权限)

**已实现功能**:

- ✅ 权限矩阵数据模型和表结构
- ✅ 权限矩阵服务和路由
- ✅ 功能权限中间件和缓存机制
- ✅ 前端权限矩阵配置页面
- ✅ 权限检查工具函数

**复用代码**:

```python
# 从 Story 1.5 复用权限矩阵相关代码
from app.models.permission_matrix import PermissionMatrix
from app.services.permission_matrix_service import PermissionMatrixService
from app.utils.permission_cache import clear_permission_cache

# 角色管理服务可以集成权限矩阵服务
class RoleManagementService:
    def __init__(self):
        self.permission_service = PermissionMatrixService()

    async def update_role_permissions(self, role_id: int, permissions: Dict):
        # 转换权限格式并更新权限矩阵
        await self.permission_service.bulk_update_permissions(
            role_name=await self._get_role_name(role_id),
            permissions=permissions
        )

        # 清除权限缓存
        clear_permission_cache(await self._get_role_name(role_id))
```

### 来自 Story 1.3 (权限管理)

**已实现功能**:

- ✅ 用户-角色关联（user.role 字段）
- ✅ 基础的权限验证机制
- ✅ 权限服务基础框架

**复用代码**:

```python
# 从 Story 1.3 复用用户-角色关联逻辑
from app.models.user import User

class RoleManagementService:
    async def get_users_by_role(self, role_id: int) -> List[Dict]:
        """获取拥有该角色的所有用户"""
        users = await self.session.execute(
            select(User)
            .where(User.role == await self._get_role_name(role_id))
        )
        return users.scalars().all()
```

---

## Git Intelligence Summary

**最近提交模式**:

```
3c6adaa feat(function-permission): Story 1.5 complete ✅
d4a7b23 fix(login): fix login functionality
920cb9a feat(data-permission): Story 1.4 complete ✅
```

**代码约定**:

- 提交信息：`feat({module}): description`
- 文件命名：snake_case (Python), PascalCase (Vue)
- 迁移文件：`{sequence}_{description}.py`
- 测试文件：`test_*.py`

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
    result = await session.execute(select(Role))
    roles = result.scalars().all()

# 类型注解 (必须)
from typing import Dict, List, Optional

async def get_role_permissions(role_id: int) -> Dict[str, Dict[str, bool]]:
    """获取角色的权限配置"""
    pass

# 标准错误响应格式
from sanic.exceptions import HTTPException

raise HTTPException(
    status_code=403,
    message="您没有权限执行此操作",
    context={
        "role_id": role_id,
        "action": "delete"
    }
)
```

**Critical Don't-Miss Rules**:

- ✅ ALL role management operations MUST require Admin role
- ✅ Role deletion MUST invalidate all user permissions for that role
- ✅ Use transaction for role and permissions updates
- ✅ Test role management operations in all API endpoints
- ✅ NEVER expose role management API to non-Admin users
- ✅ Admin role MUST have all permissions by default and cannot be modified/deleted

---

## Story Completion Status

**实现检查清单**:

- [x] **数据库迁移**
  - [x] 创建 roles 表迁移 `008_create_roles_table.py`
  - [x] 插入系统默认角色数据
  - [x] 运行迁移并验证 ✅ alembic upgrade head 成功

- [x] **后端实现**
  - [x] 创建 Role 模型 `models/roles.py`
  - [x] 创建 RoleManagementService 服务 `services/role_management_service.py`
  - [x] 创建角色管理路由 `routes/role_management_routes.py`
  - [x] 创建角色管理 Pydantic 模式 `schemas/role_management.py`
  - [x] 编写角色管理服务测试（ATDD 阶段已生成）
  - [x] 编写角色管理路由测试（ATDD 阶段已生成）

- [x] **前端实现**
  - [x] 创建类型定义 `types/role-management.ts`
  - [x] 创建 API 客户端 `api/role-management.ts`
  - [x] 创建角色管理 Store `stores/role-management.ts`
  - [x] 创建角色列表页面 `views/admin/role/RoleList.vue`
  - [x] 创建角色权限配置页面 `views/admin/role/RoleConfig.vue`
  - [x] 创建角色表单组件 `components/business/role/RoleForm.vue`
  - [x] 创建角色权限编辑组件 `components/business/role/RolePermissionEditor.vue`
  - [x] 路由配置 `router/index.ts`

- [ ] **代码审查**
  - [ ] 审查后端实现
  - [ ] 审查前端实现
  - [ ] 审查测试覆盖
  - [ ] 修复所有审查问题

- [ ] **测试验证**
  - [ ] 运行角色管理服务测试
  - [ ] 运行角色管理路由测试
  - [ ] 运行前端测试
  - [ ] 运行 E2E 测试

- [ ] **文档更新**
  - [ ] 更新 API 文档说明角色管理行为
  - [ ] 更新部署清单

---

### Dev Agent Record

### Debug Log References

- Sprint status 分析：`_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics 需求来源：`_bmad-output/planning-artifacts/epics.md` (Story 1.6: 角色管理)
- 架构模式来源：`_bmad-output/planning-artifacts/architecture.md` (RBAC 架构)
- 前序故事：`_bmad-output/implementation-artifacts/stories/1-5-function-permission.md`
- 前序故事：`_bmad-output/implementation-artifacts/stories/1-3-permission-management.md`

### Completion Notes List

- ✅ 角色管理功能基于 epics.md 中的 FR38 要求
- ✅ 使用 roles 表存储角色信息，与 permission_matrix 表关联
- ✅ 支持角色的创建、编辑、删除和权限配置
- ✅ 权限配置后自动清除缓存，确保权限立即生效
- ✅ 前端页面支持角色列表和权限配置
- ✅ 完整的测试场景覆盖（ATDD 阶段已生成）
- ✅ 前后端实现清单详细列出
- ✅ 数据库迁移成功执行（alembic upgrade head → 008）
- ✅ 后端服务加载成功测试通过
- ✅ 路由配置完成（/admin/role 和 /admin/role/:id/config）

**实现文件清单** (14 个文件):

- 后端 (6): 008_create_roles_table.py, roles.py, role_management_service.py, role_management.py (schema), role_management_routes.py, main.py (更新)
- 前端 (8): role-management.ts (types), role-management.ts (api), role-management.ts (store), RoleList.vue, RoleConfig.vue, RoleForm.vue, RolePermissionEditor.vue, router/index.ts (更新)

**Sprint 状态更新**:

- Story 1.6 状态：`backlog` → `ready-for-dev` → `in-progress` → `review`
