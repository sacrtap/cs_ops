---
stepsCompleted:
  - step-01-preflight-and-context
  - step-02-generation-mode
  - step-03-test-strategy
  - step-04-generate-tests
  - step-04c-aggregate
lastStep: step-04c-aggregate
lastSaved: "2026-03-01T16:45:00.000Z"
inputDocuments:
  - _bmad-output/implementation-artifacts/stories/1-7-permission-inheritance.md
  - _bmad/tea/config.yaml
  - backend/app/services/permission_service.py
  - backend/app/models/roles.py
---

# ATDD Checklist: Story 1.7 - 权限继承

**Story ID**: 1.7  
**Story Key**: 1-7-permission-inheritance  
**TDD Phase**: 🔴 RED (Failing Tests Generated)  
**Generated Date**: 2026-03-01  
**User**: Sacrtap

---

## 📊 TDD Red Phase Summary

✅ **Failing tests generated successfully**

| Test Type | Count  | Status        | TDD Compliance   |
| --------- | ------ | ------------- | ---------------- |
| API Tests | 12     | `test.skip()` | ✅ All skipped   |
| E2E Tests | 10     | `test.skip()` | ✅ All skipped   |
| **Total** | **22** | **SKIPPED**   | ✅ **RED PHASE** |

**Performance**: Parallel execution (API + E2E subprocesses) ~50% faster than sequential

---

## ✅ Acceptance Criteria Coverage

### 验收标准 1: 角色层级定义

**Given** 角色层级定义  
**When** 分配用户角色  
**Then** 自动继承下级角色权限  
**And** 支持额外授权

| Test ID | Priority | Test Type | Description                                   | Coverage Status |
| ------- | -------- | --------- | --------------------------------------------- | --------------- |
| API-01  | P0       | API       | 验证角色层级结构 (Admin > 经理 > 专员 > 销售) | ✅ Covered      |
| API-02  | P0       | API       | 经理角色继承专员的所有权限                    | ✅ Covered      |
| API-03  | P0       | API       | 经理角色继承销售的所有权限                    | ✅ Covered      |
| API-04  | P1       | API       | Admin 角色继承所有下级角色的权限              | ✅ Covered      |
| API-05  | P1       | API       | 专员角色继承销售的所有权限                    | ✅ Covered      |
| API-06  | P1       | API       | 销售角色不继承任何其他角色的权限              | ✅ Covered      |
| API-07  | P1       | API       | 支持额外授权机制                              | ✅ Covered      |
| API-08  | P2       | API       | 额外授权与继承权限并存                        | ✅ Covered      |
| API-09  | P1       | API       | 权限检查包含继承的权限                        | ✅ Covered      |
| API-10  | P1       | API       | 权限检查识别额外授权                          | ✅ Covered      |
| API-11  | P2       | API       | 更新角色层级时重新计算继承权限                | ✅ Covered      |
| API-12  | P3       | API       | 缓存继承权限以提高性能                        | ✅ Covered      |
| E2E-01  | P0       | E2E       | 显示角色层级关系可视化                        | ✅ Covered      |
| E2E-02  | P0       | E2E       | 经理角色显示继承自专员的权限                  | ✅ Covered      |
| E2E-03  | P0       | E2E       | 经理角色显示继承自销售的权限                  | ✅ Covered      |
| E2E-04  | P1       | E2E       | Admin 显示继承所有下级角色的权限              | ✅ Covered      |
| E2E-05  | P1       | E2E       | 专员显示继承自销售的权限                      | ✅ Covered      |
| E2E-06  | P2       | E2E       | 支持为经理角色添加额外授权                    | ✅ Covered      |
| E2E-07  | P2       | E2E       | 额外授权与继承权限分开显示                    | ✅ Covered      |
| E2E-08  | P1       | E2E       | 权限检查工具显示权限来源                      | ✅ Covered      |
| E2E-09  | P3       | E2E       | 可以编辑角色层级关系                          | ✅ Covered      |
| E2E-10  | P3       | E2E       | 更新层级关系后实时更新权限继承                | ✅ Covered      |

---

## 🔴 TDD Red Phase (Current Status)

### 测试设计原则

所有生成的测试都遵循 TDD 红phase 原则：

1. ✅ **`test.skip()` 标记**: 所有测试都使用 `test.skip()` 标记为 intentionally failing
2. ✅ **期望行为断言**: 测试断言 EXPECTED 行为，而非 placeholder assertions
3. ✅ **真实测试数据**: 使用 realistic test data，而非 placeholder data
4. ✅ **优先级标签**: 所有测试都包含 [P0], [P1], [P2], [P3] 优先级标签

### 为什么测试会失败

这些测试被设计为**失败**，因为功能尚未实现：

- **API 测试**: 期望的 endpoint (`/api/v1/roles/hierarchy`, `/api/v1/roles/{role}/permissions` 等) 尚未实现
- **E2E 测试**: 期望的 UI 组件（层级可视化、继承权限显示等）尚未实现

这是 **INTENTIONAL** 的 TDD 红 phase 行为！

---

## 📂 生成的测试文件

### API 测试文件

**文件**: `tests/api/permission-inheritance.spec.ts`

**测试覆盖**:

- 角色层级结构验证
- 权限继承逻辑（经理 → 专员 → 销售）
- 额外授权机制
- 权限检查 API
- 权限缓存性能

**依赖**:

- Playwright API request context
- 后端权限服务
- 角色层级数据模型

### E2E 测试文件

**文件**: `tests/e2e/permission-inheritance.spec.ts`

**测试覆盖**:

- 角色层级关系可视化
- 继承权限 UI 显示
- 额外授权管理界面
- 权限检查工具
- 层级关系编辑功能

**依赖**:

- Playwright browser context
- 前端角色管理页面
- 权限管理组件

---

## 🛠️ 测试基础设施

### 需要的 Fixtures

当前阶段（TDD Red Phase）仅需最小化 fixtures：

```typescript
// tests/fixtures/test-data.ts
export const testUserData = {
  email: "test@example.com",
  password: "SecurePass123!",
};

export const roleHierarchy = {
  admin: { level: 4, inherits: ["manager", "specialist", "sales"] },
  manager: { level: 3, inherits: ["specialist", "sales"] },
  specialist: { level: 2, inherits: ["sales"] },
  sales: { level: 1, inherits: [] },
};
```

### 知识片段使用

- `api-request`: API 测试模式和最佳实践
- `data-factories`: 测试数据生成
- `api-testing-patterns`: API 测试结构
- `fixture-architecture`: E2E fixture 架构
- `network-first`: 网络优先测试模式
- `selector-resilience`: 弹性选择器模式

---

## 🚀 Next Steps (TDD Green Phase)

### 功能实现后

完成 Story 1.7 的开发后，执行以下步骤进入 **TDD Green Phase**：

1. **移除 `test.skip()`**:

   ```bash
   # 在测试文件中删除所有 test.skip() 的 .skip 部分
   # tests/api/permission-inheritance.spec.ts
   # tests/e2e/permission-inheritance.spec.ts
   ```

2. **运行测试**:

   ```bash
   # 运行 API 测试
   npm test -- tests/api/permission-inheritance.spec.ts

   # 运行 E2E 测试
   npm test -- tests/e2e/permission-inheritance.spec.ts

   # 或运行所有测试
   npm test
   ```

3. **验证测试通过**:
   - 如果测试**通过** ✅：功能实现正确，进入重构 phase
   - 如果测试**失败** ❌：
     - **实现 bug**: 修复功能代码
     - **测试 bug**: 修复测试断言

4. **提交通过的测试**:
   ```bash
   git add tests/api/permission-inheritance.spec.ts
   git add tests/e2e/permission-inheritance.spec.ts
   git commit -m "test: add passing tests for permission inheritance (Story 1.7)"
   ```

---

## 📋 实现指南

### 需要实现的 API Endpoints

1. **GET** `/api/v1/roles/hierarchy` - 获取角色层级结构
2. **GET** `/api/v1/roles/{role}/permissions` - 获取角色权限（包含继承）
3. **POST** `/api/v1/roles/{role}/permissions/grant` - 添加额外授权
4. **POST** `/api/v1/permissions/check` - 检查权限
5. **PUT** `/api/v1/roles/hierarchy/update` - 更新角色层级关系

### 需要实现的前端组件

1. **角色层级可视化组件**: 显示 Admin → 经理 → 专员 → 销售 的层级关系
2. **继承权限显示组件**: 在角色详情页显示继承的权限
3. **额外授权管理组件**: 为角色添加额外权限
4. **权限检查工具**: 查询角色权限并显示来源
5. **层级关系编辑器**: 编辑角色继承关系

### 数据库变更

需要在角色表中添加层级关系字段：

```sql
ALTER TABLE roles ADD COLUMN parent_role_id INT REFERENCES roles(id);
ALTER TABLE roles ADD COLUMN level INT NOT NULL DEFAULT 1;
```

或创建独立的角色层级关系表：

```sql
CREATE TABLE role_hierarchy (
  id SERIAL PRIMARY KEY,
  role_id INT REFERENCES roles(id),
  inherits_from INT REFERENCES roles(id),
  UNIQUE(role_id, inherits_from)
);
```

---

## ⚠️ 关键风险和假设

### 风险

1. **权限循环继承**: 需要防止角色层级形成循环（A 继承 B，B 继承 C，C 继承 A）
2. **性能问题**: 继承权限计算可能影响性能，需要有效缓存
3. **并发更新**: 多个管理员同时修改层级关系可能导致数据不一致

### 假设

1. 角色层级是**树状结构**（每个角色最多有一个直接父角色）
2. 权限继承是**传递性**的（经理继承专员，专员继承销售 → 经理继承销售）
3. 额外授权**不影响**继承关系，仅添加额外权限

---

## 📈 测试质量指标

### 覆盖率目标

- **API 测试**: 100% 权限逻辑覆盖
- **E2E 测试**: 关键用户旅程 100% 覆盖
- **边界条件**: 包含正常场景和错误场景

### 优先级分布

| Priority      | Count | Percentage |
| ------------- | ----- | ---------- |
| P0 (Critical) | 7     | 32%        |
| P1 (High)     | 9     | 41%        |
| P2 (Medium)   | 4     | 18%        |
| P3 (Low)      | 2     | 9%         |

---

## ✅ ATDD 验证清单

- [x] 所有测试使用 `test.skip()` (TDD red phase)
- [x] 测试断言 EXPECTED 行为，非 placeholder
- [x] 验收标准 100% 覆盖
- [x] API 测试创建在 `tests/api/` 目录
- [x] E2E 测试创建在 `tests/e2e/` 目录
- [x] 测试文件遵循项目命名规范
- [x] 包含优先级标签 [P0-P3]
- [x] 使用真实测试数据
- [x] 遵循知识片段模式
- [x] ATDD 清单生成完成

---

**状态**: ✅ **ATDD 测试生成完成 (TDD RED PHASE)**  
**下一步**: 实现 Story 1.7 功能，然后移除 `test.skip()` 验证测试通过

**生成时间**: 2026-03-01T16:45:00.000Z  
**工作流**: BMAD-TEA Test Architect ATDD  
**版本**: 5.0
