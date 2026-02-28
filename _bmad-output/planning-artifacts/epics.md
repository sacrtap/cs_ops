---
stepsCompleted: ["step-01-validate-prerequisites"]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
---

# cs_ops - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for cs_ops（内部运营中台客户信息管理与运营系统）, decomposing the requirements from the PRD, UX Design, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**客户主数据管理 (FR1-8):**
- FR1: 客户列表分页展示、基础搜索、状态筛选
- FR2: 客户详情完整信息展示、编辑、历史记录
- FR3: 客户新增手工录入、必填项验证
- FR4: 批量导入 Excel、数据验证、错误处理
- FR5: 批量导出 Excel、自定义字段
- FR6: 客户搜索功能
- FR7: 客户状态管理 (active/risk/zombie)
- FR8: 客户数据完整性验证

**健康度监控 (FR9-16):**
- FR9: 健康度仪表盘实时展示 (总数/活跃/风险/僵尸)
- FR10: 僵尸账号自动识别 (90 天未使用)
- FR11: 风险客户预警 (7 天未使用)
- FR12: 预警推送系统 (系统内通知 + 邮件)
- FR13: 客户健康状态自动更新
- FR14: 风险评分计算
- FR15: 预警历史记录
- FR16: 健康度趋势分析

**价值评估 (FR17-22):**
- FR17: 价值等级显示 (S/A/B/C/D 五级)
- FR18: 定级规则配置 (配置文件管理阈值)
- FR19: 人工定级维护 (手动调整等级)
- FR20: 定级历史记录 (变更记录可追溯)
- FR21: 等级重算功能
- FR22: 定级规则立即生效

**结算管理 (FR23-32):**
- FR23: 结算单自动生成 (选择月份→一键生成)
- FR24: 自动关联用量数据和价格
- FR25: 自动计算结算金额
- FR26: 异常数据自动检测 (0 用量/用量突增/价格缺失)
- FR27: 异常数据处理确认
- FR28: 结算单导出 (PDF/Excel)
- FR29: 批量发送结算单 (邮件群发)
- FR30: 发送日志记录
- FR31: 结算历史查询
- FR32: 结算单审核流程

**权限与认证 (FR33-40):**
- FR33: 用户认证 (用户名密码登录)
- FR34: JWT Token 管理
- FR35: 权限管理 (4 级：Admin/经理/专员/销售)
- FR36: 数据权限 (销售仅看自己客户)
- FR37: 功能权限 (权限矩阵控制)
- FR38: 角色管理
- FR39: 权限继承
- FR40: 权限审计

**操作日志 (FR41-46):**
- FR41: 关键操作记录 (增删改/转移/导出)
- FR42: 操作人记录
- FR43: 操作时间记录
- FR44: 操作 IP 记录
- FR45: 操作详情记录
- FR46: 日志查询功能

**客户转移 (FR47-53):**
- FR47: 客户转移操作 (转出/转入销售选择)
- FR48: 转移原因记录
- FR49: 转移历史生成
- FR50: 转移单号生成
- FR51: 自动通知 (邮件发送相关人员)
- FR52: 转移统计
- FR53: 批量转移支持

**数据分析与报告 (FR54-58):**
- FR54: 运营周报一键生成
- FR55: 报告导出 (PDF)
- FR56: 基础筛选 (按价值等级/行业/状态/销售)
- FR57: 数据可视化 (图表展示)
- FR58: 自定义日期范围查询

### NonFunctional Requirements

**性能 (NFR1-5):**
- NFR1: 关键查询响应时间<1 秒 (客户列表/详情)
- NFR2: 复杂查询响应时间<5 秒 (统计分析)
- NFR3: 数据导入速度≥1000 条/分钟
- NFR4: 系统并发支持≥50 用户同时在线
- NFR5: 首屏加载时间<3 秒

**可靠性 (NFR6-10):**
- NFR6: 系统可用性≥99.5%(工作日 9:00-18:00)
- NFR7: 数据准确性≥99.9%
- NFR8: 数据备份每日自动备份 100% 可恢复
- NFR9: 故障恢复时间 (MTTR)<2 小时
- NFR10: 数据迁移完整性≥99%

**安全 (NFR11-16):**
- NFR11: JWT+RBAC 权限控制
- NFR12: 数据权限隔离 (销售仅查看自己客户)
- NFR13: 操作日志 100% 关键操作可追溯
- NFR14: 敏感信息加密存储 (联系方式等)
- NFR15: SQL 注入防护 (参数化查询)
- NFR16: XSS 防护 (输入过滤/输出编码)

**可用性 (NFR17-20):**
- NFR17: 响应式设计 (支持桌面/平板/手机)
- NFR18: 基础可访问性 (键盘导航/语义化 HTML)
- NFR19: 浏览器支持 (Chrome 90+/Edge 90+/Safari 14+)
- NFR20: 移动端适配 (销售手机访问)

**技术约束 (NFR21-25):**
- NFR21: Python 3.11+ 后端
- NFR22: Sanic 异步 Web 框架
- NFR23: SQLAlchemy 2.0 ORM
- NFR24: Vue 3+TypeScript+Arco Design 前端
- NFR25: PostgreSQL 18 数据库 (UTF-8)

### Additional Requirements

**来自 Architecture 的技术要求:**
- 后端采用 Sanic 异步框架，使用 Blueprints 组织路由
- ORM 使用 SQLAlchemy 2.0，采用异步模式
- 数据库使用 PostgreSQL 18，UTF-8 编码
- API 采用 RESTful 风格，版本控制 v1
- 认证采用 JWT Token，有效期可配置
- 日志采用结构化日志，支持 ELK 收集
- Docker 容器化部署，支持 Docker Compose

**来自 UX Design 的交互要求:**
- 全局搜索功能，支持姓名/电话/公司模糊匹配，响应<500ms
- 智能筛选，支持我的客户/高价值/风险/僵尸一键切换
- 客户 360 度视图，采用 4 个标签页（基础/用量/结算/跟进）
- 移动端一键拨号功能（`<a href="tel:">`）
- 批量操作进度可视化，显示百分比和剩余时间
- 异常数据主动检测和高亮提示（警告橙/危险红）
- 键盘快捷键支持（`/` 键聚焦搜索框，Ctrl+S 保存）
- 响应式设计，支持桌面端 (1920px→1366px) 和移动端 (375px→768px)

### FR Coverage Map

| FR 编号 | 覆盖的史诗 | 覆盖的故事 |
|---------|-----------|-----------|
| FR33-40 | Epic 1: 权限与认证 | Story 1.1-1.8 |
| FR1-8 | Epic 2: 客户主数据管理 | Story 2.1-2.8 |
| FR9-16 | Epic 3: 客户健康度监控 | Story 3.1-3.8 |
| FR17-22 | Epic 4: 客户价值评估 | Story 4.1-4.6 |
| FR23-32 | Epic 5: 结算管理 | Story 5.1-5.10 |
| FR41-46 | Epic 6: 操作日志 | Story 6.1-6.6 |
| FR47-53 | Epic 7: 客户转移 | Story 7.1-7.7 |
| FR54-58 | Epic 8: 数据分析与报告 | Story 8.1-8.5 |

## Epic List

**实施顺序（已修复重复问题）：**

1. **Epic 1: 权限与认证** - 实现用户认证、JWT 管理、4 级权限控制（基础设施）
2. **Epic 2: 客户主数据管理** - 实现客户信息的完整 CRUD 操作，支持批量导入导出
3. **Epic 3: 客户健康度监控** - 实现健康度仪表盘、僵尸账号识别、风险预警
4. **Epic 4: 客户价值评估** - 实现价值等级定级、规则配置、人工维护
5. **Epic 5: 结算管理** - 实现结算单自动生成、异常检测、批量发送
6. **Epic 6: 操作日志** - 实现关键操作记录、日志查询、审计功能
7. **Epic 7: 客户转移** - 实现客户转移流程、历史记录、通知机制
8. **Epic 8: 数据分析与报告** - 实现运营报告生成、数据可视化、自定义查询

**依赖关系说明：**
- Epic 1（权限）是所有其他史诗的基础设施
- Epic 2（客户数据）是核心数据源，被 Epic 3/4/5/7/8 依赖
- Epic 5（结算管理）依赖 Epic 2 和 Epic 4
- Epic 8（数据分析）依赖所有业务数据

---

## Epic 1: 权限与认证

**目标：** 实现用户认证、JWT 管理、4 级权限控制（Admin/经理/专员/销售），确保数据安全和权限隔离。

### Story 1.1: 用户认证

As a 用户，
I want 用户名密码登录，
So that 安全访问系统.

**Acceptance Criteria:**

**Given** 用户访问系统
**When** 输入用户名和密码
**Then** 验证凭据
**And** 成功后生成 JWT Token

### Story 1.2: JWT Token 管理

As a 系统，
I want 管理 JWT Token（生成/验证/刷新/失效）,
So that 维护会话安全.

**Acceptance Criteria:**

**Given** 用户登录成功
**When** 访问受保护 API
**Then** 验证 JWT Token 有效性
**And** Token 过期前自动刷新

### Story 1.3: 权限管理

As a Admin,
I want 管理 4 级权限（Admin/经理/专员/销售）,
So that 控制功能访问.

**Acceptance Criteria:**

**Given** Admin 进入权限管理页面
**When** 分配用户角色
**Then** 保存角色到用户表
**And** 权限立即生效

### Story 1.4: 数据权限

As a 销售，
I want 仅查看自己负责的客户，
So that 符合数据权限要求.

**Acceptance Criteria:**

**Given** 销售用户登录系统
**When** 访问客户列表或 API
**Then** 自动过滤仅显示自己负责的客户
**And** 无"查看全部客户"菜单入口

### Story 1.5: 功能权限

As a Admin,
I want 权限矩阵控制功能访问，
So that 精细化权限管理.

**Acceptance Criteria:**

**Given** 用户访问某个功能
**When** 检查权限矩阵
**Then** 有权限则显示功能，无权限则隐藏
**And** 后端 API 同时验证权限

### Story 1.6: 角色管理

As a Admin,
I want 管理角色和权限映射，
So that 灵活配置权限.

**Acceptance Criteria:**

**Given** Admin 进入角色管理页面
**When** 修改角色权限
**Then** 保存权限矩阵
**And** 该角色所有用户权限同步更新

### Story 1.7: 权限继承

As a 系统，
I want 实现权限继承（经理继承专员权限）,
So that 简化权限配置.

**Acceptance Criteria:**

**Given** 角色层级定义
**When** 分配用户角色
**Then** 自动继承下级角色权限
**And** 支持额外授权

### Story 1.8: 权限审计

As a Admin,
I want 查看权限使用日志，
So that 审计权限合规性.

**Acceptance Criteria:**

**Given** Admin 进入权限审计页面
**When** 选择用户/日期范围
**Then** 显示权限使用记录
**And** 标记异常访问

---

## Epic 2: 客户主数据管理

**目标：** 实现客户信息的完整 CRUD 操作，支持批量导入导出，管理 1320 个客户的基础数据。

### Story 2.1: 客户列表展示

As a 销售/运营，
I want 查看客户列表（分页、搜索、筛选）,
So that 快速找到目标客户.

**Acceptance Criteria:**

**Given** 用户进入客户列表页
**When** 页面加载完成
**Then** 显示分页客户列表（默认 20 条/页）
**And** 支持按状态（active/risk/zombie）筛选

### Story 2.2: 客户详情查看

As a 销售/运营，
I want 查看客户 360 度视图，包含基础信息/用量/结算/跟进 4 个标签页，
So that 全面了解客户情况.

**Acceptance Criteria:**

**Given** 用户点击客户列表中的某个客户
**When** 进入客户详情页
**Then** 显示 4 个标签页（基础/用量/结算/跟进）
**And** 默认显示基础信息标签页

### Story 2.3: 客户新增

As a 运营专员，
I want 手工录入新客户信息，必填项验证，
So that 将新客户添加到系统中.

**Acceptance Criteria:**

**Given** 用户点击"新增客户"按钮
**When** 填写客户信息表单并提交
**Then** 验证必填项（姓名、电话、公司、行业）
**And** 保存成功后跳转到客户详情页

### Story 2.4: 批量导入客户

As a 运营专员，
I want 批量导入 Excel 客户数据，支持数据验证和错误处理，
So that 快速将 Excel 中的 1320 个客户迁移到系统中.

**Acceptance Criteria:**

**Given** 用户上传 Excel 文件
**When** 点击"开始导入"
**Then** 逐行验证数据格式和必填项
**And** 显示导入进度和错误行定位

### Story 2.5: 批量导出客户

As a 运营经理，
I want 批量导出客户数据为 Excel，支持自定义字段，
So that 用于线下分析或汇报.

**Acceptance Criteria:**

**Given** 用户选择要导出的客户（支持全选）
**When** 点击"导出 Excel"
**Then** 生成 Excel 文件，包含选中的字段
**And** 显示导出进度和下载链接

### Story 2.6: 客户搜索

As a 销售/运营，
I want 全局搜索客户（姓名/电话/公司模糊匹配）,
So that 在 30 秒内找到目标客户.

**Acceptance Criteria:**

**Given** 用户在搜索框输入关键词
**When** 输入完成后 300ms（防抖）
**Then** 实时显示匹配的搜索结果
**And** 关键字段高亮显示

### Story 2.7: 客户状态管理

As a 运营经理，
I want 管理客户状态（active/risk/zombie）,
So that 标识客户健康程度.

**Acceptance Criteria:**

**Given** 系统根据 90 天未使用自动标记僵尸账号
**When** 运营经理手动调整状态
**Then** 记录状态变更原因和操作日志
**And** 状态立即生效并在列表页显示

### Story 2.8: 客户数据完整性验证

As a 系统，
I want 验证客户数据的完整性（必填项/格式/唯一性）,
So that 保证数据质量.

**Acceptance Criteria:**

**Given** 用户新增或编辑客户
**When** 提交表单
**Then** 验证必填项、电话格式、邮箱格式、公司唯一性
**And** 错误提示定位到具体字段

---

## Epic 3: 客户健康度监控

**目标：** 实现健康度仪表盘、僵尸账号自动识别、风险客户预警，帮助运营团队主动发现并处理客户流失风险。

### Story 3.1: 健康度仪表盘

As a 运营经理，
I want 查看健康度仪表盘，显示总数/活跃/风险/僵尸客户数量和占比，
So that 快速了解客户整体健康状况.

**Acceptance Criteria:**

**Given** 用户打开运营仪表盘
**When** 页面加载完成
**Then** 显示 4 个指标卡片（客户总数、活跃客户、风险客户、僵尸客户）
**And** 异常指标用颜色标记（风险橙色、僵尸红色）

### Story 3.2: 僵尸账号自动识别

As a 系统，
I want 自动识别 90 天未使用的僵尸账号，
So that 运营团队及时处理.

**Acceptance Criteria:**

**Given** 系统每日凌晨执行健康度检查
**When** 发现客户 90 天未使用
**Then** 自动标记为僵尸状态
**And** 记录到僵尸客户列表

### Story 3.3: 风险客户预警

As a 系统，
I want 自动识别 7 天未使用的风险客户，
So that 提前干预防止流失.

**Acceptance Criteria:**

**Given** 系统每日凌晨执行健康度检查
**When** 发现客户 7 天未使用
**Then** 自动标记为风险状态
**And** 生成预警记录

### Story 3.4: 预警推送系统

As a 运营经理，
I want 接收预警推送（系统内通知 + 邮件）,
So that 及时处理风险客户.

**Acceptance Criteria:**

**Given** 系统生成预警记录
**When** 预警级别为高（S/A 级客户）
**Then** 发送系统内通知给运营经理
**And** 发送邮件给负责销售

### Story 3.5: 客户健康状态自动更新

As a 系统，
I want 每日自动更新客户健康状态，
So that 数据保持最新.

**Acceptance Criteria:**

**Given** 系统每日凌晨 2 点执行定时任务
**When** 扫描所有活跃客户
**Then** 根据最后使用时间更新状态
**And** 记录健康状态变更日志

### Story 3.6: 风险评分计算

As a 系统，
I want 计算客户风险评分（0-100 分）,
So that 量化风险程度.

**Acceptance Criteria:**

**Given** 系统执行健康度检查
**When** 计算风险评分（基于使用频率、消费趋势、投诉记录）
**Then** 评分>80 分为高风险，50-80 为中风险，<50 为低风险
**And** 评分显示在客户详情页

### Story 3.7: 预警历史记录

As a 运营经理，
I want 查看预警历史记录，
So that 追踪预警处理情况.

**Acceptance Criteria:**

**Given** 用户进入预警历史页面
**When** 选择日期范围
**Then** 显示该时间段内所有预警记录
**And** 支持按级别/状态/负责人筛选

### Story 3.8: 健康度趋势分析

As a 运营经理，
I want 查看健康度趋势图表（近 12 个月）,
So that 分析客户健康变化趋势.

**Acceptance Criteria:**

**Given** 用户打开健康度趋势图表
**When** 选择时间范围（近 12 个月/近 6 个月/近 3 个月）
**Then** 显示活跃/风险/僵尸客户数量趋势线
**And** 支持导出数据

---

## Epic 4: 客户价值评估

**目标：** 实现客户价值等级定级（S/A/B/C/D 五级）、规则配置、人工维护，支持精细化运营和资源倾斜。

### Story 4.1: 价值等级显示

As a 销售/运营，
I want 查看客户价值等级（S/A/B/C/D 五级）,
So that 了解客户重要程度.

**Acceptance Criteria:**

**Given** 用户查看客户列表或详情页
**When** 客户价值等级已计算
**Then** 显示等级标签（S 级红色/A 级橙色/B 级蓝色/C 级绿色/D 级灰色）
**And** 鼠标悬停显示等级规则说明

### Story 4.2: 定级规则配置

As a 运营经理，
I want 配置价值等级定级规则（阈值配置文件管理）,
So that 根据业务需要调整定级标准.

**Acceptance Criteria:**

**Given** 运营经理进入定级规则配置页面
**When** 修改 S/A/B/C/D 级阈值
**Then** 实时预览影响客户数量
**And** 确认后保存规则到配置文件

### Story 4.3: 人工定级维护

As a 运营经理，
I want 手动调整客户价值等级，
So that 处理特殊情况.

**Acceptance Criteria:**

**Given** 运营经理在客户详情页点击"调整等级"
**When** 选择新等级并填写原因
**Then** 保存人工调整记录
**And** 等级立即生效

### Story 4.4: 定级历史记录

As a 运营经理，
I want 查看客户定级历史记录，
So that 追溯等级变更原因.

**Acceptance Criteria:**

**Given** 用户进入客户详情页的"历史"标签页
**When** 查看定级历史
**Then** 显示所有等级变更记录（时间、原等级、新等级、原因、操作人）
**And** 支持导出历史记录

### Story 4.5: 等级重算功能

As a 运营经理，
I want 手动触发等级重算，
So that 定级规则变更后立即生效.

**Acceptance Criteria:**

**Given** 运营经理修改定级规则
**When** 点击"立即重算"
**Then** 系统重算所有 1320 个客户的等级
**And** 显示重算结果对比（调整前 vs 调整后）

### Story 4.6: 定级规则立即生效

As a 系统，
I want 定级规则变更后立即生效，
So that 新规则影响所有相关客户.

**Acceptance Criteria:**

**Given** 运营经理确认保存新规则
**When** 规则写入配置文件
**Then** 新查询立即使用新规则
**And** 缓存同步更新

---

## Epic 5: 结算管理

**目标：** 实现结算单自动生成、异常检测、批量发送，将月度结算时间从 3 天缩短到 2 小时。

### Story 5.1: 结算单自动生成

As a 运营专员，
I want 选择月份后一键生成结算单，
So that 告别手工计算.

**Acceptance Criteria:**

**Given** 用户进入结算管理页面
**When** 选择结算月份（如 2026 年 4 月）并点击"开始生成"
**Then** 系统自动筛选应结算客户
**And** 生成结算单草稿

### Story 5.2: 自动关联用量数据和价格

As a 系统，
I want 自动关联客户用量数据和价格，
So that 计算结算金额.

**Acceptance Criteria:**

**Given** 系统生成结算单
**When** 读取客户用量数据和定价套餐
**Then** 关联用量×价格计算金额
**And** 处理缺失数据（标记为异常）

### Story 5.3: 自动计算结算金额

As a 系统，
I want 自动计算结算金额（用量×单价）,
So that 避免手工计算错误.

**Acceptance Criteria:**

**Given** 系统已关联用量和价格
**When** 执行金额计算
**Then** 按定价公式计算
**And** 保留 2 位小数

### Story 5.4: 异常数据自动检测

As a 系统，
I want 自动检测异常数据（0 用量/用量突增/价格缺失）,
So that 运营专员及时核实.

**Acceptance Criteria:**

**Given** 系统生成结算单
**When** 检测到 0 用量/用量突增>200%/价格缺失
**Then** 标记为异常并高亮显示
**And** 生成异常列表待确认

### Story 5.5: 异常数据处理确认

As a 运营专员，
I want 确认处理异常数据，
So that 结算单准确无误.

**Acceptance Criteria:**

**Given** 系统显示异常列表
**When** 运营专员逐个确认或修正
**Then** 记录处理方式（标记免结算/手动输入/跳过）
**And** 所有异常处理完成后才能生成正式结算单

### Story 5.6: 结算单导出

As a 运营专员，
I want 导出结算单为 PDF/Excel,
So that 发送给客户或财务.

**Acceptance Criteria:**

**Given** 用户选择要导出的结算单
**When** 点击"导出 PDF"或"导出 Excel"
**Then** 生成格式化文件
**And** 提供下载链接

### Story 5.7: 批量发送结算单

As a 运营专员，
I want 批量发送邮件发送结算单，
So that 快速通知所有客户.

**Acceptance Criteria:**

**Given** 用户选择要发送的结算单
**When** 点击"批量发送"
**Then** 逐封发送邮件
**And** 显示发送进度（XX/YY，百分比）

### Story 5.8: 发送日志记录

As a 系统，
I want 记录发送日志（成功/失败/时间）,
So that 追踪发送状态.

**Acceptance Criteria:**

**Given** 系统发送邮件
**When** 发送完成或失败
**Then** 记录发送结果（成功/失败原因/时间）
**And** 支持在结算单列表查看发送状态

### Story 5.9: 结算历史查询

As a 运营专员，
I want 查询历史结算单，
So that 处理客户咨询.

**Acceptance Criteria:**

**Given** 用户进入结算历史页面
**When** 选择客户/日期范围/状态筛选
**Then** 显示匹配的结算单列表
**And** 支持查看详情和重新发送

### Story 5.10: 结算单审核流程

As a 运营经理，
I want 审核结算单后发送，
So that 确保准确性.

**Acceptance Criteria:**

**Given** 运营专员生成结算单草稿
**When** 提交审核
**Then** 运营经理查看草稿并确认
**And** 审核通过后才能批量发送

---

## Epic 6: 操作日志

**目标：** 实现关键操作记录、日志查询、审计功能，满足合规要求和数据追溯需求。

### Story 6.1: 关键操作记录

As a 系统，
I want 记录关键操作（增删改/转移/导出）,
So that 操作可追溯.

**Acceptance Criteria:**

**Given** 用户执行关键操作
**When** 操作完成
**Then** 记录操作类型、对象、结果
**And** 写入操作日志表

### Story 6.2: 操作人记录

As a 系统，
I want 记录操作人信息，
So that 责任可追溯.

**Acceptance Criteria:**

**Given** 用户执行操作
**When** 记录日志
**Then** 记录操作人 ID、姓名、角色
**And** 关联用户会话

### Story 6.3: 操作时间记录

As a 系统，
I want 记录操作时间（精确到秒）,
So that 时间可追溯.

**Acceptance Criteria:**

**Given** 用户执行操作
**When** 记录日志
**Then** 记录操作时间戳（UTC+8）
**And** 格式：YYYY-MM-DD HH:mm:ss

### Story 6.4: 操作 IP 记录

As a 系统，
I want 记录操作 IP 地址，
So that 安全审计.

**Acceptance Criteria:**

**Given** 用户执行操作
**When** 记录日志
**Then** 记录客户端 IP 地址
**And** 支持 IP 归属地查询

### Story 6.5: 操作详情记录

As a 系统，
I want 记录操作详情（变更前后对比）,
So that 完整追溯变更.

**Acceptance Criteria:**

**Given** 用户执行编辑操作
**When** 记录日志
**Then** 记录变更字段（原值→新值）
**And** 支持 JSON 格式存储

### Story 6.6: 日志查询功能

As a Admin,
I want 查询操作日志，
So that 审计和排查问题.

**Acceptance Criteria:**

**Given** Admin 进入日志查询页面
**When** 选择操作人/操作类型/日期范围
**Then** 显示匹配的日志列表
**And** 支持导出日志

---

## Epic 7: 客户转移

**目标：** 实现客户转移流程、历史记录、通知机制，支持销售离职/轮岗时的客户交接。

### Story 7.1: 客户转移操作

As a 运营经理，
I want 转移客户（选择转出/转入销售）,
So that 调整客户分配.

**Acceptance Criteria:**

**Given** 运营经理选择要转移的客户
**When** 选择转入销售并确认
**Then** 更新客户负责人字段
**And** 生成转移记录

### Story 7.2: 转移原因记录

As a 运营经理，
I want 记录转移原因，
So that 追溯转移背景.

**Acceptance Criteria:**

**Given** 运营经理执行转移
**When** 填写转移原因（必填）
**Then** 保存原因到转移记录
**And** 支持预设原因选项

### Story 7.3: 转移历史生成

As a 系统，
I want 生成客户转移历史，
So that 查看完整流转记录.

**Acceptance Criteria:**

**Given** 客户发生转移
**When** 查看客户详情页的"历史"标签页
**Then** 显示所有转移记录（时间、转出、转入、原因）
**And** 按时间倒序排列

### Story 7.4: 转移单号生成

As a 系统，
I want 生成转移单号，
So that 唯一标识每次转移.

**Acceptance Criteria:**

**Given** 客户转移发生
**When** 保存转移记录
**Then** 生成唯一转移单号（TRF-YYYYMMDD-序号）
**And** 单号不可重复

### Story 7.5: 自动通知

As a 系统，
I want 自动发送邮件通知相关人员，
So that 转出/转入销售知晓变更.

**Acceptance Criteria:**

**Given** 客户转移完成
**When** 保存转移记录
**Then** 发送邮件给转出销售和转入销售
**And** 邮件包含转移详情和新负责人联系方式

### Story 7.6: 转移统计

As a 运营经理，
I want 查看客户转移统计，
So that 分析客户流动情况.

**Acceptance Criteria:**

**Given** 运营经理进入转移统计页面
**When** 选择日期范围
**Then** 显示转移数量、转出/转入销售排名
**And** 支持导出统计报表

### Story 7.7: 批量转移支持

As a 运营经理，
I want 批量转移客户，
So that 销售离职时快速交接.

**Acceptance Criteria:**

**Given** 运营经理选择多个客户
**When** 点击"批量转移"并选择转入销售
**Then** 逐个转移客户
**And** 显示转移进度和结果报告

---

## Epic 8: 数据分析与报告

**目标：** 实现运营报告一键生成、数据可视化、自定义查询，支持数据驱动决策。

### Story 8.1: 运营周报一键生成

As a 运营经理，
I want 一键生成运营周报，
So that 快速向总监汇报.

**Acceptance Criteria:**

**Given** 用户进入报告生成页面
**When** 选择报告类型（周报/月报）和日期范围
**Then** 自动生成报告（客户概况/健康度/价值分布/结算汇总）
**And** 10 秒内完成生成

### Story 8.2: 报告导出

As a 运营经理，
I want 导出报告为 PDF,
So that 发送给管理层.

**Acceptance Criteria:**

**Given** 报告生成完成
**When** 点击"导出 PDF"
**Then** 生成格式化 PDF 文件
**And** 包含公司 Logo 和美观排版

### Story 8.3: 基础筛选

As a 用户，
I want 按价值等级/行业/状态/销售筛选数据，
So that 分析特定客户群体.

**Acceptance Criteria:**

**Given** 用户查看数据列表
**When** 选择筛选条件
**Then** 实时过滤数据
**And** 显示筛选结果数量

### Story 8.4: 数据可视化

As a 运营经理，
I want 查看数据图表（柱状图/折线图/饼图）,
So that 直观理解数据趋势.

**Acceptance Criteria:**

**Given** 用户打开数据分析页面
**When** 选择图表类型和数据维度
**Then** 渲染交互式图表
**And** 支持鼠标悬停查看详情

### Story 8.5: 自定义日期范围查询

As a 用户，
I want 自定义日期范围查询，
So that 分析特定时间段数据.

**Acceptance Criteria:**

**Given** 用户查看数据列表或图表
**When** 选择自定义日期范围
**Then** 过滤该时间段内数据
**And** 支持快捷选项（今天/本周/本月/近 30 天）

---

## Change Log

**2026-02-27** - 修复 Epic 重复问题
- 移除重复的 Epic 5（权限与认证）
- 原 Epic 5 的权限内容合并到 Epic 1
- 原 Epic 1 的客户主数据内容重编号为 Epic 2
- 后续史诗依次重编号（原 Epic 2-8 → Epic 3-8）
- 总计：8 个史诗，58 个用户故事
