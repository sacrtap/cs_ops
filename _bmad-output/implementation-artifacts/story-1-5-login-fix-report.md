# Story 1.5 功能权限 - 登录功能修复报告

**修复日期**: 2026-03-01  
**修复状态**: ✅ **完成**

---

## 🔧 问题诊断与修复

### **问题 1: bcrypt 与 passlib 不兼容**

**症状**:

```
ValueError: password cannot be longer than 72 bytes
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**原因**: passlib 1.7.4 不支持 bcrypt 5.0.0

**解决方案**:

1. 移除 passlib 依赖
2. 直接使用 bcrypt 库

**修复文件**: `backend/app/utils/password.py`

```python
# 修复前（使用 passlib）:
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])

# 修复后（直接使用 bcrypt）:
import bcrypt
def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

---

### **问题 2: UserResponse schema 类型错误**

**症状**:

```
ValidationError: user.role - Field required [type=missing]
user.role value: <UserRole.ADMIN: 'admin'> (expected str)
```

**原因**: UserResponse 的 role/status 字段使用枚举类型，但 user.to_dict() 返回字符串

**解决方案**: 修改 schema 定义

**修复文件**: `backend/app/schemas/auth.py`

```python
# 修复前:
role: UserRole
status: UserStatus

# 修复后:
role: str  # UserRole 枚举值
status: str  # UserStatus 枚举值
```

---

### **问题 3: datetime JSON 序列化失败**

**症状**:

```
TypeError: datetime.datetime(2026, 3, 1, 14, 48, 58) is not JSON serializable
```

**原因**: Pydantic model_dump() 返回的 datetime 对象无法被 Sanic json() 序列化

**解决方案**: 使用 model_dump(mode='json')

**修复文件**: `backend/app/routes/auth_routes.py`

```python
# 修复前:
return json({"data": response_data.model_dump()})

# 修复后:
return json({"data": response_data.model_dump(mode='json')})
```

---

### **问题 4: 请求上下文数据库会话**

**症状**: 500 错误，无详细日志

**原因**: request.ctx.db 未正确设置

**解决方案**: 在 main.py 的 on_request 处理器中创建数据库会话

**修复文件**: `backend/app/main.py`

```python
@app.on_request
async def before_request(request):
    from app.database import async_session_maker
    request.ctx.db = async_session_maker()

@app.on_response
async def after_response(request, response):
    if hasattr(request.ctx, 'db'):
        await request.ctx.db.close()
```

---

## ✅ 验证结果

### **登录测试**

| 用户    | 密码       | 角色    | 状态    |
| ------- | ---------- | ------- | ------- |
| admin   | admin123   | admin   | ✅ 成功 |
| manager | manager123 | manager | ✅ 成功 |
| sales   | sales123   | sales   | ✅ 成功 |

### **API 响应**

```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 7200,
    "user": {
      "id": 4,
      "username": "admin",
      "real_name": "系统管理员",
      "role": "admin",
      "email": "admin@example.com",
      "phone": null,
      "status": "active",
      "created_at": "2026-03-01T14:43:33.050657"
    }
  }
}
```

✅ 响应格式正确
✅ 所有字段序列化正常
✅ datetime 转换为 ISO 字符串

---

## 📊 修复统计

| 修复项              | 文件修改            | 状态 |
| ------------------- | ------------------- | ---- |
| bcrypt 兼容性       | 1 (password.py)     | ✅   |
| UserResponse schema | 1 (auth.py)         | ✅   |
| datetime 序列化     | 1 (auth_routes.py)  | ✅   |
| 数据库会话管理      | 1 (main.py)         | ✅   |
| 重新创建用户        | 脚本执行            | ✅   |
| **总计**            | **4 文件 + 1 脚本** | ✅   |

---

## 🎯 后续工作

1. ✅ 后端登录功能 - 已修复
2. ⏳ 前端 TypeScript LSP 错误 - 待修复
3. ⏳ E2E 测试 - 待执行（依赖登录功能）

---

**修复完成时间**: 2026-03-01 14:49  
**后端服务状态**: ✅ 运行中 (port 8000)  
**登录功能**: ✅ 正常工作
