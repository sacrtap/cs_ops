# 测试架构文档 - 内部运营中台客户信息管理与运营系统

> 本文档描述项目的测试架构、工具和最佳实践

---

## 📋 目录

1. [测试框架概览](#测试框架概览)
2. [目录结构](#目录结构)
3. [安装与配置](#安装与配置)
4. [运行测试](#运行测试)
5. [测试架构](#测试架构)
6. [最佳实践](#最佳实践)
7. [CI/CD 集成](#ci-cd-集成)
8. [故障排查](#故障排查)

---

## 测试框架概览

本项目采用分层测试策略，覆盖单元测试、集成测试和 E2E 测试：

| 测试层级     | 框架               | 用途                    |
| ------------ | ------------------ | ----------------------- |
| **E2E 测试**     | Playwright         | 端到端浏览器自动化测试  |
| **API 测试**     | pytest + httpx     | 后端 API 集成测试         |
| **单元测试**     | pytest + Vitest    | 后端/前端单元测试        |
| **组件测试**     | Vitest + Vue Test Utils | Vue 组件测试       |

### 技术栈

**前端测试**：
- Playwright v1.40+ - E2E 测试
- Vitest v1.0+ - 单元测试和组件测试
- Vue Test Utils v2.4+ - Vue 组件测试工具

**后端测试**：
- pytest v7.4+ - Python 测试框架
- pytest-asyncio v0.21+ - 异步测试支持
- httpx v0.25+ - HTTP 客户端测试
- Faker v21.0+ - 测试数据生成

---

## 目录结构

```
cs-ops/
├── tests/
│   ├── e2e/                      # Playwright E2E 测试
│   │   ├── customer/             # 客户管理 E2E
│   │   │   ├── example.spec.ts   # 示例测试
│   │   │   └── *.spec.ts         # 其他 E2E 测试
│   │   ├── billing/              # 结算管理 E2E
│   │   └── auth/                 # 认证授权 E2E
│   │
│   ├── api/                      # API 集成测试
│   │   ├── customer/             # 客户 API 测试
│   │   │   └── test_customer_api.py
│   │   ├── billing/              # 结算 API 测试
│   │   └── health/               # 健康度监控 API 测试
│   │
│   ├── unit/                     # 单元测试
│   │   ├── backend/              # 后端单元测试
│   │   │   ├── models/           # 模型测试
│   │   │   ├── services/         # 服务测试
│   │   │   └── strategies/       # 策略模式测试
│   │   └── frontend/             # 前端单元测试
│   │       ├── components/       # 组件测试
│   │       └── composables/      # Composables 测试
│   │
│   └── support/                  # 测试支持
│       ├── fixtures/             # 测试 fixtures
│       │   ├── index.ts          # Playwright fixtures
│       │   └── test-data/        # 测试数据文件
│       ├── helpers/              # 辅助函数
│       │   └── test_helpers.py   # Python 辅助函数
│       └── page-objects/         # 页面对象模型
│
│   ├── conftest.py               # pytest 全局 fixtures
│   ├── pyproject.toml            # pytest 配置
│   └── README.md                 # 本文档
│
├── playwright.config.ts          # Playwright 配置
├── pyproject.toml                # Python 项目配置（含 pytest）
├── package.json                  # Node.js 项目配置
├── .env.example                  # 环境变量示例
├── .nvmrc                        # Node 版本
└── .python-version               # Python 版本
```

---

## 安装与配置

### 前置要求

- **Node.js**: >= 20.0.0 (参考 `.nvmrc`)
- **Python**: >= 3.11 (参考 `.python-version`)

### 1. 安装依赖

**前端测试依赖**：
```bash
# 使用 nvm 设置 Node 版本
nvm install
nvm use

# 安装依赖
npm install
```

**后端测试依赖**：
```bash
# 使用 pyenv 设置 Python 版本
pyenv install 3.11  # 如果未安装
pyenv local 3.11

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
.\venv\Scripts\Activate.ps1  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，设置测试环境
TEST_ENV=test
TEST_BASE_URL=http://localhost:3000
TEST_API_URL=http://localhost:8000
```

### 3. 安装 Playwright 浏览器

```bash
npx playwright install
npx playwright install-deps  # 安装系统依赖（Linux）
```

---

## 运行测试

### E2E 测试 (Playwright)

```bash
# 运行所有 E2E 测试
npm run test:e2e

# 有头模式（打开浏览器）
npm run test:e2e:headed

# 调试模式
npm run test:e2e:debug

# UI 模式
npm run test:e2e:ui

# 运行特定测试文件
npx playwright test tests/e2e/customer/example.spec.ts

# 运行特定测试用例
npx playwright test --grep "应该成功创建新客户"

# 生成测试报告
npm run test:e2e:report

# 查看测试追踪
npm run test:e2e:trace
```

### API 测试 (pytest)

```bash
# 运行所有 API 测试
pytest tests/api/ -v

# 运行特定测试文件
pytest tests/api/customer/test_customer_api.py -v

# 运行特定测试用例
pytest tests/api/customer/test_customer_api.py::TestCustomerAPI::test_create_customer -v

# 带覆盖率
pytest tests/api/ --cov=backend --cov-report=html

# 仅运行标记的测试
pytest tests/api/ -m "customer"
pytest tests/api/ -m "integration"

# 并行运行测试
pytest tests/api/ -n auto
```

### 单元测试

**后端**：
```bash
# 运行后端单元测试
pytest tests/unit/backend/ -v

# 带覆盖率
pytest tests/unit/backend/ --cov=backend --cov-report=term-missing
```

**前端**：
```bash
# 运行前端单元测试
npm run test

# UI 模式
npm run test:ui

# 带覆盖率
npm run test:coverage
```

### 运行所有测试

```bash
# 后端所有测试
pytest tests/ -v --tb=short

# 前端所有测试
npm run test && npm run test:e2e
```

---

## 测试架构

### Fixtures 架构

**Playwright Fixtures** (`tests/support/fixtures/index.ts`):

```typescript
import { test, expect } from '../support/fixtures';

test('使用测试 fixture', async ({ page, testData, apiClient }) => {
  // testData - 预生成的测试数据
  // apiClient - 封装的 API 客户端
  // authenticatedPage - 已认证的页面
});
```

**pytest Fixtures** (`tests/conftest.py`):

```python
import pytest

@pytest.mark.asyncio
async def test_using_fixtures(authenticated_client, customer_factory, db_session):
    # authenticated_client - 带认证的 HTTP 客户端
    # customer_factory - 客户数据工厂
    # db_session - 数据库会话（自动回滚）
    pass
```

### 数据工厂模式

```typescript
// TypeScript - Playwright
import { DataFactory } from '../support/fixtures/index';

const customer = DataFactory.createCustomer({
  name: '自定义客户名称'
});
```

```python
# Python - pytest
def test_with_factory(customer_factory):
    customer = customer_factory.create({
        'name': '自定义客户名称'
    })
```

### 测试数据清理

 fixtures 自动处理测试数据清理：

- Playwright: `afterEach` 钩子调用 `DataFactory.cleanup()`
- pytest: `autouse` fixture 在每个测试后重置工厂

---

## 最佳实践

### 1. 测试命名规范

```typescript
// ❌ 不好的命名
test('test 1', async () => {});

// ✅ 好的命名 - 描述预期行为
test('应该成功创建新客户', async () => {});
test('当邮箱格式无效时应该显示验证错误', async () => {});
```

### 2. Given-When-Then 结构

```typescript
test('应该支持批量导入客户', async ({ page }) => {
  // Given: 访问客户列表页
  await page.goto('/customers');
  
  // When: 点击"批量导入"按钮
  await page.click('[data-testid="bulk-import-button"]');
  
  // Then: 应该显示导入对话框
  await expect(page.locator('[data-testid="import-dialog"]')).toBeVisible();
});
```

### 3. 数据-testid 选择器策略

```html
<!-- ✅ 推荐：使用 data-testid -->
<button data-testid="new-customer-button">新建客户</button>

<!-- ❌ 避免：依赖 CSS 类或 XPath -->
<button class="btn btn-primary">新建客户</button>
```

```typescript
// ✅ 推荐
await page.click('[data-testid="new-customer-button"]');

// ❌ 避免
await page.click('.btn.btn-primary');
await page.click('//button[contains(text(), "新建客户")]');
```

### 4. 异步测试最佳实践

```python
# ✅ 推荐：使用 pytest-asyncio
@pytest.mark.asyncio
async def test_async_api():
    response = await client.get("/api/v1/customers")
    assert response.status_code == 200

# ❌ 避免：使用 asyncio.run()
def test_async_api():
    asyncio.run(client.get("/api/v1/customers"))
```

### 5. 参数化测试

```python
@pytest.mark.parametrize(
    "invalid_data,expected_error",
    [
        ({"name": ""}, "name 不能为空"),
        ({"email": "invalid"}, "邮箱格式无效"),
    ],
)
async def test_validation_errors(self, authenticated_client, invalid_data, expected_error):
    response = await authenticated_client.post("/api/v1/customers", json=invalid_data)
    assert expected_error in str(response.json())
```

### 6. 测试隔离

- ✅ 每个测试在独立的事务中运行
- ✅ 使用工厂创建测试数据
- ✅ 测试后自动回滚/清理
- ❌ 避免测试间依赖

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm install
          pip install -e ".[dev]"
          npx playwright install --with-deps
      
      - name: Run backend tests
        run: pytest tests/ --cov=backend --cov-report=xml
      
      - name: Run frontend tests
        run: npm run test
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./test-results/coverage.xml
```

---

## 故障排查

### 常见问题

**问题 1**: Playwright 测试超时

```
Error: Test timeout of 60000ms exceeded.
```

**解决方案**:
- 检查 `BASE_URL` 环境变量是否正确
- 确保应用在测试前已启动
- 增加超时时间：`test.setTimeout(120000)`

**问题 2**: pytest 找不到模块

```
ModuleNotFoundError: No module named 'backend'
```

**解决方案**:
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 以可编辑模式安装
pip install -e ".[dev]"
```

**问题 3**: Fixtures 未加载

```
fixture 'authenticated_client' not found
```

**解决方案**:
- 确认 `conftest.py` 在 `tests/` 目录下
- 检查 fixture 作用域是否正确

**问题 4**: Playwright 浏览器无法启动

```
Error: Executable doesn't exist
```

**解决方案**:
```bash
npx playwright install
npx playwright install-deps  # Linux
```

---

## 参考资料

- [Playwright 官方文档](https://playwright.dev)
- [pytest 官方文档](https://docs.pytest.org)
- [Vitest 官方文档](https://vitest.dev)
- [BMAD TEA 测试架构知识库](../../_bmad/tea/)

---

**文档版本**: 1.0  
**最后更新**: 2026-02-27  
**维护者**: Sacrtap
