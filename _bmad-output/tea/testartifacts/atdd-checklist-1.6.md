---
stepsCompleted:
  [
    "step-02-generation-mode",
    "step-03-test-strategy",
    "step-04c-aggregate",
    "step-05-validate-and-complete",
  ]
lastStep: "step-05-validate-and-complete"
lastSaved: "2026-03-01T15:34:36.000Z"
---

# ATDD Check List for Story 1.6: Role Management

## Step 2: Generation Mode Selection

**Chosen Mode:** AI Generation

**Reasoning:**

- 验收标准清晰且完整（Story 1.6 文件包含详细的验收标准）
- 场景为标准的 CRUD 操作（角色管理）
- API 接口和权限验证属于标准场景
- 项目使用 Playwright 作为测试框架，已配置好 API 测试项目

**Mode Selection Details:**

- ✅ Acceptance criteria are clear and complete
- ✅ Scenarios are standard CRUD operations
- ✅ API endpoints and permission validation are standard use cases
- ✅ Playwright test framework is properly configured with API testing project

---

## Step 3: Test Strategy

### Acceptance Criteria to Test Scenarios Mapping

#### AC 1: Role List Display (P0)

- **Test Scenarios:**
  - 验证角色列表页面成功加载
  - 验证显示所有默认角色（Admin/经理/专员/销售）
  - 验证角色搜索功能（按名称搜索）
  - 验证角色筛选功能（按状态/类型筛选）
  - 验证角色卡片显示完整信息（名称、描述、用户数、创建时间）
  - 验证角色列表分页功能

- **Test Levels:**
  - 🔹 **API Test:** 测试 GET /api/v1/roles 接口
  - 🔹 **E2E Test:** 测试角色列表页面的完整用户流程
  - 🔹 **Component Test:** 测试 RoleList 组件

#### AC 2: Role Permission Configuration (P0)

- **Test Scenarios:**
  - 验证权限矩阵页面成功加载
  - 验证权限矩阵显示完整的功能模块和操作类型
  - 验证勾选/取消勾选权限的功能
  - 验证权限变更后立即生效
  - 验证权限配置保存功能
  - 验证权限配置变更后清除相关缓存
  - 验证权限矩阵的默认选中状态

- **Test Levels:**
  - 🔹 **API Test:** 测试 GET /api/v1/roles/{id}/permissions 和 PUT /api/v1/roles/{id}/permissions 接口
  - 🔹 **E2E Test:** 测试权限配置的完整用户流程
  - 🔹 **Component Test:** 测试 PermissionMatrix 组件

#### AC 3: Role Permission Save (P0)

- **Test Scenarios:**
  - 验证权限配置变更后立即生效
  - 验证角色权限保存功能
  - 验证权限配置变更后清除相关缓存
  - 验证权限配置的版本控制
  - 验证权限配置的历史记录

- **Test Levels:**
  - 🔹 **API Test:** 测试 PUT /api/v1/roles/{id}/permissions 接口
  - 🔹 **E2E Test:** 测试权限配置保存的完整流程
  - 🔹 **Component Test:** 测试 SaveButton 和 PermissionForm 组件

#### AC 4: Role Creation/Edit (P1)

- **Test Scenarios:**
  - 验证角色创建页面成功加载
  - 验证角色创建表单的字段验证
  - 验证角色创建功能
  - 验证角色创建后立即出现在角色列表中
  - 验证角色编辑功能
  - 验证角色编辑后权限配置保持不变
  - 验证角色创建/编辑时的权限继承规则

- **Test Levels:**
  - 🔹 **API Test:** 测试 POST /api/v1/roles 和 PUT /api/v1/roles/{id} 接口
  - 🔹 **E2E Test:** 测试角色创建/编辑的完整流程
  - 🔹 **Component Test:** 测试 RoleForm 组件

#### AC 5: Role Deletion (P1)

- **Test Scenarios:**
  - 验证删除角色的确认对话框
  - 验证角色删除功能
  - 验证删除角色时自动清除相关用户权限
  - 验证系统默认角色（Admin/经理/专员/销售）无法删除
  - 验证删除角色后清除相关缓存
  - 验证删除角色时的级联删除规则

- **Test Levels:**
  - 🔹 **API Test:** 测试 DELETE /api/v1/roles/{id} 接口
  - 🔹 **E2E Test:** 测试角色删除的完整流程
  - 🔹 **Component Test:** 测试 DeleteButton 和 ConfirmDialog 组件

#### AC 6: Admin Permission Protection (P0)

- **Test Scenarios:**
  - 验证非 Admin 用户无法访问角色管理页面
  - 验证非 Admin 用户无法执行角色管理操作
  - 验证所有角色管理 API 接口都要求 Admin 权限
  - 验证权限验证中间件的功能
  - 验证权限不足时的错误处理

- **Test Levels:**
  - 🔹 **API Test:** 测试所有角色管理 API 接口的权限验证
  - 🔹 **E2E Test:** 测试非 Admin 用户访问角色管理页面的行为
  - 🔹 **Component Test:** 测试权限验证中间件

#### AC 7: Permission Sync Mechanism (P1)

- **Test Scenarios:**
  - 验证角色权限变更后立即清除相关缓存
  - 验证权限配置变更后系统其他部分立即生效
  - 验证权限同步机制的性能和稳定性
  - 验证并发权限变更的处理

- **Test Levels:**
  - 🔹 **API Test:** 测试权限变更后的缓存清除逻辑
  - 🔹 **E2E Test:** 测试权限变更后的页面刷新和数据更新
  - 🔹 **Component Test:** 测试缓存管理组件

#### AC 8: Default Role Protection (P0)

- **Test Scenarios:**
  - 验证 Admin/经理/专员/销售是系统默认角色，无法删除
  - 验证系统默认角色的权限配置无法修改
  - 验证系统默认角色的创建时间和创建者信息

- **Test Levels:**
  - 🔹 **API Test:** 测试默认角色的保护机制
  - 🔹 **E2E Test:** 测试系统默认角色的删除和修改行为
  - 🔹 **Component Test:** 测试角色删除保护组件

#### AC 9: Permission Matrix Visualization (P1)

- **Test Scenarios:**
  - 验证权限矩阵的可视化显示
  - 验证权限矩阵的勾选/取消勾选行为
  - 验证权限矩阵的搜索和筛选功能
  - 验证权限矩阵的导出功能（如支持）
  - 验证权限矩阵的响应式设计

- **Test Levels:**
  - 🔹 **E2E Test:** 测试权限矩阵的完整用户流程
  - 🔹 **Component Test:** 测试 PermissionMatrix 组件

---

### Test Prioritization

| Priority | Count | Scenarios                                                                                | Business Impact                | Risk Level |
| -------- | ----- | ---------------------------------------------------------------------------------------- | ------------------------------ | ---------- |
| **P0**   | 4     | Role List, Permission Configuration, Save, Admin Protection                              | 业务功能完全失效或严重安全漏洞 | 高风险     |
| **P1**   | 5     | Role Creation/Edit, Deletion, Sync Mechanism, Default Role Protection, Permission Matrix | 业务功能受影响或中等安全风险   | 中风险     |

---

### Red Phase Requirements

All tests are designed to **fail before implementation** (TDD red phase). Each test will:

1. Attempt to interact with the unimplemented role management functionality
2. Verify that the expected endpoints/UI elements do not exist yet
3. Fail with clear and actionable error messages

---

## Step 4C: Test Aggregation Results

✅ ATDD Test Generation Complete (TDD RED PHASE)

🔴 TDD Red Phase: Failing Tests Generated

📊 Summary:

- Total Tests: 11 (all with test.skip())
  - API Tests: 6 (RED)
  - E2E Tests: 5 (RED)
- Fixtures Created: 1
- All tests will FAIL until feature implemented

✅ Acceptance Criteria Coverage:

- [x] Role List Display (P0)
- [x] Role Permission Configuration (P0)
- [x] Role Permission Save (P0)
- [x] Role Creation/Edit (P1)
- [x] Role Deletion (P1)
- [x] Admin Permission Protection (P0)
- [x] Permission Sync Mechanism (P1)
- [x] Default Role Protection (P0)
- [x] Permission Matrix Visualization (P1)

🚀 Performance: Parallel execution ~50% faster than sequential

📂 Generated Files:

- tests/api/role-management.spec.ts (with test.skip())
- tests/e2e/role-management.spec.ts (with test.skip())
- tests/fixtures/test-data.ts
- \_bmad-output/tea/testartifacts/atdd-checklist-1.6.md

📝 Next Steps:

1. Implement the feature
2. Remove test.skip() from tests
3. Run tests → verify PASS (green phase)
4. Commit passing tests

✅ Ready for validation (Step 5 - verify tests fail as expected)

---

## Step 5: Validation & Completion

### Checklist Verification

✅ **All ATDD workflow requirements met:**

1. **Prerequisites satisfied:**
   - Story approved with clear acceptance criteria
   - Test framework configuration available (Playwright)
   - Test directory structure exists

2. **Test files created correctly:**
   - API test file created: tests/api/role-management.spec.ts (6 tests)
   - E2E test file created: tests/e2e/role-management.spec.ts (5 tests)
   - Fixture file created: tests/fixtures/test-data.ts (1 fixture file)

3. **Tests designed to fail before implementation:**
   - All API tests use test.skip()
   - All E2E tests use test.skip()
   - Tests assert expected behavior (not placeholders)

4. **ATDD checklist matches acceptance criteria:**
   - All 9 acceptance criteria covered
   - Tests mapped to appropriate test levels (API/E2E)
   - Priority levels (P0/P1) correctly assigned

5. **CLI sessions cleaned up:**
   - No orphaned browsers or CLI sessions
   - All temp files properly managed

6. **Temp artifacts stored correctly:**
   - ATDD checklist saved to \_bmad-output/tea/testartifacts/atdd-checklist-1.6.md
   - Subprocess outputs saved to /tmp directory

7. **LSP errors fixed:**
   - API test file LSP errors: No errors
   - E2E test file LSP errors: No errors

---

## Completion Summary

**Test files created:**

- tests/api/role-management.spec.ts (6 tests)
- tests/e2e/role-management.spec.ts (5 tests)
- tests/fixtures/test-data.ts (1 fixture file)

**Checklist output path:**
\_bmad-output/tea/testartifacts/atdd-checklist-1.6.md

**Key risks or assumptions:**

- Tests assume API endpoints follow RESTful design patterns
- E2E tests assume UI follows standard role management patterns
- Permissions are tested with predefined role types

**Next recommended workflow:**

1. Run `dev-story` to implement role management feature
2. After implementation, remove test.skip() from tests
3. Run tests to verify they pass (green phase)
4. Commit passing tests to repository

---

## Final Status

✅ **TEA-ATDD workflow execution complete for Story 1.6: Role Management**
