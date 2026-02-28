# CS Ops - 客户成功运营平台

**版本**: 0.1.0  
**最后更新**: 2026-02-28  
**状态**: 开发中

---

## 📋 项目概述

CS Ops 是一个内部运营中台客户信息管理与运营系统，提供客户管理、账单管理、健康度监控等核心功能。

### 核心价值

- 🎯 **客户管理**: 统一的客户信息管理平台
- 💰 **账单管理**: 自动化账单生成和跟踪
- 📊 **健康度监控**: 客户健康度评分和预警
- 🔄 **运营自动化**: 减少手动操作，提升效率

---

## 🛠️ 技术栈

### 后端

| 技术       | 版本            | 说明            |
| ---------- | --------------- | --------------- |
| **框架**   | Sanic 23.0+     | 异步 Web 框架   |
| **ORM**    | SQLAlchemy 2.0+ | 异步数据库操作  |
| **数据库** | PostgreSQL 18   | 关系型数据库    |
| **迁移**   | Alembic         | 数据库版本管理  |
| **验证**   | Pydantic 2.0+   | 数据验证        |
| **认证**   | JWT             | JSON Web Tokens |
| **密码**   | bcrypt          | 密码哈希        |

### 前端

| 技术     | 版本              | 说明             |
| -------- | ----------------- | ---------------- |
| **框架** | Vue 3.4+          | Composition API  |
| **语言** | TypeScript 5.3+   | 严格模式         |
| **构建** | Vite 5.0+         | 快速开发和构建   |
| **UI**   | Arco Design 2.54+ | 企业级 UI 组件库 |
| **状态** | Pinia 2.1+        | 轻量级状态管理   |
| **路由** | Vue Router 4.2+   | 单页应用路由     |
| **HTTP** | Axios 1.6+        | HTTP 客户端      |

### 测试

| 技术       | 版本             | 说明                |
| ---------- | ---------------- | ------------------- |
| **E2E**    | Playwright 1.40+ | 跨浏览器端到端测试  |
| **后端**   | pytest 7.0+      | Python 单元测试框架 |
| **前端**   | Vitest 1.1+      | Vue 组件测试        |
| **覆盖率** | 95%              | 代码覆盖率目标      |

### 开发框架

| 技术       | 版本     | 说明          |
| ---------- | -------- | ------------- |
| **BMAD**   | 6.0.3    | 业务管理框架  |
| **IDE**    | Opencode | AI 驱动的 IDE |
| **Python** | 3.11+    | 后端运行时    |
| **Node**   | 20+      | 前端运行时    |

---

## 📂 项目结构

```
cs_ops/
├── _bmad/                        # BMAD 框架核心
│   ├── _config/                  # 配置清单
│   ├── core/                     # 核心工作流
│   ├── bmm/                      # 业务管理模块
│   ├── bmb/                      # 构建器模块
│   ├── cis/                      # 创意智能套件
│   └── tea/                      # 测试架构企业
├── _bmad-output/                 # BMAD 生成输出
├── .opencode/                    # Opencode IDE 配置
├── backend/                      # 后端服务
│   ├── app/                      # 应用源码
│   │   ├── config/               # 配置管理
│   │   ├── models/               # SQLAlchemy 模型
│   │   ├── routes/               # API 路由
│   │   ├── schemas/              # Pydantic 模式
│   │   ├── services/             # 业务逻辑
│   │   └── utils/                # 工具函数
│   ├── alembic/                  # 数据库迁移
│   ├── tests/                    # 后端测试
│   ├── requirements.txt          # Python 依赖
│   └── pyproject.toml            # Python 项目配置
├── frontend/                     # 前端服务
│   ├── src/                      # Vue 源码
│   │   ├── api/                  # API 客户端
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── views/                # 页面组件
│   │   ├── router/               # 路由配置
│   │   ├── components/           # 可复用组件
│   │   ├── types/                # TypeScript 类型
│   │   ├── utils/                # 工具函数
│   │   └── assets/               # 静态资源
│   ├── tests/                    # 前端测试
│   ├── package.json              # Node 依赖
│   └── vite.config.ts            # Vite 配置
├── tests/                        # 端到端测试
│   ├── api/                      # API 集成测试
│   ├── e2e/                      # Playwright E2E
│   ├── unit/                     # 单元测试
│   └── support/                  # 测试支持
├── docs/                         # 项目文档
├── AGENTS.md                     # AI 代理指南
├── Makefile                      # 构建脚本
├── pyproject.toml                # 根 Python 配置
└── package.json                  # 根前端配置
```

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.11+
- **Node.js**: 20+
- **PostgreSQL**: 18
- **Git**: 最新版

### 1. 克隆项目

```bash
git clone https://github.com/your-org/cs-ops.git
cd cs_ops
```

### 2. 安装依赖

#### 后端依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量

#### 后端配置

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件：

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops
JWT_SECRET_KEY=your-secret-key-change-in-production
APP_DEBUG=true
```

#### 前端配置

```bash
cd frontend
cp .env.example .env.local
```

### 4. 初始化数据库

```bash
cd backend
createdb cs_ops  # 创建数据库
alembic upgrade head  # 运行迁移
```

### 5. 启动服务

#### 后端服务

```bash
cd backend
python -m app.main
# 访问 http://localhost:8000/health
```

#### 前端服务

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

---

## 📖 文档导航

| 文档                             | 说明                   |
| -------------------------------- | ---------------------- |
| [开发指南](development.md)       | 开发环境搭建和开发流程 |
| [架构设计](architecture.md)      | 系统架构和技术决策     |
| [API 文档](api.md)               | API 接口文档和使用示例 |
| [部署指南](deployment.md)        | 生产环境部署流程       |
| [数据库设计](database.md)        | 数据库表结构和关系     |
| [BMAD 工作流](bmad-workflows.md) | BMAD 工作流使用指南    |

---

## 🧪 运行测试

### 后端测试

```bash
cd backend
pytest
pytest --cov=app  # 带覆盖率
```

### 前端测试

```bash
cd frontend
npm run test
npm run test:coverage  # 带覆盖率
```

### E2E 测试

```bash
# 确保后端和前端都在运行
npm run test:e2e
npm run test:e2e:ui  # UI 模式
```

### 运行所有测试

```bash
make test
```

---

## 📋 常用命令

### Makefile 命令

| 命令           | 说明           |
| -------------- | -------------- |
| `make install` | 安装所有依赖   |
| `make dev`     | 启动开发服务器 |
| `make test`    | 运行所有测试   |
| `make lint`    | 代码检查       |
| `make build`   | 生产构建       |
| `make clean`   | 清理构建产物   |

### BMAD 命令

| 命令                     | 说明           |
| ------------------------ | -------------- |
| `/bmad-help`             | 查看所有工作流 |
| `bmad-bmm-create-prd`    | 创建 PRD       |
| `bmad-bmm-dev-story`     | 开发用户故事   |
| `bmad-tea-testarch-atdd` | ATDD 测试      |

---

## 🔐 安全注意事项

### 环境变量

- ❌ **不要**将 `.env` 文件提交到 Git
- ✅ **必须**在生产环境修改 `JWT_SECRET_KEY`
- ✅ **必须**使用强密码

### 数据库

- ✅ 使用连接池
- ✅ 启用 SSL（生产环境）
- ✅ 定期备份

---

## 🤝 贡献指南

### 提交规范

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Type**:

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

### 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License

---

## 📞 联系方式

- **项目地址**: https://github.com/your-org/cs-ops
- **问题反馈**: https://github.com/your-org/cs-ops/issues

---

**最后更新**: 2026-02-28  
**维护者**: Sacrtap
