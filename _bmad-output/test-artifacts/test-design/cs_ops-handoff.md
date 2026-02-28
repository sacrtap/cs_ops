---
title: "TEA Test Design → BMAD Integration Handoff"
version: "1.0"
workflowType: "testarch-test-design-handoff"
inputDocuments:
  - _bmad-output/test-artifacts/test-design-architecture.md
  - _bmad-output/test-artifacts/test-design-qa.md
sourceWorkflow: "testarch-test-design"
generatedBy: "TEA Master Test Architect"
generatedAt: "2026-02-27T00:00:00.000Z"
projectName: "内部运营中台客户信息管理与运营系统 (cs_ops)"
---

# TEA → BMAD Integration Handoff

## Purpose

本文档桥接 TEA 的测试设计输出与 BMAD 的 epic/story 分解工作流（`create-epics-and-stories`）。它提供结构化的集成指南，确保质量要求、风险评估和测试策略能够流入实现规划。

## TEA Artifacts Inventory

| Artifact                                | Path                                                      | BMAD 集成点                    |
| --------------------------------------- | --------------------------------------------------------- | ------------------------------ |
| **Test Design Document (Architecture)** | `_bmad-output/test-artifacts/test-design-architecture.md` | Epic 质量要求、Story 验收标准  |
| **Test Design Document (QA)**           | `_bmad-output/test-artifacts/test-design-qa.md`           | Story 测试要求、P0/P1 场景映射 |
| **Risk Assessment**                     | (embedded in test design)                                 | Epic 风险分类、Story 优先级    |
| **Coverage Strategy**                   | (embedded in test design)                                 | Story 测试要求                 |

## Epic-Level Integration Guidance

### Risk References

**P0/P1 风险应作为 Epic 级质量门槛：**

| Epic                       | P0/P1 Risks                                       | Quality Gate                                                                                            |
| -------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Epic 1: 权限与认证**     | RISK-01 (权限数据泄露), RISK-04 (JWT 泄露)        | - 4 角色×8 模块权限矩阵测试 100% 通过<br>- 渗透测试无高危漏洞<br>- JWT 令牌短有效期（2 小时）+ 刷新机制 |
| **Epic 2: 客户主数据管理** | RISK-06 (Excel 脏数据)                            | - Excel 导入验证层 100% 通过<br>- 边界值测试（空文件/超大文件/特殊字符）<br>- 导入失败回滚机制          |
| **Epic 3: 客户健康度监控** | RISK-02 (Celery 任务失败), RISK-05 (定时任务重复) | - Celery 任务失败重试（3 次）<br>- 分布式锁防止重复执行<br>- 故障注入测试通过                           |
| **Epic 4: 客户价值评估**   | RISK-11 (定级规则错误)                            | - 规则边界测试（S 级=100 万 vs 99.9999 万）<br>- 历史数据重算准确性验证<br>- 规则变更审计日志           |
| **Epic 5: 结算管理**       | RISK-12 (结算金额错误)                            | - 结算准确性测试 100% 通过<br>- 异常数据检测（0 用量/突增）<br>- 财务对账 0 差异                        |

### Quality Gates

**每个 Epic 的推荐质量门槛（基于风险评估）：**

#### Epic 1: 权限与认证 (Infrastructure - Priority)

**Entry Criteria:**

- [ ] 所有权限需求明确（4 角色×8 模块矩阵）
- [ ] JWT 令牌规范定义（有效期、刷新机制）
- [ ] 数据权限规则明确（销售 vs 运营）

**Exit Criteria:**

- [ ] P0 测试 100% 通过（15 个）
- [ ] P1 测试通过率 ≥ 95%（~10 个）
- [ ] 渗透测试无高危漏洞
- [ ] 4 角色权限矩阵测试完整覆盖
- [ ] 未授权访问测试 100% 通过

**Definition of Done (per Story):**

- 故事级验收测试（ATDD）通过
- API 测试覆盖（成功 + 失败场景）
- 权限测试验证（角色 + 数据权限）

#### Epic 2: 客户主数据管理

**Entry Criteria:**

- [ ] Excel 导入格式规范定义
- [ ] 数据验证规则明确（必填/格式/业务规则）
- [ ] 批量导入/导出性能要求定义（≥1000 条/分钟）

**Exit Criteria:**

- [ ] P0 测试 100% 通过（2 个）
- [ ] P1 测试通过率 ≥ 95%（~8 个）
- [ ] Excel 导入验证测试 100% 通过
- [ ] 数据完整性测试通过

**Definition of Done (per Story):**

- 故事级验收测试通过
- CRUD API 测试覆盖
- 数据验证测试（边界值、格式）

#### Epic 3: 客户健康度监控

**Entry Criteria:**

- [ ] 僵尸账号识别规则定义（90 天未使用）
- [ ] 风险客户识别规则定义（7 天未使用）
- [ ] 预警推送规则定义（系统内 + 邮件）
- [ ] Celery 任务测试基础设施就绪

**Exit Criteria:**

- [ ] P0 测试 100% 通过（2 个）
- [ ] P1 测试通过率 ≥ 95%（~8 个）
- [ ] Celery 任务失败重试测试通过
- [ ] 定时任务手动触发接口可用

**Definition of Done (per Story):**

- 故事级验收测试通过
- 定时任务测试（手动触发 + 自动触发）
- 预警推送测试

#### Epic 4: 客户价值评估

**Entry Criteria:**

- [ ] 定级阈值定义（S/A/B/C/D）
- [ ] 定级规则变更流程定义
- [ ] 历史数据重算策略定义

**Exit Criteria:**

- [ ] P0 测试 100% 通过（1 个）
- [ ] P1 测试通过率 ≥ 95%（~6 个）
- [ ] 规则边界测试通过
- [ ] 历史重算准确性测试通过

**Definition of Done (per Story):**

- 故事级验收测试通过
- 规则配置测试
- 重算测试（批量 + 增量）

#### Epic 5: 结算管理

**Entry Criteria:**

- [ ] 三种结算模式算法定义（定价/阶梯/包年）
- [ ] 异常数据检测规则定义（0 用量/突增）
- [ ] 结算单审核流程定义
- [ ] 财务对账流程定义

**Exit Criteria:**

- [ ] P0 测试 100% 通过（2 个）
- [ ] P1 测试通过率 ≥ 95%（~10 个）
- [ ] 结算准确性测试 100% 通过
- [ ] 财务对账测试通过

**Definition of Done (per Story):**

- 故事级验收测试通过
- 结算算法测试（多种模式）
- 异常检测测试

---

## Story-Level Integration Guidance

### P0/P1 测试场景 → Story 验收标准

**关键测试场景必须作为 Story 验收标准：**

#### Epic 1: 权限与认证

**Story 1-1: 用户认证**

- ✅ 验收标准 1: 有效用户名密码登录返回 JWT Token（P0-001）
- ✅ 验收标准 2: 无效密码返回 401 错误（P0-011）
- ✅ 验收标准 3: Token 刷新机制可用（P0-002）
- ✅ 验收标准 4: Token 过期自动拒绝（P0-002）

**Story 1-2: JWT Token 管理**

- ✅ 验收标准 1: Token 有效期 2 小时（P0-002）
- ✅ 验收标准 2: Refresh Token 有效期 7 天（P0-002）
- ✅ 验收标准 3: Token 撤销后立即失效（P0-002）

**Story 1-3: 权限管理**

- ✅ 验收标准 1: 4 角色登录验证（P0-003）
- ✅ 验收标准 2: 无权限返回 403（P0-011）
- ✅ 验收标准 3: SQL 注入防护（P0-012）

**Story 1-4: 数据权限**

- ✅ 验收标准 1: 销售只能查看自己客户（P0-004）
- ✅ 验收标准 2: 运营可查看全部客户（P0-004）
- ✅ 验收标准 3: 销售转运营权限立即生效（P2-038）

#### Epic 2: 客户主数据管理

**Story 2-4: 批量导入客户**

- ✅ 验收标准 1: Excel 导入支持 1000+ 条/分钟（P0-006）
- ✅ 验收标准 2: 必填字段验证（P0-006）
- ✅ 验收标准 3: 格式验证（邮箱/电话/手机）（P0-006）
- ✅ 验收标准 4: 导入前预览确认（P1-047）
- ✅ 验收标准 5: 导入失败全部回滚（P2-012）

#### Epic 3: 客户健康度监控

**Story 3-2: 僵尸账号检测**

- ✅ 验收标准 1: 90 天未使用自动标记为僵尸账号（P0-007）
- ✅ 验收标准 2: 僵尸账号清单可导出（P0-007）
- ✅ 验收标准 3: 僵尸账号识别率 100%（P0-007）

**Story 3-3: 风险客户预警**

- ✅ 验收标准 1: 7 天未使用标记为风险客户（P1-008）
- ✅ 验收标准 2: 预警系统内通知（P1-008）
- ✅ 验收标准 3: 预警邮件推送（P1-008）

#### Epic 4: 客户价值评估

**Story 4-2: 定级规则配置**

- ✅ 验收标准 1: S 级阈值=100 万（边界 99.9999 万不是 S 级）（P0-010）
- ✅ 验收标准 2: 规则变更立即生效（P1-021）
- ✅ 验收标准 3: 规则变更审计日志（P1-019）

**Story 4-5: 等级重算**

- ✅ 验收标准 1: 批量重算 1320 个客户<1 分钟（P1-020）
- ✅ 验收标准 2: 重算结果准确性验证（P1-020）
- ✅ 验收标准 3: 重算历史记录（P1-019）

#### Epic 5: 结算管理

**Story 5-1: 结算单自动生成**

- ✅ 验收标准 1: Celery 异步任务生成结算单（P0-008）
- ✅ 验收标准 2: 任务失败自动重试（3 次）（P0-008）
- ✅ 验收标准 3: 任务执行日志完整（P0-008）

**Story 5-4: 异常数据检测**

- ✅ 验收标准 1: 0 用量客户自动标记（P0-009）
- ✅ 验收标准 2: 用量突增（>300%）自动标记（P0-009）
- ✅ 验收标准 3: 异常数据人工确认流程（P1-027）

**Story 5-3: 自动计算金额**

- ✅ 验收标准 1: 定价结算模式计算准确（P1-020）
- ✅ 验收标准 2: 阶梯结算模式计算准确（P1-020）
- ✅ 验收标准 3: 包年结算模式计算准确（P1-020）
- ✅ 验收标准 4: 财务对账 0 差异（P1-041）

### Data-TestId Requirements

**推荐的 data-testid 属性命名规范（提升 E2E 测试可维护性）：**

#### 通用规范

```typescript
// 格式：[模块]-[功能]-[类型]-[描述]
// 示例：
[data-testid="customer-list-table"]           // 客户列表表格
[data-testid="customer-create-button"]         // 客户新建按钮
[data-testid="customer-form-name-input"]       // 客户表单 - 名称输入框
[data-testid="customer-form-email-input"]      // 客户表单 - 邮箱输入框
[data-testid="customer-form-submit-button"]    // 客户表单 - 提交按钮
[data-testid="customer-delete-confirm-dialog"] // 客户删除 - 确认对话框
```

#### 权限相关

```typescript
[data-testid="login-email-input"]
[data-testid="login-password-input"]
[data-testid="login-button"]
[data-testid="login-error-message"]
[data-testid="user-role-badge"]                // 用户角色标记
[data-testid="permission-denied-message"]      // 权限不足提示
```

#### 客户管理

```typescript
[data-testid="customer-list-page"]
[data-testid="customer-detail-page"]
[data-testid="customer-create-page"]
[data-testid="customer-edit-page"]
[data-testid="customer-import-page"]
[data-testid="customer-export-button"]
[data-testid="customer-search-input"]
[data-testid="customer-filter-status"]
[data-testid="customer-filter-value-level"]
```

#### 健康度监控

```typescript
[data-testid="health-dashboard-page"]
[data-testid="health-score-display"]
[data-testid="risk-level-badge"]
[data-testid="zombie-account-list"]
[data-testid="risk-customer-list"]
[data-testid="warning-notification"]
```

#### 结算管理

```typescript
[data-testid="settlement-generate-button"]
[data-testid="settlement-list-page"]
[data-testid="settlement-detail-page"]
[data-testid="settlement-pdf-preview"]
[data-testid="settlement-send-button"]
[data-testid="settlement-status-badge"]
```

---

## Risk-to-Story Mapping

| Risk ID     | Category | P×I   | Recommended Story/Epic                     | Test Level |
| ----------- | -------- | ----- | ------------------------------------------ | ---------- |
| **RISK-01** | **SEC**  | **6** | Epic 1 (所有权限 Stories)                  | API + E2E  |
| **RISK-02** | **DATA** | **6** | Epic 3 (健康度定时任务), Epic 5 (结算生成) | API        |
| **RISK-03** | **PERF** | **6** | Epic 2 (客户列表查询), Epic 5 (结算计算)   | API        |
| **RISK-04** | **SEC**  | **6** | Epic 1 (JWT Token 管理)                    | API        |
| **RISK-05** | **DATA** | **4** | Epic 3 (定时任务)                          | API        |
| **RISK-06** | **DATA** | **6** | Epic 2 (批量导入)                          | API + E2E  |
| **RISK-07** | **TECH** | **3** | 所有 E2E Stories                           | E2E        |
| **RISK-08** | **TECH** | **4** | DevOps (数据库迁移)                        | DevOps     |
| **RISK-09** | **TECH** | **6** | Epic 3 (预警推送), Epic 5 (邮件发送)       | API        |
| **RISK-10** | **TECH** | **4** | QA Infrastructure                          | QA         |
| **RISK-11** | **BUS**  | **6** | Epic 4 (定级规则)                          | API + E2E  |
| **RISK-12** | **BUS**  | **6** | Epic 5 (结算计算)                          | API + E2E  |

## Recommended BMAD → TEA Workflow Sequence

1. **TEA Test Design** (`TD`) → 生成本交接文档
2. **BMAD Create Epics & Stories** → 消费本交接文档，嵌入质量要求
3. **TEA ATDD** (`AT`) → 为每个 Story 生成验收测试
4. **BMAD Implementation** → 开发人员实现（测试驱动）
5. **TEA Automate** (`TA`) → 生成完整测试套件
6. **TEA Trace** (`TR`) → 验证覆盖完整性

## Phase Transition Quality Gates

| From Phase              | To Phase                | Gate Criteria                                                                    |
| ----------------------- | ----------------------- | -------------------------------------------------------------------------------- |
| **Test Design**         | **Epic/Story Creation** | - 所有 P0 风险有缓解策略<br>- 高风险缓解措施已定义<br>- 测试覆盖矩阵完成         |
| **Epic/Story Creation** | **ATDD**                | - Stories 有验收标准（来自测试设计）<br>- 质量门槛明确<br>- 数据-testid 规范定义 |
| **ATDD**                | **Implementation**      | - 所有 P0/P1 场景有失败的验收测试<br>- 测试基础设施就绪<br>- Mock 基础设施就绪   |
| **Implementation**      | **Test Automation**     | - 所有验收测试通过<br>- 代码审查通过<br>- 集成测试通过                           |
| **Test Automation**     | **Release**             | - 追踪矩阵显示 P0/P1 要求覆盖率≥80%<br>- 性能基准达标<br>- 无高优先级 Bug        |

---

**Generated by:** BMad TEA Agent  
**Workflow:** `_bmad/tea/testarch/test-design`  
**Version:** 4.0 (BMad v6)  
**Next Step:** Use this handoff document in `bmad-bmm-create-epics-and-stories` workflow
