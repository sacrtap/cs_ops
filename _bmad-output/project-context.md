---
project_name: "cs_ops"
user_name: "Sacrtap"
date: "2026-02-28"
sections_completed:
  [
    "technology_stack",
    "language_rules",
    "framework_rules",
    "testing_rules",
    "code_quality_rules",
    "workflow_rules",
    "critical_rules",
  ]
existing_patterns_found: 150
status: "complete"
optimized_for_llm: true
last_reviewed: "2026-02-28"
review_notes: "目录结构审查完成，PostgreSQL 18 数据库配置确认"
---

# Project Context for AI Agents

_此文件包含 AI 代理在 cs_ops 项目中实现代码时必须遵循的关键规则和模式。重点关注代理可能忽略的不明显细节。_

---

## Technology Stack & Versions

### Backend

- **Python**: 3.11+ (async/await required)
- **Web Framework**: Sanic (async request handling)
- **ORM**: SQLAlchemy 2.0+ (async session, modern API)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 18 (UTF-8 encoding)

### Frontend

- **Framework**: Vue 3.x (Composition API only)
- **Language**: TypeScript (strict mode)
- **UI Library**: Arco Design
- **State Management**: Pinia

### Deployment

- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

### BMAD Framework

- **Core**: 6.0.3 (built-in)
- **BMM**: 6.0.3 (built-in) - 业务管理模块
- **BMB**: 0.1.6 (external) - 构建器模块
- **CIS**: 0.1.8 (external) - 创意智能套件
- **TEA**: 1.3.1 (external) - 测试架构企业

### Critical Version Constraints

- SQLAlchemy 2.0+ required for async session support
- Python 3.11+ for improved async performance
- PostgreSQL 18 for latest features and performance
- Vue 3.4+ for Composition API stability

## Critical Implementation Rules

### Language-Specific Rules

#### Python Rules

**Async/Await Usage**

- All I/O operations MUST use async/await
- Database operations MUST use SQLAlchemy async_session
- API routes MUST be async functions
- Use asyncio.gather() for parallel async operations

**Type Annotations**

- All functions MUST include type hints
- Use typing module: Optional, Union, List, Dict
- Return types MUST be explicitly declared
- Use Pydantic models for request/response validation

**Error Handling**

- Catch specific exceptions, not bare Exception
- Return standard error response format: {error: {code, message, details}}
- Log exceptions with full stack trace
- Use HTTPException for API errors

**SQLAlchemy 2.0 Patterns**

- Use select() syntax, NOT legacy Query API
- Use async_session for all database operations
- Configure relationship lazy loading explicitly
- Use session context managers for proper cleanup

#### TypeScript Rules

**Strict Mode Requirements**

- strict: true in tsconfig.json
- NO any type usage - use unknown or specific types
- All interfaces MUST have explicit type definitions
- Enable noImplicitAny, strictNullChecks

**Composition API Patterns**

- Use <script setup> syntax exclusively
- Use ref() for primitives, reactive() for objects
- Use defineProps/defineEmits for component interfaces
- Use computed() for derived state, NOT methods

**Import/Export Conventions**

- Use ES6 module syntax (import/export)
- Relative imports MUST include .ts extension
- Organize imports: vue -> libs -> components -> utils
- Use named exports over default exports

### Framework-Specific Rules

#### Sanic Rules (Backend)

**Blueprint Organization**

- Organize routes using Blueprints by domain
- Register blueprints in main app initialization
- Each blueprint handles related functionality

**Async Request Handling**

- All route handlers MUST be async functions
- Use request.json for request body
- Use request.args for query parameters
- Use request.url_params for path parameters

**Response Format**

- Standard response format: {data: T, meta: {timestamp, request_id}, error: null}
- Success: 200 OK, Created: 201 Created
- Async tasks: 202 Accepted with task_id
- Errors: HTTPException with {error: {code, message, details}}

**Middleware Usage**

- CORS middleware for cross-origin requests
- Authentication middleware for protected routes
- Logging middleware for request/response tracking
- Error handling middleware for centralized error processing

#### Vue 3 Rules (Frontend)

**Component Structure**

- Use Composition API with <script setup> syntax exclusively
- Use Arco Design components for UI consistency
- Organize components by feature/domain, not type
- Use PascalCase for component names

**Pinia State Management**

- Use defineStore() to create stores
- Use state for reactive data, getters for computed values
- Use actions for async operations and mutations
- Import stores where needed, avoid global injection

**API Integration**

- Wrap all HTTP calls in api/ directory modules
- Use axios with base URL configuration
- Implement request/response interceptors for auth
- Handle errors uniformly with notification component

**Async Task Polling**

- Poll async task progress every 2 seconds
- Use setInterval for polling mechanism
- Clear interval on task completion or error
- Show progress indicator during polling
- Use REST API polling pattern: GET /tasks/{task_id}/progress

### Testing Rules

#### Backend Testing (Python/Sanic)

**Test Framework Setup**

- Use pytest as test runner
- Use pytest-asyncio for async test support
- Use pytest-cov for coverage reporting
- Configure in pytest.ini at project root

**Test Organization**

- Test files: test\_\*.py
- Test directory: tests/ at project root
- Test classes: Test\* prefix
- Test functions: test\_\* prefix

**Mock Usage**

- Use pytest-mock for mocking
- Mock external dependencies (database, external APIs, Redis)
- Use fixtures for test data setup and teardown
- Avoid mocking business logic, only mock I/O

**Test Types**

- Unit tests: Test individual functions/methods in isolation
- Integration tests: Test module interactions
- API tests: Test HTTP endpoints with test client
- Target coverage: 80% minimum

#### Frontend Testing (Vue 3/TypeScript)

**Test Framework Setup**

- Use Vitest as test runner
- Use @vue/test-utils for component testing
- Use @testing-library/vue for user behavior tests
- Configure in vitest.config.ts

**Test Organization**

- Test files: _.test.ts or _.spec.ts
- Co-locate tests with source files in **tests**/ directories
- Use describe() blocks to organize test suites
- Use it() or test() for individual test cases

**Component Testing**

- Test component rendering with correct props
- Test user interactions (clicks, inputs, etc.)
- Test emitted events
- Test slots content rendering
- Mock child components for unit testing

**Pinia Store Testing**

- Test state initialization
- Test getters return correct values
- Test actions perform correct mutations
- Mock API calls in action tests

### Code Quality & Style Rules

#### Backend Style (Python)

**Naming Conventions**

- Modules/files: snake_case (e.g., `user_service.py`)
- Functions/variables: snake_case (e.g., `get_user_by_id`)
- Classes: PascalCase (e.g., `UserService`)
- Constants: UPPER_CASE (e.g., `MAX_RETRY_COUNT`)
- Database tables: snake_case plural (e.g., `users`, `customer_addresses`)
- API endpoints: kebab-case (e.g., `/api/v1/user-profiles`)

**Code Organization**

- Organize by feature modules
- Each module contains: models/, schemas/, services/, routes/
- Utility functions in utils/ directory
- One class per file for models and services

**Documentation Requirements**

- All public functions MUST have docstrings
- Use Google-style docstrings
- Complex business logic MUST have inline comments
- API endpoints MUST have OpenAPI descriptions

**Linting Configuration**

- Use flake8 for linting
- Use black for code formatting
- Use isort for import sorting
- Use mypy for type checking

#### Frontend Style (TypeScript/Vue)

**Naming Conventions**

- Component files: PascalCase (e.g., `UserList.vue`)
- Component names: PascalCase (e.g., `<UserList>`)
- Functions/variables: camelCase (e.g., `getUserById`)
- Types/interfaces: PascalCase (e.g., `UserResponse`)
- Constants: UPPER_CASE (e.g., `API_BASE_URL`)
- CSS classes: kebab-case (e.g., `.user-list-item`)

**Code Organization**

- Feature modules in src/modules/{module}/
- Shared components in src/components/
- API calls in src/api/
- Pinia stores in src/stores/
- Types in src/types/
- Utilities in src/utils/

**Documentation Requirements**

- Components MUST have comment describing purpose
- Complex functions MUST have JSDoc comments
- Props MUST have type definitions and default values
- Events MUST be documented with @emits annotation

**Linting Configuration**

- Use ESLint with Vue 3 + TypeScript config
- Use Prettier for code formatting
- Enable no-unused-vars, no-explicit-any
- Enforce single quotes, semicolons

### Development Workflow Rules

#### Git & Repository Rules

**Branch Naming Conventions**

- Main branch: `main`
- Development branch: `develop`
- Feature branches: `feature/{feature-name}` (e.g., `feature/user-auth`)
- Bug fixes: `fix/{bug-description}` (e.g., `fix/login-error`)
- Hot fixes: `hotfix/{urgent-fix}`

**Commit Message Format**

- Use Conventional Commits specification
- Format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Example: `feat(auth): add user login endpoint`

**Pull Request Requirements**

- All code MUST be code-reviewed before merging
- CI/CD pipeline MUST pass (tests, linting, type check)
- Tests MUST cover new functionality
- Documentation MUST be updated if API changes
- Use PR templates for consistency

**Code Review Checklist**

- Code follows style guidelines
- Tests are included and passing
- No security vulnerabilities introduced
- Performance implications considered
- Error handling is adequate

#### Docker & Deployment

**Image Building**

- Use multi-stage builds to reduce image size
- Backend: Python slim base image
- Frontend: Node for build, Nginx for serving
- Tag images with version and git commit SHA

**Container Orchestration**

- Use docker-compose for local development
- Define service dependencies (depends_on)
- Configure environment variables via .env files
- Use named volumes for persistent data

**Deployment Patterns**

- Use blue-green deployment for zero-downtime
- Configure health checks for all services
- Use environment-specific configurations
- Implement rollback procedures

### Critical Don't-Miss Rules

#### Anti-Patterns to Avoid

**Database Operations**

- ❌ NEVER use N+1 queries - ALWAYS use eager loading (selectinload, joinedload)
- ❌ NEVER execute database queries in loops - batch operations instead
- ❌ NEVER forget to commit session or close connections
- ❌ NEVER use synchronous I/O in async context

**Async Programming**

- ❌ NEVER use blocking I/O in async functions (use aiohttp, asyncpg, etc.)
- ❌ NEVER forget to await async function calls
- ❌ NEVER block the event loop with long-running computations

**API Design**

- ❌ NEVER return sensitive data (passwords, tokens, internal IDs)
- ❌ NEVER expose internal error details in 500 responses
- ❌ NEVER skip input validation - always validate with Pydantic schemas
- ❌ NEVER return raw database errors to clients

**Frontend Performance**

- ❌ NEVER forget :key in v-for loops
- ❌ NEVER forget to clear intervals/subscriptions in onUnmounted
- ❌ NEVER cause unnecessary re-renders with reactive data misuse

#### Critical Edge Cases

**Data Permission Filtering**

- ALL database queries MUST apply data permission filters
- Users can ONLY access authorized customer data
- Use SQLAlchemy session-level event listeners for automatic filtering
- Test permission filtering in all API endpoints

**Async Task Handling**

- Tasks MUST have timeout handling (default: 30 minutes)
- Task failures MUST have retry mechanism (max 3 retries)
- Task progress MUST be trackable via progress endpoint
- Long-running tasks MUST support cancellation

**Concurrency Control**

- Use optimistic locking (version field) for concurrent updates
- Use database unique constraints to prevent duplicates
- Use Redis distributed locks for cross-instance coordination
- Handle race conditions in critical sections

#### Security Rules

**Authentication & Authorization**

- ALL API endpoints MUST validate JWT tokens (except public endpoints)
- Use RBAC (Role-Based Access Control) for permission management
- Sensitive operations MUST log audit trail
- Implement rate limiting for authentication endpoints

**Data Validation**

- ALL user input MUST be validated using Pydantic schemas
- NEVER trust client-side data - validate on server
- Use parameterized queries to prevent SQL injection
- Sanitize HTML input to prevent XSS attacks

**Sensitive Data Handling**

- Passwords MUST be hashed with bcrypt/argon2
- NEVER log sensitive data (passwords, tokens, PII)
- Use HTTPS for all data transmission
- Implement secure cookie handling for session management

#### Business Logic Gotchas

**Customer Dual-ID Design**

- Customer table uses DUAL-ID: `id` (database PK) + `customer_code` (business ID)
- ALWAYS use `customer_code` for business logic and API responses
- Use `id` only for internal database relationships
- Index both fields appropriately

**Pricing Strategy Pattern**

- Use Strategy pattern for pricing calculations
- Three strategies: FlatRate, TieredRate, PackageRate
- Strategy selection based on customer subscription type
- Test all pricing scenarios thoroughly

---

## Usage Guidelines

### For AI Agents

**必读要求**：

- ✅ 在实现任何代码**之前**必须阅读此文件
- ✅ **严格遵循**所有规则，不要偏离
- ✅ 当有疑问时，选择更严格的选项
- ✅ 如果发现新的模式，更新此文件

**实现检查清单**：

- [ ] 已阅读并理解此文件的所有规则
- [ ] 代码遵循技术栈版本要求
- [ ] 代码遵循语言和框架特定规则
- [ ] 代码遵循测试和质量标准
- [ ] 代码避免了所有列出的反模式
- [ ] 代码处理了所有相关的边缘情况

### For Humans

**维护指南**：

- 📝 当技术栈变更时更新此文件
- 📝 当发现新的关键模式时添加规则
- 📝 每季度审查一次，移除过时的规则
- 📝 随着团队成熟，移除变得显而易见的规则

**优化原则**：

- 保持文件简洁，专注于 AI 代理的需求
- 只记录不明显的、容易被忽略的规则
- 使用具体的、可操作的语言
- 确保每条规则都提供独特价值

---

**Last Updated**: 2026-02-28  
**Status**: Complete ✅  
**Total Rules**: 150+ critical implementation rules  
**Optimized for**: LLM context efficiency + AI agent consistency

---

## Project Directory Structure

### Root Structure

```
cs_ops/
├── _bmad/                          # BMAD 框架核心
│   ├── _config/                    # 配置清单
│   │   ├── agent-manifest.csv      # 21 个注册代理
│   │   ├── workflow-manifest.csv   # 51 个注册工作流
│   │   └── manifest.yaml           # 模块版本
│   ├── core/                       # 核心工作流
│   ├── bmm/                        # 业务管理模块
│   ├── bmb/                        # 构建器模块
│   ├── cis/                        # 创意智能套件
│   └── tea/                        # 测试架构企业
├── _bmad-output/                   # BMAD 生成输出
│   ├── project-context.md          # 项目上下文（本文档）
│   └── planning-artifacts/         # 规划产物
├── .opencode/                      # Opencode IDE 配置
│   ├── agent/                      # 代理定义
│   └── command/                    # 命令触发器
├── backend/                        # 后端服务
│   ├── app/                        # 应用源码
│   │   ├── config/                 # 配置管理
│   │   ├── models/                 # SQLAlchemy 模型
│   │   ├── routes/                 # API 路由
│   │   ├── schemas/                # Pydantic 模式
│   │   ├── services/               # 业务逻辑
│   │   └── utils/                  # 工具函数
│   ├── alembic/                    # 数据库迁移
│   ├── tests/                      # 后端测试
│   ├── requirements.txt            # Python 依赖
│   └── pyproject.toml              # Python 项目配置
├── frontend/                       # 前端服务
│   ├── src/                        # Vue 源码（待创建）
│   ├── public/                     # 静态资源
│   ├── tests/                      # 前端测试
│   ├── vite.config.ts              # Vite 配置
│   ├── package.json                # Node 依赖
│   └── tsconfig.json               # TypeScript 配置
├── tests/                          # 端到端测试
│   ├── api/                        # API 测试
│   ├── e2e/                        # Playwright E2E
│   ├── unit/                       # 单元测试
│   └── support/                    # 测试支持
├── docs/                           # 项目文档（待完善）
├── src/                            # 前端源码（重复，建议移除）
├── AGENTS.md                       # AI 代理指南
├── Makefile                        # 构建脚本
├── pyproject.toml                  # 根 Python 配置
├── package.json                    # 根前端配置
└── playwright.config.ts            # Playwright 配置
```

### Directory Naming Conventions

- **后端**: `backend/` 包含所有 Python 后端代码
- **前端**: `frontend/` 包含所有 Vue/TypeScript 代码
- **测试**: `tests/` 在根目录（E2E），`backend/tests/`（后端测试）
- **文档**: `docs/` 存放项目文档
- **输出**: `_bmad-output/` BMAD 工作流生成文件
- **框架**: `_bmad/` BMAD 框架核心

### Critical Directory Rules

- ✅ `backend/app/` 必须包含 config/, models/, routes/, schemas/, services/, utils/
- ✅ `backend/alembic/` 必须配置 script_location 和 sqlalchemy.url
- ✅ `frontend/src/` 必须创建（当前缺失）
- ✅ `docs/` 必须包含项目文档（当前为空）
- ⚠️ 根目录 `src/` 与 `frontend/src/` 冲突，建议移除或合并
