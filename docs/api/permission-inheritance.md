# 权限继承 API 文档

**Story**: 1.7-permission-inheritance  
**版本**: v1  
**最后更新**: 2026-03-01

---

## 📚 概述

权限继承功能允许高级角色自动继承低级角色的所有权限，同时支持额外授权机制。

**核心功能**:

- 角色层级结构查询（Admin > Manager > Specialist > Sales）
- 权限继承查询（自动包含下级角色权限）
- 权限检查（支持继承和额外授权）
- 额外授权管理（添加/撤销/查询）

---

## 🔑 认证要求

所有 API 端点需要 JWT 认证：

```http
Authorization: Bearer {your_jwt_token}
```

---

## 📖 API 端点

### 1. 获取角色层级结构

**端点**: `GET /api/v1/roles/hierarchy`

**权限**: Admin, Manager

**描述**: 获取完整的角色层级结构，包含每个角色的继承关系。

**响应示例**:

```json
{
  "success": true,
  "data": {
    "levels": [
      {
        "level": 4,
        "role": "admin",
        "name": "Admin",
        "inherits": ["manager", "specialist", "sales"]
      },
      {
        "level": 3,
        "role": "manager",
        "name": "Manager",
        "inherits": ["specialist", "sales"]
      },
      {
        "level": 2,
        "role": "specialist",
        "name": "Specialist",
        "inherits": ["sales"]
      },
      {
        "level": 1,
        "role": "sales",
        "name": "Sales",
        "inherits": []
      }
    ]
  },
  "meta": {
    "timestamp": "2026-03-01T12:00:00Z",
    "roles_count": 4
  }
}
```

**cURL 示例**:

```bash
curl -X GET http://localhost:8000/api/v1/roles/hierarchy \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. 获取角色权限（包含继承）

**端点**: `GET /api/v1/roles/{role_name}/permissions`

**权限**: Admin, Manager

**描述**: 获取指定角色的所有权限，包含直接权限和继承权限。

**路径参数**:

- `role_name` (string): 角色名称（admin, manager, specialist, sales）

**响应示例**:

```json
{
  "success": true,
  "data": {
    "role": "manager",
    "level": 3,
    "inherited_from": ["specialist", "sales"],
    "inherited_permissions": [
      {
        "resource": "customer",
        "action": "read",
        "inherited_from": "specialist"
      },
      {
        "resource": "customer",
        "action": "update",
        "inherited_from": "specialist"
      }
    ],
    "direct_permissions": [
      {
        "resource": "report",
        "action": "create"
      }
    ],
    "all_permissions": [
      { "resource": "customer", "action": "read" },
      { "resource": "customer", "action": "update" },
      { "resource": "report", "action": "create" }
    ]
  },
  "meta": {
    "timestamp": "2026-03-01T12:00:00Z"
  }
}
```

**cURL 示例**:

```bash
curl -X GET http://localhost:8000/api/v1/roles/manager/permissions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. 检查权限

**端点**: `POST /api/v1/permissions/check`

**权限**: 所有认证用户

**描述**: 检查指定角色是否有权限执行特定操作（支持继承和额外授权）。

**请求体**:

```json
{
  "role": "manager",
  "resource": "customer",
  "action": "delete"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "has_permission": true,
    "source": "inherited",
    "inherited_from": "specialist",
    "message": "Permission granted"
  },
  "meta": {
    "timestamp": "2026-03-01T12:00:00Z",
    "role": "manager",
    "resource": "customer",
    "action": "delete"
  }
}
```

**权限来源说明**:

- `admin`: Admin 角色拥有所有权限
- `direct`: 直接授予的权限
- `inherited`: 从下级角色继承的权限
- `none`: 无权限

**cURL 示例**:

```bash
curl -X POST http://localhost:8000/api/v1/permissions/check \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"manager","resource":"customer","action":"delete"}'
```

---

### 4. 清除权限缓存

**端点**: `POST /api/v1/permissions/cache/clear`

**权限**: Admin

**描述**: 清除所有权限缓存，强制重新计算。

**响应示例**:

```json
{
  "success": true,
  "message": "Permission cache cleared successfully"
}
```

**cURL 示例**:

```bash
curl -X POST http://localhost:8000/api/v1/permissions/cache/clear \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. 添加额外授权 ⭐

**端点**: `POST /api/v1/roles/{role_name}/grant-additional`

**权限**: Admin

**描述**: 为角色添加额外授权（允许高级角色拥有低级角色没有的权限）。

**路径参数**:

- `role_name` (string): 角色名称

**请求体**:

```json
{
  "resource": "role",
  "action": "delete"
}
```

**响应示例**:

```json
{
  "success": true,
  "message": "Additional permission granted: delete on role for role manager",
  "permission_id": 123
}
```

**错误响应**:

```json
{
  "success": false,
  "message": "Missing required fields: resource, action"
}
```

**cURL 示例**:

```bash
curl -X POST http://localhost:8000/api/v1/roles/manager/grant-additional \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resource":"role","action":"delete"}'
```

---

### 6. 获取额外授权列表 ⭐

**端点**: `GET /api/v1/roles/{role_name}/additional-permissions`

**权限**: Admin, Manager

**描述**: 获取角色的所有额外授权。

**路径参数**:

- `role_name` (string): 角色名称

**响应示例**:

```json
{
  "success": true,
  "role": "manager",
  "additional_permissions": [
    {
      "resource": "role",
      "action": "delete",
      "id": 123
    }
  ],
  "count": 1
}
```

**cURL 示例**:

```bash
curl -X GET http://localhost:8000/api/v1/roles/manager/additional-permissions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 7. 撤销额外授权 ⭐

**端点**: `DELETE /api/v1/roles/{role_name}/revoke-additional`

**权限**: Admin

**描述**: 撤销角色的额外授权。

**路径参数**:

- `role_name` (string): 角色名称

**查询参数**:

- `resource` (string): 资源名称
- `action` (string): 操作类型

**响应示例**:

```json
{
  "success": true,
  "message": "Additional permission revoked: delete on role for role manager"
}
```

**错误响应**:

```json
{
  "success": false,
  "message": "Additional permission not found"
}
```

**cURL 示例**:

```bash
curl -X DELETE "http://localhost:8000/api/v1/roles/manager/revoke-additional?resource=role&action=delete" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 使用示例

### 场景 1: 查询经理角色的完整权限

```bash
# 1. 获取角色层级
curl -X GET http://localhost:8000/api/v1/roles/hierarchy \
  -H "Authorization: Bearer TOKEN"

# 2. 获取经理的权限（包含继承）
curl -X GET http://localhost:8000/api/v1/roles/manager/permissions \
  -H "Authorization: Bearer TOKEN"

# 3. 检查经理是否有删除客户的权限
curl -X POST http://localhost:8000/api/v1/permissions/check \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"manager","resource":"customer","action":"delete"}'
```

### 场景 2: 为经理角色添加额外授权

```bash
# 1. 为经理添加删除角色的额外授权
curl -X POST http://localhost:8000/api/v1/roles/manager/grant-additional \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"resource":"role","action":"delete"}'

# 2. 验证额外授权已添加
curl -X GET http://localhost:8000/api/v1/roles/manager/additional-permissions \
  -H "Authorization: Bearer TOKEN"

# 3. 检查经理是否有删除角色的权限
curl -X POST http://localhost:8000/api/v1/permissions/check \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"manager","resource":"role","action":"delete"}'

# 4. 撤销额外授权
curl -X DELETE "http://localhost:8000/api/v1/roles/manager/revoke-additional?resource=role&action=delete" \
  -H "Authorization: Bearer TOKEN"
```

---

## ⚠️ 错误处理

### 常见错误码

| 错误码                    | 说明                | 解决方案               |
| ------------------------- | ------------------- | ---------------------- |
| 401 Unauthorized          | 未认证或 Token 过期 | 重新登录获取新 Token   |
| 403 Forbidden             | 无权限访问该端点    | 使用更高权限的角色     |
| 404 Not Found             | 资源不存在          | 检查角色名称或路径参数 |
| 400 Bad Request           | 请求参数错误        | 检查请求体格式         |
| 500 Internal Server Error | 服务器错误          | 查看服务器日志         |

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "资源不存在",
    "details": [
      {
        "field": "role_name",
        "message": "角色 'invalid_role' 不存在"
      }
    ]
  }
}
```

---

## 📊 性能优化

### 缓存机制

- **内存缓存**: 权限检查结果会被缓存
- **缓存键**: `{role}_{resource}_{action}`
- **缓存失效**:
  - 手动调用 `/permissions/cache/clear`
  - 角色权限变更时自动失效

### 最佳实践

1. **批量查询**: 使用 `/roles/{role}/permissions` 代替多次单独查询
2. **缓存利用**: 相同权限检查会被自动缓存
3. **定期清理**: 权限配置变更后调用清除缓存

---

## 🧪 测试

### 运行测试

```bash
# 单元测试
python -m pytest tests/unit/test_permission_inheritance.py -v

# API 测试
npx playwright test tests/api/permission-inheritance.spec.ts --project=api
```

### 测试覆盖

- ✅ 角色层级查询
- ✅ 权限继承逻辑
- ✅ 额外授权管理（添加/撤销/查询）
- ✅ 缓存机制
- ✅ 边界条件（销售无继承，Admin 继承所有）

---

## 📝 更新日志

### v1.0.0 (2026-03-01)

- ✨ 初始版本
- ✨ 7 个 API 端点
- ✨ 权限继承机制
- ✨ 额外授权管理
- ✨ 缓存优化

---

**维护者**: ark-code-latest  
**文档版本**: 1.0.0  
**最后更新**: 2026-03-01
