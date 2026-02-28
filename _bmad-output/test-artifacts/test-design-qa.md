---
stepsCompleted:
  [
    "step-01-detect-mode",
    "step-02-load-context",
    "step-03-risk-and-testability",
    "step-04-coverage-plan",
    "step-05-generate-output",
  ]
lastStep: "step-05-generate-output"
lastSaved: "2026-02-27T00:00:00.000Z"
workflowType: "testarch-test-design"
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad/tea/config.yaml
  - _bmad-output/test-artifacts/test-design-architecture.md
---

# Test Design for QA: 内部运营中台客户信息管理与运营系统

**Purpose:** QA 团队测试执行指南。定义测试什么、如何测试，以及 QA 需要从其他团队获得什么。

**Date:** 2026-02-27  
**Author:** TEA Master Test Architect  
**Status:** 草稿  
**Project:** 内部运营中台客户信息管理与运营系统 (cs_ops)

**Related:** 请参阅架构文档 (`test-design-architecture.md`) 了解可测试性关注点和架构阻塞点

---

## Executive Summary

**Scope:** 系统级测试设计，覆盖 8 个 Epic、58 个用户故事的完整测试策略

**Risk Summary:**

- **Total Risks**: 12 个 (8 个高风险 score≥6, 3 个中风险，1 个低风险)
- **Critical Categories**: SEC (安全), DATA (数据完整性), BUS (业务影响)

**Coverage Summary:**

- **P0 tests**: ~45 个（关键路径、安全、权限）
- **P1 tests**: ~60 个（重要功能、集成测试）
- **P2 tests**: ~40 个（边界条件、回归测试）
- **P3 tests**: ~15 个（探索性测试、性能基准）
- **Total**: ~160 个测试 (~6-9 周，1 名 QA 全职)

---

## Not in Scope

**明确排除在此测试计划之外的组件或系统：**

| 项目                          | 排除原因                         | 缓解措施                                     |
| ----------------------------- | -------------------------------- | -------------------------------------------- |
| **Docker 镜像构建测试**       | 由 DevOps 团队负责，使用基础镜像 | DevOps 团队验证，QA 仅提供功能验证清单       |
| **PostgreSQL 数据库性能调优** | DBA 团队负责，专业领域           | 依赖 DBA 性能测试报告，QA 验证应用层查询性能 |
| **Vue 组件单元测试**          | 前端开发负责，粒度太细           | 通过 E2E 测试验证组件集成行为                |
| **第三方邮件服务功能测试**    | 外部服务，由供应商保证           | 仅测试邮件发送接口集成，不验证邮件服务本身   |
| **Excel 文件格式兼容性测试**  | 使用成熟库 (pandas)，风险低      | 仅验证导入业务逻辑，不测试 pandas 库本身     |
| **网络层 SSL/TLS 配置测试**   | DevOps/安全团队负责              | 依赖安全团队渗透测试报告                     |
| **移动端原生功能测试**        | 仅支持移动浏览器，非原生 App     | 使用 Playwright 移动端浏览器测试             |

**注意:** 此处列出的项目已经过 QA、开发和产品经理评审并接受为排除范围

---

## Dependencies & Test Blockers

**关键:** 没有这些项目，QA 无法开始测试

### 后端/架构依赖（预实现）

**来源:** 请参阅架构文档"快速指南"了解详细的缓解计划

1. **Celery 任务测试隔离机制 (BLK-01)** - 后端团队 - 预实现
   - 提供测试专用 Celery eager 模式配置 (`CELERY_TASK_ALWAYS_EAGER=True`)
   - 或提供同步任务执行器用于测试
   - **阻塞原因:** 无法测试结算生成、批量导入等异步任务

2. **外部 API Mock 基础设施 (BLK-02)** - 后端团队 - 预实现
   - 完整 mock 邮件服务、用量采集接口
   - 禁止测试调用真实外部服务
   - **阻塞原因:** 外部服务不稳定导致集成测试失败

3. **数据权限测试支持 (BLK-03)** - 后端团队 - 预实现
   - 提供测试专用数据库视图或查询接口
   - 支持断言不同角色的数据权限过滤
   - **阻塞原因:** 无法验证销售只能看自己客户、运营看全部的权限逻辑

### QA 基础设施搭建（预实现）

1. **测试数据工厂** - QA
   - CustomerFactory 扩展（支持价值等级、设备类型、结算模式）
   - UserFactory 扩展（支持 4 角色、数据权限）
   - 自动清理 fixture 确保并行安全

2. **测试环境** - QA + DevOps
   - Local: Docker Compose 本地环境（PostgreSQL + Redis + Celery）
   - CI/CD: GitHub Actions 配置，并行测试支持
   - Staging: 与生产环境配置一致

**示例工厂模式:**

```python
# tests/support/factories/customer_factory.py
from faker import Faker
from datetime import datetime

fake = Faker('zh_CN')

class CustomerFactory:
    """客户数据工厂 - 扩展支持业务字段"""

    @classmethod
    def create(cls, overrides=None):
        """创建客户测试数据"""
        data = {
            "name": fake.company(),
            "email": fake.company_email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "status": "active",
            # 业务字段
            "value_level": fake.random_element(["S", "A", "B", "C", "D"]),
            "annual_consumption": fake.random_int(10000, 2000000),
            "settlement_mode": fake.random_element([
                "pricing",      # 定价结算
                "tiered",       # 阶梯结算
                "yearly"        # 包年结算
            ]),
            "equipment_types": fake.random_elements(
                ["X_single", "X_multi", "N_single", "N_multi", "L_single", "L_multi"],
                length=fake.random_int(1, 3)
            ),
            "health_score": fake.random_int(0, 100),
            "risk_level": fake.random_element(["low", "medium", "high"]),
            "last_activity_date": fake.date_time_between(start_date="-90d", end_date="now"),
        }

        if overrides:
            data.update(overrides)

        return data

    @classmethod
    def create_zombie_account(cls):
        """创建僵尸账号（90 天未使用）"""
        return cls.create({
            "last_activity_date": fake.date_time_between(
                start_date="-180d", end_date="-91d"
            ),
            "health_score": fake.random_int(0, 30),
            "risk_level": "high",
        })

    @classmethod
    def create_risk_customer(cls):
        """创建风险客户（7 天未使用）"""
        return cls.create({
            "last_activity_date": fake.date_time_between(
                start_date="-14d", end_date="-8d"
            ),
            "health_score": fake.random_int(30, 60),
            "risk_level": "medium",
        })
```

```python
# tests/support/factories/user_factory.py
class UserFactory:
    """用户数据工厂 - 支持 4 级权限"""

    @classmethod
    def create(cls, role="operator", overrides=None):
        """创建用户测试数据

        Args:
            role: admin | manager | specialist | sales
        """
        data = {
            "email": fake.email(),
            "username": fake.user_name(),
            "password": "Test123456!",  # 符合密码策略
            "role": role,
            # 数据权限字段
            "assigned_customers": [] if role == "sales" else None,
        }

        if overrides:
            data.update(overrides)

        return data

    @classmethod
    def create_sales(cls, customer_ids=None):
        """创建销售用户（有 assigned_customers）"""
        return cls.create(role="sales", {
            "assigned_customers": customer_ids or [],
        })
```

---

## Risk Assessment

**注意:** 完整风险详情在架构文档中。本节总结与 QA 测试计划相关的风险。

### 高风险 (Score ≥6)

| Risk ID     | Category | Description                     | Score | QA 测试覆盖                                          |
| ----------- | -------- | ------------------------------- | ----- | ---------------------------------------------------- |
| **RISK-01** | SEC      | 权限系统缺陷导致数据泄露        | **6** | 4 角色×8 模块权限矩阵测试，每个 API 验证数据权限过滤 |
| **RISK-02** | DATA     | Celery 任务失败导致结算数据丢失 | **6** | 任务失败重试测试，故障注入测试，幂等性测试           |
| **RISK-03** | PERF     | 大数据量下性能不达标            | **6** | pytest-benchmark 性能基准测试，10 万 + 数据压力测试  |
| **RISK-04** | SEC      | JWT 令牌泄露导致未授权访问      | **6** | 认证测试（未授权/过期/刷新），HTTPS 强制，二次认证   |
| **RISK-06** | DATA     | Excel 导入验证不足导致脏数据    | **6** | 边界值测试（空文件/超大文件/特殊字符），验证层测试   |
| **RISK-09** | TECH     | 外部 API 不稳定导致集成测试失败 | **6** | pytest-httpx mock 测试，契约测试，超时测试           |
| **RISK-11** | BUS      | 定级规则配置错误                | **6** | 规则边界测试，变更影响测试，历史重算测试             |
| **RISK-12** | BUS      | 结算金额计算错误                | **6** | 结算准确性测试，异常检测测试，财务对账测试           |

### 中/低风险

| Risk ID | Category | Description      | Score | QA 测试覆盖                    |
| ------- | -------- | ---------------- | ----- | ------------------------------ |
| RISK-05 | DATA     | 定时任务重复执行 | **4** | 分布式锁测试，手动触发接口测试 |
| RISK-08 | TECH     | 数据库迁移失败   | **4** | CI 中迁移测试，回滚测试        |
| RISK-10 | TECH     | 并发测试数据竞争 | **4** | 并行测试隔离测试，重试机制测试 |
| RISK-07 | TECH     | E2E 测试维护成本 | **3** | 页面对象模式，data-testid 规范 |

---

## Entry Criteria

**QA 测试在以下所有条件满足前不能开始：**

- [ ] 所有需求和假设经 QA、Dev、PM 达成一致
- [ ] 测试环境已配置并可访问（PostgreSQL + Redis + Celery）
- [ ] 测试数据工厂就绪或种子数据可用
- [ ] 预实现阻塞项已解决（BLK-01/02/03，见 Dependencies 章节）
- [ ] 功能已部署到测试环境
- [ ] 外部 API Mock 基础设施就绪
- [ ] CI/CD 流水线配置完成（支持并行测试）

## Exit Criteria

**测试阶段在以下所有条件满足时完成：**

- [ ] 所有 P0 测试通过
- [ ] 所有 P1 测试通过（或失败已分类并接受）
- [ ] 无未解决的高优先级/高严重性 Bug
- [ ] 测试覆盖率经 QA Lead 和 Dev Lead 同意为充分
- [ ] 性能基线达标（关键查询<1 秒，复杂查询<5 秒）
- [ ] 高风险缓解措施已完成
- [ ] 代码覆盖率 ≥ 80%

---

## Project Team

| 姓名    | 角色                | 测试职责                             |
| ------- | ------------------- | ------------------------------------ |
| Sacrtap | QA Lead / Architect | 测试策略、测试架构设计、测试评审     |
| TBD     | Dev Lead            | 单元测试、集成测试支持、可测试性钩子 |
| TBD     | PM                  | 需求澄清、验收标准、UAT 验收         |
| TBD     | Backend Dev         | 后端 API 测试实现、数据工厂          |
| TBD     | Frontend Dev        | 前端 E2E 测试实现、页面对象模式      |

---

## Test Coverage Plan

**重要:** P0/P1/P2/P3 = **优先级和风险级别**（如果时间有限应该关注什么），**不是**执行时机。详见"执行策略"章节。

### P0 (关键)

**标准:** 阻塞核心功能 + 高风险 (≥6) + 无变通方案 + 影响大多数用户

| Test ID    | Requirement         | Test Level | Risk Link        | Notes                    |
| ---------- | ------------------- | ---------- | ---------------- | ------------------------ |
| **P0-001** | FR45-用户登录认证   | API        | RISK-01, RISK-04 | 4 角色登录，JWT 生成验证 |
| **P0-002** | FR46-JWT Token 管理 | API        | RISK-04          | Token 刷新、过期、撤销   |
| **P0-003** | FR47-权限控制       | API        | RISK-01          | 4 角色×8 模块权限矩阵    |
| **P0-004** | FR48-数据权限过滤   | API        | RISK-01          | 销售只看自己客户         |
| **P0-005** | FR1-客户列表 CRUD   | API + E2E  | RISK-01          | 完整 CRUD 流程           |
| **P0-006** | FR4-批量导入客户    | API + E2E  | RISK-06          | Excel 导入，验证层测试   |
| **P0-007** | FR9-僵尸账号识别    | API        | RISK-02          | 90 天未使用自动标记      |
| **P0-008** | FR23-结算单自动生成 | API        | RISK-02, RISK-12 | Celery 异步任务测试      |
| **P0-009** | FR26-异常数据检测   | API        | RISK-12          | 0 用量、用量突增检测     |
| **P0-010** | FR33-定级规则配置   | API        | RISK-11          | 阈值边界测试             |
| **P0-011** | 安全-未授权访问     | API        | RISK-04          | 无 Token 返回 401        |
| **P0-012** | 安全-SQL 注入防护   | API        | RISK-01          | SQL 注入攻击测试         |
| **P0-013** | 安全-XSS 防护       | E2E        | RISK-01          | XSS 攻击测试             |
| **P0-014** | 性能-关键查询<1 秒  | API        | RISK-03          | 客户列表/详情查询        |
| **P0-015** | 性能-复杂查询<5 秒  | API        | RISK-03          | 多条件筛选/统计          |

**Total P0:** ~15 个测试

---

### P1 (高)

**标准:** 重要功能 + 中风险 (3-4) + 常见工作流 + 变通方案存在但困难

| Test ID    | Requirement            | Test Level | Risk Link        | Notes                       |
| ---------- | ---------------------- | ---------- | ---------------- | --------------------------- |
| **P1-001** | FR2-客户详情 360 视图  | E2E        | -                | 完整客户信息展示            |
| **P1-002** | FR3-客户新增           | API + E2E  | -                | 表单验证、业务规则          |
| **P1-003** | FR5-批量导出客户       | API        | -                | Excel 导出，自定义字段      |
| **P1-004** | FR6-客户搜索           | API        | -                | 多条件搜索                  |
| **P1-005** | FR7-客户状态管理       | API        | -                | active/inactive 切换        |
| **P1-006** | FR8-数据完整性验证     | API        | -                | 必填字段、格式验证          |
| **P1-007** | FR10-风险客户预警      | API        | -                | 7 天未使用标记              |
| **P1-008** | FR11-预警通知系统      | API        | -                | 系统内通知 + 邮件推送       |
| **P1-009** | FR12-健康度自动更新    | API        | RISK-05          | 定时任务触发                |
| **P1-010** | FR13-风险评分计算      | API        | -                | 健康度评分算法              |
| **P1-011** | FR14-预警历史查询      | API        | -                | 预警记录列表                |
| **P1-012** | FR15-健康趋势分析      | E2E        | -                | 趋势图可视化                |
| **P1-013** | FR16-运营仪表盘        | E2E        | -                | 关键指标概览                |
| **P1-014** | FR17-价值等级显示      | API + E2E  | -                | S/A/B/C/D 展示              |
| **P1-015** | FR18-人工定级维护      | API + E2E  | RISK-11          | 手动调整等级                |
| **P1-016** | FR19-定级历史记录      | API        | RISK-11          | 变更记录查询                |
| **P1-017** | FR20-等级重算          | API        | RISK-11          | 批量重算 1320 客户          |
| **P1-018** | FR21-规则立即生效      | API        | RISK-11          | 配置后立即应用              |
| **P1-019** | FR24-自动关联价格      | API        | RISK-12          | 结算模式×价格关联           |
| **P1-020** | FR25-自动计算金额      | API        | RISK-12          | 结算引擎计算逻辑            |
| **P1-021** | FR27-异常数据确认      | E2E        | RISK-12          | 人工确认异常流程            |
| **P1-022** | FR28-结算单导出        | API        | -                | PDF 生成                    |
| **P1-023** | FR29-批量发送结算单    | API        | -                | 邮件群发、记录日志          |
| **P1-024** | FR30-发送日志查询      | API        | -                | 发送历史记录                |
| **P1-025** | FR31-结算历史查询      | API        | -                | 历史结算单列表              |
| **P1-026** | FR32-结算单审批        | E2E        | RISK-12          | 审核流程                    |
| **P1-027** | FR34-客户转移          | API + E2E  | -                | 转移操作、记录历史          |
| **P1-028** | FR35-操作日志          | API        | -                | 增删改/转移/导出记录        |
| **P1-029** | FR36-审计日志查询      | API        | -                | 日志列表、筛选              |
| **P1-030** | FR37-数据备份          | API        | -                | 手动备份、恢复              |
| **P1-031** | FR38-设备类型管理      | API        | -                | X/N/L 设备 CRUD             |
| **P1-032** | FR39-客户设备关联      | API        | -                | 多设备类型关联              |
| **P1-033** | FR40-结算模式配置      | API        | -                | 三种模式切换                |
| **P1-034** | FR41-定价结算配置      | API        | -                | 6 种单价配置                |
| **P1-035** | FR42-阶梯结算配置      | API        | -                | 阶梯规则配置                |
| **P1-036** | FR43-包年套餐配置      | API        | -                | A/B/C/D 套餐配置            |
| **P1-037** | FR44-结算模式切换      | API        | -                | 无需审批切换                |
| **P1-038** | FR49-角色管理          | API        | RISK-01          | 角色 CRUD、权限分配         |
| **P1-039** | FR50-权限继承          | API        | RISK-01          | 角色权限继承逻辑            |
| **P1-040** | FR51-权限审计          | API        | RISK-01          | 权限变更日志                |
| **P1-041** | 集成 - 客户 - 结算     | API        | RISK-12          | 客户 + 结算集成测试         |
| **P1-042** | 集成 - 健康度 - 预警   | API        | -                | 健康度 + 预警集成           |
| **P1-043** | 集成 - 定级 - 重算     | API        | RISK-11          | 定级 + 重算集成             |
| **P1-044** | E2E - 创建客户完整流程 | E2E        | -                | 列表→新建→验证              |
| **P1-045** | E2E - 编辑客户完整流程 | E2E        | -                | 列表→编辑→验证              |
| **P1-046** | E2E - 删除客户完整流程 | E2E        | -                | 列表→删除→验证              |
| **P1-047** | E2E - 导入客户完整流程 | E2E        | RISK-06          | 上传→预览→确认              |
| **P1-048** | E2E - 生成结算单流程   | E2E        | RISK-02, RISK-12 | 选择月份→生成→异常检查→发送 |
| **P1-049** | E2E - 定级规则配置流程 | E2E        | RISK-11          | 配置→重算→验证              |
| **P1-050** | E2E - 权限切换流程     | E2E        | RISK-01          | 不同角色登录验证权限        |
| **P1-051** | 边界值 - 空数据        | API        | -                | 空列表、空表单              |
| **P1-052** | 边界值 - 大数据量      | API        | RISK-03          | 1000+ 条导入                |
| **P1-053** | 边界值 - 特殊字符      | API        | -                | 中文、emoji、SQL 注入字符   |
| **P1-054** | 错误处理 - 400         | API        | -                | 无效请求返回 400            |
| **P1-055** | 错误处理 - 403         | API        | RISK-01          | 无权限返回 403              |
| **P1-056** | 错误处理 - 404         | API        | -                | 资源不存在返回 404          |
| **P1-057** | 错误处理 - 500         | API        | -                | 服务器错误返回 500          |
| **P1-058** | 错误处理 - 友好提示    | E2E        | -                | 错误消息用户友好            |
| **P1-059** | 兼容性 - Chrome        | E2E        | -                | Chrome 浏览器测试           |
| **P1-060** | 兼容性 - Firefox       | E2E        | -                | Firefox 浏览器测试          |

**Total P1:** ~60 个测试

---

### P2 (中)

**标准:** 次要功能 + 低风险 (1-2) + 边界条件 + 回归预防

| Test ID    | Requirement           | Test Level | Risk Link | Notes                     |
| ---------- | --------------------- | ---------- | --------- | ------------------------- |
| **P2-001** | 分页 - 第 1 页        | API        | -         | 标准分页                  |
| **P2-002** | 分页 - 最后一页       | API        | -         | 边界分页                  |
| **P2-003** | 分页 - 超出范围       | API        | -         | 页码超出范围处理          |
| **P2-004** | 排序 - 升序           | API        | -         | 按创建时间升序            |
| **P2-005** | 排序 - 降序           | API        | -         | 按创建时间降序            |
| **P2-006** | 筛选 - 单条件         | API        | -         | 单条件筛选                |
| **P2-007** | 筛选 - 多条件组合     | API        | -         | 多条件组合筛选            |
| **P2-008** | 搜索 - 模糊匹配       | API        | -         | 名称模糊搜索              |
| **P2-009** | 搜索 - 精确匹配       | API        | -         | ID 精确搜索               |
| **P2-010** | 导出 - 自定义字段     | API        | -         | 选择导出字段              |
| **P2-011** | 导出 - 全部字段       | API        | -         | 导出所有字段              |
| **P2-012** | 导入 - 部分失败       | API        | RISK-06   | 部分数据失败回滚          |
| **P2-013** | 导入 - 重复数据       | API        | -         | 重复客户处理              |
| **P2-014** | 健康度 - 分数边界     | API        | -         | 0 分、100 分边界          |
| **P2-015** | 健康度 - 风险等级边界 | API        | -         | low/medium/high 边界      |
| **P2-016** | 预警 - 推送频率限制   | API        | -         | 同一客户不重复推送        |
| **P2-017** | 定级 - 边界值         | API        | RISK-11   | S 级=100 万 vs 99.9999 万 |
| **P2-018** | 定级 - 向下调整       | API        | RISK-11   | S→A 降级                  |
| **P2-019** | 定级 - 向上调整       | API        | RISK-11   | A→S 升级                  |
| **P2-020** | 重算 - 部分客户       | API        | RISK-11   | 批量重算子集              |
| **P2-021** | 结算 - 0 用量         | API        | RISK-12   | 0 用量客户结算            |
| **P2-022** | 结算 - 负值处理       | API        | RISK-12   | 负用量处理                |
| **P2-023** | 结算 - 超量处理       | API        | RISK-12   | 包年超量计费              |
| **P2-024** | 结算 - 多种模式切换   | API        | RISK-12   | 定价→阶梯→包年切换        |
| **P2-025** | 转移 - 批量转移       | API        | -         | 一次转移多个客户          |
| **P2-026** | 转移 - 转移历史       | API        | -         | 转移记录查询              |
| **P2-027** | 日志 - 时间范围筛选   | API        | -         | 按日期范围查询日志        |
| **P2-028** | 日志 - 操作类型筛选   | API        | -         | 按操作类型查询            |
| **P2-029** | 备份 - 恢复验证       | API        | -         | 备份数据恢复测试          |
| **P2-030** | 设备 - 多设备关联     | API        | -         | 客户关联多个设备          |
| **P2-031** | 价格 - 单价边界       | API        | -         | 0 单价、最大单价          |
| **P2-032** | 阶梯 - 多阶梯         | API        | -         | 多阶梯规则配置            |
| **P2-033** | 套餐 - 套餐升级       | API        | -         | A→B 套餐升级              |
| **P2-034** | 套餐 - 套餐降级       | API        | -         | B→A 套餐降级              |
| **P2-035** | Token - 边界时间      | API        | RISK-04   | Token 即将过期            |
| **P2-036** | Token - 刷新链        | API        | RISK-04   | 多次刷新                  |
| **P2-037** | 权限 - 角色切换       | API        | RISK-01   | 用户角色变更              |
| **P2-038** | 权限 - 数据权限边界   | API        | RISK-01   | 销售转运营权限变化        |
| **P2-039** | 性能 - 并发读取       | API        | RISK-03   | 50 用户并发查询           |
| **P2-040** | 性能 - 并发写入       | API        | RISK-03   | 10 用户并发创建           |

**Total P2:** ~40 个测试

---

### P3 (低)

**标准:** 锦上添花 + 探索性测试 + 性能基准 + 文档验证

| Test ID    | Requirement               | Test Level | Notes                       |
| ---------- | ------------------------- | ---------- | --------------------------- |
| **P3-001** | 性能基准 - 单查询         | API        | 单查询性能基线              |
| **P3-002** | 性能基准 - 批量查询       | API        | 批量查询性能基线            |
| **P3-003** | 性能基准 - 导入速度       | API        | 导入速度基线（条/分钟）     |
| **P3-004** | 性能基准 - 并发性能       | API        | 并发性能曲线                |
| **P3-005** | 探索性 - 异常操作序列     | E2E        | 非标准操作序列测试          |
| **P3-006** | 探索性 - 极端数据         | API        | 极端大数据量测试            |
| **P3-007** | 文档验证 - API 文档一致性 | API        | Swagger 文档与实际 API 一致 |
| **P3-008** | 文档验证 - 错误码文档     | API        | 错误码文档完整性            |
| **P3-009** | 可访问性 - 键盘导航       | E2E        | 键盘操作可访问性            |
| **P3-010** | 可访问性 - 屏幕阅读器     | E2E        | 屏幕阅读器兼容              |
| **P3-011** | 移动端 - 响应式布局       | E2E        | 手机端布局适配              |
| **P3-012** | 移动端 - 触摸手势         | E2E        | 触摸手势支持                |
| **P3-013** | 国际化 - 中文显示         | E2E        | 中文显示正常                |
| **P3-014** | 兼容性 - Safari           | E2E        | Safari 浏览器测试           |
| **P3-015** | 兼容性 - 移动端 Chrome    | E2E        | 移动端 Chrome 测试          |

**Total P3:** ~15 个测试

---

## Execution Strategy

**Philosophy:** 在 PR 中运行所有测试，除非有显著的基础设施开销。Playwright 并行化非常快（数百个测试在~10-15 分钟内）。

**按工具类型组织:**

### 每个 PR: Playwright 测试 (~10-15 分钟)

**所有功能测试**（来自任何优先级）:

- 所有 E2E、API、集成、单元测试使用 Playwright
- 并行化跨 ~8 个分片
- 总计：~160 个 Playwright 测试（包括 P0、P1、P2、P3）

**为什么在 PR 中运行:** 快速反馈，无需昂贵基础设施

**配置示例** (`playwright.config.ts`):

```typescript
export default defineConfig({
  testDir: "./tests",
  fullyParallel: true, // 完全并行
  workers: process.env.CI ? "100%" : undefined, // CI 中使用所有 CPU
  retries: process.env.CI ? 2 : 0, // CI 中重试 2 次
  reporter: [
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["junit", { outputFile: "test-results/junit.xml" }],
    ["list"],
  ],
  // 使用标签选择测试
  grep: /@P0|@P1/, // PR 中运行 P0+P1
});
```

**PR 测试命令:**

```bash
# 运行所有 Playwright 测试（默认）
npx playwright test

# 仅运行 P0 测试
npx playwright test --grep @P0

# 仅运行 P0+P1 测试（快速 PR）
npx playwright test --grep "@P0|@P1"

# 仅运行 API 测试
npx playwright test --grep @API

# 仅运行 E2E 测试
npx playwright test --grep @E2E
```

### 每日夜间：k6 性能测试 (~30-60 分钟)

**所有性能测试**（来自任何优先级）:

- 负载测试、压力测试、峰值测试、耐久测试
- 总计：~5 个 k6 测试（可能包括 P0、P1、P2）

**为什么延迟到夜间运行:** 昂贵基础设施（k6 Cloud），长运行（每个测试 10-40 分钟）

**性能测试场景:**

1. **负载测试** - 50 并发用户，持续 10 分钟
   - 验证系统在正常负载下性能达标

2. **压力测试** - 100 并发用户，持续 20 分钟
   - 找出系统瓶颈和性能极限

3. **峰值测试** - 从 10 用户逐步增加到 200 用户
   - 验证系统弹性扩展能力

4. **耐久测试** - 50 并发用户，持续 4 小时
   - 验证内存泄漏、性能退化

5. **大数据量测试** - 10 万 + 客户数据，50 并发查询
   - 验证大数据量下查询性能

**k6 脚本示例:**

```javascript
// performance-tests/load-test.js
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "5m", target: 50 }, // 5 分钟增加到 50 用户
    { duration: "10m", target: 50 }, // 保持 50 用户 10 分钟
    { duration: "5m", target: 0 }, // 5 分钟减少到 0
  ],
  thresholds: {
    http_req_duration: ["p(95)<1000"], // 95% 请求<1 秒
    http_req_failed: ["rate<0.01"], // 失败率<1%
  },
};

export default function () {
  const params = {
    headers: {
      Authorization: `Bearer ${__ENV.JWT_TOKEN}`,
    },
  };

  const res = http.get("http://localhost:8000/api/v1/customers", params);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 1s": (r) => r.timings.duration < 1000,
  });

  sleep(1);
}
```

### 每周：混沌工程与长运行 (~小时)

**特殊基础设施测试**（来自任何优先级）:

- 多区域故障转移（需要 AWS Fault Injection Simulator）
- 灾难恢复（备份恢复，4+ 小时）
- 耐久测试（4+ 小时运行时间）

**为什么延迟到每周运行:** 非常昂贵的基础设施，运行时间非常长，低频验证已足够

**混沌工程测试场景:**

1. **数据库故障注入** - 模拟 PostgreSQL 宕机 30 秒
   - 验证系统自动恢复能力

2. **Redis 故障注入** - 模拟 Redis 不可用
   - 验证降级策略（缓存失效→直接查库）

3. **Celery 故障注入** - 模拟 Celery Worker 宕机
   - 验证任务重试机制

4. **网络延迟注入** - 模拟网络延迟 500ms-2s
   - 验证超时配置和重试逻辑

5. **备份恢复测试** - 从备份恢复完整数据库
   - 验证备份可用性和恢复流程

**手动测试**（排除在自动化外）:

- DevOps 验证（部署、监控）
- 财务验证（成本告警）
- 文档验证

---

## QA Effort Estimate

**仅 QA 测试开发工作量**（不包括 DevOps、后端、数据工程、财务工作）:

| 优先级    | 数量     | 工作量范围  | 说明                           |
| --------- | -------- | ----------- | ------------------------------ |
| P0        | ~15      | ~2-3 周     | 复杂设置（安全、性能、多步骤） |
| P1        | ~60      | ~3-4 周     | 标准覆盖（集成、API 测试）     |
| P2        | ~40      | ~1-2 周     | 边界条件、简单验证             |
| P3        | ~15      | ~2-3 天     | 探索性测试、基准测试           |
| **Total** | **~160** | **~6-9 周** | **1 名 QA 工程师，全职**       |

**假设:**

- 包括测试设计、实现、调试、CI 集成
- 不包括持续维护（约 10% 工作量）
- 假设测试基础设施（factories、fixtures）就绪
- 假设阻塞项（BLK-01/02/03）已解决

**来自其他团队的依赖:**

- 见"Dependencies & Test Blockers"章节了解 QA 需要从后端、DevOps、数据工程获得什么

**分阶段实施建议:**

- **Sprint 1-2**: P0 测试（权限认证、核心 CRUD、安全）
- **Sprint 3-4**: P1 测试（重要功能、集成测试）
- **Sprint 5-6**: P2 测试（边界条件、回归测试）
- **Sprint 7**: P3 测试（探索性测试、性能基准）

---

## Implementation Planning Handoff

**仅当此测试设计产生需要排期的实现任务时包含。**

**用于告知实现规划；如果没有专职 QA，分配给开发负责人。**

| 工作项                | 负责人      | 目标里程碑（可选） | 依赖/说明        |
| --------------------- | ----------- | ------------------ | ---------------- |
| Celery eager 模式配置 | 后端        | Sprint 1           | BLK-01，预实现   |
| HTTP Mock 基础设施    | 后端        | Sprint 1           | BLK-02，预实现   |
| 数据权限测试支持      | 后端        | Sprint 1           | BLK-03，预实现   |
| CustomerFactory 扩展  | QA          | Sprint 1           | 支持业务字段     |
| UserFactory 扩展      | QA          | Sprint 1           | 支持 4 角色      |
| P0 测试实现           | QA          | Sprint 2           | 权限认证、安全   |
| P1 测试实现           | QA          | Sprint 3-4         | 重要功能、集成   |
| 性能基准测试          | QA + 架构师 | Sprint 1           | pytest-benchmark |
| 契约测试框架          | QA          | Sprint 2           | Pact.io          |
| CI/CD 配置            | DevOps      | Sprint 1           | 并行测试支持     |
| 性能测试环境          | DevOps      | Sprint 1           | k6 环境          |

---

## Tooling & Access

**仅当需要非标准工具或访问请求时包含。**

| 工具或服务           | 目的              | 需要的访问       | 状态       |
| -------------------- | ----------------- | ---------------- | ---------- |
| **pytest**           | 后端 API 测试     | 已安装           | ✅ Ready   |
| **pytest-asyncio**   | 异步测试支持      | 已安装           | ✅ Ready   |
| **pytest-httpx**     | HTTP 请求 mock    | 需要安装         | ⏳ Pending |
| **pytest-benchmark** | 性能基准测试      | 需要安装         | ⏳ Pending |
| **playwright**       | E2E 测试          | 已安装           | ✅ Ready   |
| **vitest**           | 单元测试          | 已安装           | ✅ Ready   |
| **k6**               | 性能测试          | 需要安装         | ⏳ Pending |
| **Pact.io**          | 契约测试          | 需要安装         | ⏳ Pending |
| **Docker Compose**   | 测试环境          | 已安装           | ✅ Ready   |
| **Redis**            | 缓存/任务队列测试 | 需要 Docker 配置 | ⏳ Pending |

**需要的访问请求:**

- [ ] pytest-httpx 安装 (`pip install pytest-httpx`)
- [ ] pytest-benchmark 安装 (`pip install pytest-benchmark`)
- [ ] k6 安装（参考 https://k6.io/docs）
- [ ] Pact.io 安装 (`npm install --save-dev @pact-foundation/pact`)
- [ ] Redis Docker 容器配置

---

## Interworking & Regression

**受此功能影响的服务和组件:**

| 服务/组件        | 影响方式        | 回归测试范围              | 验证步骤                            |
| ---------------- | --------------- | ------------------------- | ----------------------------------- |
| **客户管理模块** | 核心 CRUD 变更  | 现有客户 API 测试必须通过 | 运行 `tests/api/customer/` 所有测试 |
| **权限系统**     | 新角色/数据权限 | 所有 API 权限测试必须通过 | 运行 4 角色×所有 API 测试矩阵       |
| **健康度监控**   | 定时任务触发    | 健康度更新、预警推送测试  | 手动触发接口测试 + 定时任务测试     |
| **结算管理**     | Celery 异步任务 | 结算生成、发送测试        | 任务失败重试、幂等性测试            |
| **价值评估**     | 定级规则重算    | 定级规则变更测试          | 规则边界、重算准确性测试            |
| **前端 UI**      | 页面交互流程    | 核心 E2E 流程测试         | 创建/编辑/删除/导入 E2E 流程        |

**回归测试策略:**

- **每次 PR**: 运行所有 P0+P1 测试（~75 个，~10 分钟）
- **每日夜间**: 运行所有 P0+P1+P2 测试（~115 个，~20 分钟）
- **每周**: 运行完整测试套件（~160 个，~30 分钟）+ 性能测试
- **发布前**: 完整回归测试 + 性能基准测试 + 混沌工程测试

**跨团队协调:**

- **后端团队**: 确保 API 向后兼容，破坏性变更提前通知 QA
- **前端团队**: 确保 data-testid 稳定性，UI 变更更新页面对象
- **DevOps**: 确保测试环境稳定性，CI 配置更新

---

## Appendix A: Code Examples & Tagging

**Playwright 标签用于选择性执行:**

```python
# 后端 API 测试示例 (pytest)
# tests/api/auth/test_login.py
import pytest
from httpx import AsyncClient


class TestLoginAPI:
    """登录认证 API 测试"""

    @pytest.mark.asyncio
    @pytest.mark.P0
    @pytest.mark.security
    async def test_login_success(self, app, db_session, user_factory):
        """
        测试登录成功

        Given: 有效用户名密码
        When: 发送 POST 请求到 /api/v1/auth/login
        Then: 返回 JWT Token 和用户信息
        """
        # Given
        user = await user_factory.create_in_db(db_session, {
            "email": "test@example.com",
            "password": "Test123456!",
            "role": "operator",
        })

        # When
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "Test123456!",
                },
            )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    @pytest.mark.P0
    @pytest.mark.security
    async def test_login_invalid_password(self, app, db_session, user_factory):
        """
        测试密码错误

        Given: 无效密码
        When: 发送 POST 请求登录
        Then: 返回 401 错误
        """
        # Given
        await user_factory.create_in_db(db_session, {
            "email": "test@example.com",
            "password": "Test123456!",
        })

        # When
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "WrongPassword!",
                },
            )

        # Then
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "密码错误" in data["error"]

    @pytest.mark.asyncio
    @pytest.mark.P0
    @pytest.mark.security
    async def test_login_unauthorized_access(self, app):
        """
        测试未授权访问

        Given: 无 Token
        When: 访问受保护的 API
        Then: 返回 401 错误
        """
        # When
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/customers")

        # Then
        assert response.status_code == 401
```

```typescript
// 前端 E2E 测试示例 (Playwright)
// tests/e2e/auth/login.spec.ts
import { test, expect } from "@playwright/test";

test.describe("登录认证 E2E 测试", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test("@P0 @Security 应该成功登录", async ({ page }) => {
    // Given: 访问登录页面
    await expect(page).toHaveURL(/\/login/);

    // When: 输入有效用户名密码
    await page.fill('[data-testid="email-input"]', "admin@example.com");
    await page.fill('[data-testid="password-input"]', "Admin123456!");

    // When: 点击登录按钮
    await page.click('[data-testid="login-button"]');

    // Then: 应该跳转到首页
    await expect(page).toHaveURL(/\/dashboard/);

    // Then: 应该显示欢迎消息
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });

  test("@P0 @Security 密码错误应该显示错误提示", async ({ page }) => {
    // Given: 访问登录页面

    // When: 输入错误密码
    await page.fill('[data-testid="email-input"]', "admin@example.com");
    await page.fill('[data-testid="password-input"]', "WrongPassword!");

    // When: 点击登录按钮
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示错误提示
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText(
      "密码错误",
    );

    // Then: 应该停留在登录页
    await expect(page).toHaveURL(/\/login/);
  });

  test("@P0 @Security 未授权访问应该跳转到登录页", async ({ page }) => {
    // Given: 未登录状态

    // When: 直接访问受保护的页面
    await page.goto("/customers");

    // Then: 应该重定向到登录页
    await expect(page).toHaveURL(/\/login/);
  });
});
```

**运行特定标签:**

```bash
# 仅运行 P0 测试
npx playwright test --grep @P0
pytest -m "P0"

# 仅运行 P0+P1 测试
npx playwright test --grep "@P0|@P1"
pytest -m "P0 or P1"

# 仅运行安全测试
npx playwright test --grep @Security
pytest -m "security"

# 仅运行 API 测试
npx playwright test --grep @API
pytest tests/api/

# 仅运行 E2E 测试
npx playwright test --grep @E2E
pytest tests/e2e/

# 运行所有 Playwright 测试（默认）
npx playwright test
pytest
```

---

## Appendix B: Knowledge Base References

- **Risk Governance**: `risk-governance.md` - 风险评分方法论
- **Test Priorities Matrix**: `test-priorities-matrix.md` - P0-P3 标准
- **Test Levels Framework**: `test-levels-framework.md` - E2E vs API vs Unit 选择
- **Test Quality**: `test-quality.md` - 完成定义（无硬等待、<300 行、<1.5 分钟）

---

**Generated by:** BMad TEA Agent  
**Workflow:** `_bmad/tea/testarch/test-design`  
**Version:** 4.0 (BMad v6)
