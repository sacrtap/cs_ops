# AGENTS.md - BMAD-CMS 项目指南

_为在 BMAD-CMS 仓库中工作的 AI 编码代理的完整指南_

---

## 项目概述

这是一个 **BMAD（Business Method for AI Development）** 项目，实现了基于工作流的 AI 代理系统，用于软件开发的全生命周期管理。项目采用模块化架构，包含 21 个专用代理和 56 个工作流命令。

**技术栈**：
- **核心框架**: BMAD 6.0.3（内置 core + bmm 模块）
- **外部模块**: bmb 0.1.6, cis 0.1.8, tea 1.2.6
- **IDE**: Opencode（配置在 `.opencode/` 目录）
- **输出目录**: `_bmad-output/`

---

## 交互要求

- **Thinking**: 思考过程用**中文**表述
- **Reply**: 回答用**中文**回复
- **文档**: 所有生成的文档必须使用中文（除关键代码或术语外），且必须符合**中文语法规范**
- **技术查询**: 使用 **context7** 进行所有代码生成和 API 文档查询

---

## 构建/运行/测试命令

### Opencode IDE 命令（56 个可用命令）

**核心命令**（始终可用）：
```bash
/bmad-help                           # 获取工作流指导
bmad-brainstorming                   # 交互式头脑风暴
bmad-party-mode                      # 多代理讨论模式
```

**BMM - 业务管理模块**：
```bash
# 需求分析
bmad-bmm-create-product-brief        # 创建产品简报
bmad-bmm-domain-research             # 领域研究
bmad-bmm-technical-research          # 技术研究
bmad-bmm-market-research             # 市场研究

# 规划
bmad-bmm-create-prd                  # 创建 PRD
bmad-bmm-edit-prd                    # 编辑 PRD
bmad-bmm-validate-prd                # 验证 PRD
bmad-bmm-create-epics-and-stories    # 创建史诗和用户故事
bmad-bmm-create-story                # 创建单个用户故事
bmad-bmm-dev-story                   # 开发用户故事

# 架构与设计
bmad-bmm-create-architecture         # 创建架构设计
bmad-bmm-create-ux-design            # 创建 UX 设计
bmad-bmm-code-review                 # 代码审查

# 敏捷开发
bmad-bmm-sprint-planning             # 冲刺规划
bmad-bmm-sprint-status               # 冲刺状态
bmad-bmm-retrospective               # 回顾会议
bmad-bmm-correct-course              # 纠偏
bmad-bmm-check-implementation-readiness  # 检查实现就绪性

# 文档与上下文
bmad-bmm-generate-project-context    # 生成项目上下文
bmad-bmm-document-project            # 项目文档化

# 快速开发
bmad-bmm-quick-spec                  # 快速规范
bmad-bmm-quick-dev                   # 快速开发
```

**BMB - 构建器模块**：
```bash
# 代理管理
bmad-bmb-create-agent                # 创建新代理
bmad-bmb-edit-agent                  # 编辑代理
bmad-bmb-validate-agent              # 验证代理配置

# 模块管理
bmad-bmb-create-module               # 创建新模块
bmad-bmb-create-module-brief         # 创建模块简报
bmad-bmb-edit-module                 # 编辑模块
bmad-bmb-validate-module             # 验证模块

# 工作流管理
bmad-bmb-create-workflow             # 创建工作流
bmad-bmb-edit-workflow               # 编辑工作流
bmad-bmb-rework-workflow             # 返工工作流
bmad-bmb-validate-workflow           # 验证工作流
bmad-bmb-validate-max-parallel-workflow  # 验证最大并行工作流
```

**CIS - 创意智能套件**：
```bash
bmad-cis-design-thinking             # 设计思维
bmad-cis-innovation-strategy         # 创新战略
bmad-cis-problem-solving             # 问题解决
bmad-cis-storytelling                # 故事叙述
```

**TEA - 测试架构企业**：
```bash
bmad-tea-teach-me-testing            # 测试教学
bmad-tea-testarch-framework          # 测试框架初始化
bmad-tea-testarch-atdd               # ATDD（验收测试驱动开发）
bmad-tea-testarch-automate           # 测试自动化（生成 API/E2E 测试）
bmad-tea-testarch-test-design        # 测试设计（风险评估 + 覆盖策略）
bmad-tea-testarch-trace              # 需求跟踪到测试
bmad-tea-testarch-nfr                # 非功能需求评估
bmad-tea-testarch-ci                 # CI/CD 流水线设置
bmad-tea-testarch-test-review        # 测试质量审查

# QA 特定
bmad-bmm-qa-generate-e2e-tests       # 生成 E2E 测试
```

**文档管理**：
```bash
bmad-index-docs                      # 索引文档
bmad-shard-doc                       # 分片文档
bmad-review-adversarial-general      # 对抗性审查（通用）
bmad-editorial-review-structure      # 编辑审查（结构）
bmad-editorial-review-prose          # 编辑审查（散文）
```

### 执行单个测试

**使用 TEA 工作流生成和运行测试**：

1. **ATDD 工作流**（推荐用于新功能）：
   ```bash
   bmad-tea-testarch-atdd
   # 选择菜单码:
   # [ATDD] - 从验收标准生成测试
   # [TDD] - 测试驱动开发
   ```

2. **测试自动化工作流**（生成 API/E2E 测试）：
   ```bash
   bmad-tea-testarch-automate
   # 选择菜单码:
   # [AT] - API 测试生成
   # [E2E] - E2E 测试生成
   ```

3. **测试审查工作流**：
   ```bash
   bmad-tea-testarch-test-review
   # 审查现有测试质量
   ```

**测试输出位置**: `_bmad-output/tea/` 目录

### 执行单个工作流

所有 BMAD 工作流通过 Opencode IDE 命令触发：

1. 使用命令触发器（例如 `bmad-bmb-edit-workflow`）
2. 或通过 `/bmad-help` 获取可用工作流列表
3. 工作流自动保存输出到 `{project-root}/_bmad-output/`

---

## 代码风格指南

### 文件命名规范

| 文件类型 | 命名格式 | 示例 |
|----------|----------|------|
| **工作流文件** | `workflow.md` 或 `workflow.yaml` | `generate-project-context/workflow.md` |
| **代理文件** | `{agent-name}.md` | `architect.md`, `pm.md` |
| **命令文件** | `bmad-{module}-{action}.md` | `bmad-bmm-create-prd.md` |
| **配置文件** | `config.yaml` | `bmm/config.yaml` |
| **模板文件** | `template.md` | `project-context-template.md` |
| **数据文件** | `{data-type}.csv` | `agent-manifest.csv` |
| **步骤文件** | `step-{n}-{name}.md` | `step-01-discover.md` |

### 目录结构

```
bmad-cms/
├── .opencode/                        # Opencode IDE 配置
│   ├── agent/                        # 代理定义（21 个代理）
│   ├── command/                      # 命令触发器（56 个命令）
│   └── package.json                  # IDE 依赖
├── _bmad/                            # BMAD 框架核心
│   ├── _config/                      # 安装与模块清单
│   │   ├── agent-manifest.csv        # 21 个注册代理
│   │   ├── workflow-manifest.csv     # 51 个注册工作流
│   │   └── manifest.yaml             # 模块版本
│   ├── core/                         # 核心工作流（头脑风暴、派对模式）
│   ├── bmm/                          # 业务管理模块
│   │   ├── agents/                   # 9 个代理（PM、架构师、开发、QA 等）
│   │   ├── workflows/                # 分析、规划、实现工作流
│   │   └── config.yaml               # 模块配置
│   ├── bmb/                          # 构建器模块
│   │   ├── agents/                   # 3 个代理（代理/模块/工作流构建师）
│   │   └── workflows/                # 创建/编辑/验证代理和工作流
│   ├── cis/                          # 创意智能套件
│   │   ├── agents/                   # 5 个代理（设计思维、创新等）
│   │   └── workflows/                # 创意问题解决方法
│   └── tea/                          # 测试架构企业
│       ├── agents/                   # TEA 代理（测试架构师）
│       └── workflows/                # 测试框架、ATDD、自动化
├── _bmad-output/                     # 生成的输出
│   ├── planning-artifacts/           # 规划产物（PRD、架构等）
│   ├── project-context.md            # 项目上下文文档
│   └── {module}/                     # 模块特定输出
└── docs/                             # 项目文档
```

### 工作流文件格式

工作流使用**微文件架构**，带有 frontmatter：

```yaml
---
name: workflow-name
description: 清晰描述工作流目的
context_file: ''  # 可选上下文路径
---

# 工作流标题

**Goal:** 清晰的目标陈述

**Your Role:** 代理角色定义

---

## WORKFLOW ARCHITECTURE

## INITIALIZATION

## STEPS
```

### 配置文件格式

每个模块都有 `config.yaml`，包含必需字段：

```yaml
user_name: <name>
communication_language: Chinese
document_output_language: Chinese
output_folder: "{project-root}/_bmad-output"
planning_artifacts_folder: "{project-root}/_bmad-output/planning-artifacts"
project_knowledge_folder: "{project-root}/docs"
user_skill_level: intermediate  # beginner | intermediate | advanced
```

**CRITICAL**: 所有工作流在执行前**必须**解析配置文件变量。

### 变量解析

工作流变量遵循以下模式：

| 变量模式 | 说明 | 示例 |
|----------|------|------|
| `{project-root}` | 项目根目录 | `/Users/sacrtap/Documents/trae_projects/bmad-cms` |
| `{installed_path}` | 模块安装路径 | `_bmad/bmm` |
| `{output_folder}` | 输出目录（来自配置） | `_bmad-output` |
| `{{date}}` | 系统生成的时间戳 | `2026-02-25T10:30:00.000Z` |
| `{config_source}` | 来自 config.yaml 的值 | `{user_name}` |

---

## 代理通信协议

### 语言协议

- **默认**: 使用配置的 `communication_language`（**中文**）交流
- **技术命令**: 保持**英文**（工作流命令、文件路径等）
- **紧急/关键**: 使用** urgent/critical **语言强调工作流命令的重要性

### 代理激活格式（XML）

```xml
<agent id="agent-name" name="DisplayName" icon="🎯">
  <activation critical="true">
    <step n="1">加载 config.yaml</step>
    <step n="2">存储会话变量</step>
    <step n="3">显示菜单</step>
    <step n="4">WAIT for user input</step>
  </activation>
  <menu>
    <item cmd="CMD">[CMD] 菜单项描述</item>
  </menu>
</agent>
```

**关键要求**：
- ✅ 必须显示**完整菜单**供用户选择
- ✅ 必须**WAIT**用户输入后才能继续
- ✅ 使用** critical="true" **确保代理遵循激活步骤

### CSV 数据文件格式

结构化数据使用 CSV 格式存储：

- `agent-manifest.csv` - 代理注册表
- `workflow-manifest.csv` - 工作流注册表
- `module-help.csv` - 模块特定帮助
- 领域特定数据（头脑风暴方法、创新框架等）

**格式规范**：
```csv
id,name,description,module
agent-001,pm,产品经理代理，负责需求分析,bmm
agent-002,architect,系统架构师代理，负责架构设计，bmm
```
- 第一行是表头
- 不需要引号（除非必要）
- 使用 UTF-8 编码

---

## 错误处理

### 错误类型与处理策略

| 错误类型 | 处理策略 | 用户沟通 |
|----------|----------|----------|
| **Config Load Failure** | **STOP** 并报告错误 | "配置文件加载失败：{错误信息}" |
| **Missing Files** | 通知用户文件不存在 | "文件不存在：{文件路径}" |
| **Invalid Input** | 请求澄清 | "请澄清：{具体问题}" |
| **Workflow Errors** | 遵循 `workflow.xml` 错误恢复 | "工作流执行错误，尝试恢复..." |
| **User Cancellation** | 优雅退出，保存进度 | "已取消，进度已保存到：{路径}" |

### 错误消息格式

```markdown
❌ **错误**: {错误类型}

**详情**: {具体错误信息}

**建议操作**:
1. {操作步骤 1}
2. {操作步骤 2}

**需要帮助吗？** 我可以：
- [重试] 重新尝试操作
- [跳过] 跳过此步骤
- [帮助] 获取更多帮助
```

---

## 输出管理

### 输出文件位置

```
_bmad-output/
├── project-context.md                    # 项目上下文文档
├── planning-artifacts/                   # 规划产物
│   ├── product-brief-{date}.md
│   ├── prd-{date}.md
│   ├── architecture-{date}.md
│   └── ux-design-{date}.md
├── bmm/                                  # BMM 模块输出
│   ├── epics-{date}.md
│   └── research-{date}.md
├── bmb/                                  # BMB 模块输出
│   ├── agent-{name}-{date}.md
│   └── workflow-{name}-{date}.md
├── cis/                                  # CIS 模块输出
│   └── {workflow-name}-{date}.md
└── tea/                                  # TEA 模块输出
    ├── test-framework-{date}.md
    ├── atdd-tests-{date}.md
    └── e2e-tests-{date}.md
```

### 输出保存规则

**模板工作流**：
- ✅ **每**一个 `template-output` 标签后**立即保存**
- ❌ **禁止**批量保存多个模板输出
- ✅ 保存后询问用户确认（除非 `#yolo` 模式）

**行动工作流**：
- ✅ 执行但不生成文件输出
- ✅ 直接在对话中呈现结果

**文件命名**：
```
{output_folder}/{module}/{workflow-name}-{date}.md
```

---

## 工作流执行规则

**CRITICAL MANDATES**（来自 `workflow.xml`）：

1. ✅ **ALWAYS** 读取**完整**工作流文件 - **NEVER** 使用 offset/limit
2. ✅ **ALWAYS** 按**精确数字顺序**执行**所有**步骤
3. ✅ **NEVER** 跳过任何步骤 - 对每个步骤负责
4. ✅ **每**一个 `template-output` 标签后保存到输出文件
5. ✅ 在可选步骤询问用户（除非 `#yolo` 模式激活）
6. ✅ **所有**外部模块**必须**加载配置文件

### 步骤执行模式

**顺序执行**（默认）：
```
Step 1 → Step 2 → Step 3 → ... → Step N
```

**并行执行**（仅当工作流明确允许）：
```
Step 1 → [Step 2a + Step 2b] → Step 3
```

**条件执行**（用户选择）：
```
Step 1 → IF [A] THEN Step 2a ELSE Step 2b
```

---

## 模块依赖

**已安装模块**：

```yaml
Modules installed:
- core: 6.0.3 (built-in)           # 核心工作流（头脑风暴、派对模式）
- bmm: 6.0.3 (built-in)            # 业务管理模块（9 个代理）
- bmb: 0.1.6 (external)            # 构建器模块（bmad-builder）
- cis: 0.1.8 (external)            # 创意智能套件（bmad-creative-intelligence-suite）
- tea: 1.2.6 (external)            # 测试架构企业（bmad-method-test-architecture-enterprise）
```

**兼容性检查**：
- ✅ core + bmm 6.0.3 完全兼容
- ⚠️ bmb 0.1.6+ 需要 core 6.0+
- ⚠️ cis 0.1.8+ 需要 core 6.0+
- ⚠️ tea 1.2.6+ 需要 core 6.0+

---

## IDE 集成

### Opencode IDE 配置

**主 IDE**: Opencode（配置在 `_bmad/_config/manifest.yaml`）

**配置位置**：
- **代理文件**: `.opencode/agent/` 目录
- **命令文件**: `.opencode/command/` 目录（56 个命令）
- **Skills**: 从 `~/.agents/skills/` 和 `~/.claude/skills/` 加载

**IDE 依赖**（`.opencode/package.json`）：
```json
{
  "name": "bmad-cms-opencode",
  "version": "1.0.0",
  "dependencies": {
    "@opencode/core": "latest"
  }
}
```

---

## 快速入门

### 第一次使用

1. **了解可用工作流**：
   ```bash
   /bmad-help
   ```

2. **选择适合任务的模块**：
   - **新项目**: 从 BMM 开始（产品简报 → PRD → 架构）
   - **新功能**: 使用 BMM（PRD → 史诗 → 架构）
   - **测试**: 使用 TEA 代理菜单码
   - **创意工作**: 使用 CIS 模块
   - **系统变更**: 使用 BMB 修改代理/工作流

3. **执行工作流**：
   ```bash
   bmad-bmm-create-product-brief  # 创建产品简报
   ```

4. **查看输出**：
   - 输出保存在 `_bmad-output/` 目录
   - 文件命名：`{workflow-name}-{date}.md`

5. **多代理协作**：
   ```bash
   bmad-party-mode  # 复杂任务的多代理讨论
   ```

### 常用工作流路径

**新产品开发**：
```
bmad-bmm-create-product-brief
  → bmad-bmm-create-prd
    → bmad-bmm-create-epics-and-stories
      → bmad-bmm-create-architecture
        → bmad-bmm-dev-story
```

**测试驱动开发**：
```
bmad-tea-testarch-atdd
  → bmad-tea-testarch-automate
    → bmad-tea-testarch-ci
```

**系统重构**：
```
bmad-bmb-edit-agent
  → bmad-bmb-edit-workflow
    → bmad-bmb-validate-agent
      → bmad-bmb-validate-workflow
```

---

## 反模式（避免这些错误）

| 反模式 | 正确做法 | 影响 |
|--------|----------|------|
| ❌ 跳过 config.yaml 加载 | ✅ **总是**先加载配置文件 | 高 - 变量解析失败 |
| ❌ 部分文件读取（使用 offset/limit） | ✅ **总是**读取完整文件 | 高 - 错过关键步骤 |
| ❌ 批量保存模板输出 | ✅ **每个** template-output 后立即保存 | 中 - 丢失进度 |
| ❌ 在 template-output 未经用户确认继续 | ✅ **总是**询问确认（除非 #yolo） | 中 - 用户不满 |
| ❌ 硬编码路径 | ✅ **总是**使用变量解析 | 高 - 跨平台失败 |
| ❌ 忽略模块版本兼容性 | ✅ **检查** manifest.yaml 版本 | 高 - 工作流崩溃 |
| ❌ 乱序修改工作流步骤 | ✅ **严格按顺序**执行 | 高 - 逻辑错误 |
| ❌ 中文文档使用英文语法 | ✅ **遵循中文语法规范** | 中 - 文档质量下降 |

---

## 项目上下文

**项目上下文文档**已生成并保存在：
```
_bmad-output/project-context.md
```

**包含内容**：
- 150+ 条关键规则
- 技术栈与版本（Python 3.11+, Vue 3.x, PostgreSQL 18等）
- 语言特定规则（Python 异步/类型，TypeScript 严格类型）
- 框架特定规则（Sanic、Vue 3、Pinia）
- 领域模式（命名、目录结构、API 格式等）
- AI 代理特别注意事项和检查清单

**使用项目上下文**：
- AI 代理实现代码前**必读**
- 包含快速参考（30 秒掌握核心规则）
- 包含✅正确和❌错误对比示例
- 包含提交前自检检查清单

---

## 帮助与支持

### 获取帮助

1. **一般帮助**：
   ```bash
   /bmad-help
   ```

2. **模块特定帮助**：
   - BMM: 查看 `bmad-bmm-*.md` 命令文件
   - BMB: 查看 `bmad-bmb-*.md` 命令文件
   - CIS: 查看 `bmad-cis-*.md` 命令文件
   - TEA: 查看 `bmad-tea-*.md` 命令文件

3. **工作流帮助**：
   - 每个工作流文件包含完整说明
   - 步骤文件包含详细指导

### 故障排除

**常见问题**：

1. **工作流不执行**：
   - 检查 config.yaml 是否存在
   - 验证模块版本兼容性
   - 确认命令文件路径正确

2. **输出未保存**：
   - 检查 `_bmad-output/` 目录权限
   - 确认工作流包含 `template-output` 标签
   - 验证 frontmatter 配置

3. **代理不响应**：
   - 检查代理激活步骤是否完整
   - 确认菜单码正确
   - 验证 WAIT 用户输入

---

**文档版本**: 2.0  
**最后更新**: 2026-02-25  
**维护者**: Sacrtap  
**许可证**: MIT
