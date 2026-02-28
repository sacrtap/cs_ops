# 开发指南

**最后更新**: 2026-02-28  
**适用对象**: 所有开发人员

---

## 📋 目录

1. [开发环境搭建](#开发环境搭建)
2. [代码规范](#代码规范)
3. [BMAD 工作流](#bmad-工作流)
4. [调试技巧](#调试技巧)
5. [常见问题](#常见问题)

---

## 🛠️ 开发环境搭建

### 1. 系统要求

| 组件           | 版本   | 必需    |
| -------------- | ------ | ------- |
| **Python**     | 3.11+  | ✅ 必需 |
| **Node.js**    | 20+    | ✅ 必需 |
| **PostgreSQL** | 18     | ✅ 必需 |
| **Git**        | 最新版 | ✅ 必需 |
| **Make**       | 最新版 | ✅ 必需 |

### 2. 安装 Python

#### macOS

```bash
# 使用 Homebrew
brew install python@3.11

# 验证安装
python --version  # 应显示 Python 3.11.x
```

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# 验证安装
python3 --version
```

#### Windows

```bash
# 下载安装程序
# https://www.python.org/downloads/release/python-311/

# 验证安装
python --version
```

### 3. 安装 Node.js

#### macOS

```bash
# 使用 Homebrew
brew install node@20

# 验证安装
node --version  # 应显示 v20.x.x
npm --version
```

#### Ubuntu/Debian

```bash
# 使用 NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

#### Windows

```bash
# 下载安装程序
# https://nodejs.org/en/download/

# 验证安装
node --version
npm --version
```

### 4. 安装 PostgreSQL 18

#### macOS

```bash
# 使用 Homebrew
brew install postgresql@18
brew services start postgresql@18

# 验证安装
psql --version

# 创建数据库
createdb cs_ops
```

#### Ubuntu/Debian

```bash
# 添加 PostgreSQL 仓库
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install postgresql-18

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库
sudo -u postgres createdb cs_ops
```

#### Windows

```bash
# 下载安装程序
# https://www.postgresql.org/download/windows/

# 使用 pgAdmin 或命令行创建数据库
```

### 5. 克隆项目

```bash
git clone https://github.com/your-org/cs-ops.git
cd cs_ops
```

### 6. 安装后端依赖

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 验证安装
pytest --version
```

### 7. 安装前端依赖

```bash
cd frontend

# 安装依赖
npm install

# 验证安装
npm run dev
```

### 8. 配置环境变量

#### 后端配置

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 应用配置
APP_NAME=cs_ops
APP_DEBUG=true

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cs_ops

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
BCRYPT_ROUNDS=10
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### 前端配置

```bash
cd frontend
cp .env.example .env.local
```

编辑 `.env.local` 文件：

```bash
# 开发模式
VITE_APP_DEBUG=true

# API 后端地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用配置
VITE_APP_NAME=CS Ops
VITE_APP_VERSION=0.1.0
```

### 9. 初始化数据库

```bash
cd backend

# 创建数据库（如果未创建）
createdb cs_ops

# 运行数据库迁移
alembic upgrade head

# 验证迁移
alembic current
# 应显示当前版本号：3666a9a9ed2a
```

### 10. 启动开发服务

#### 方法 1: 使用 Makefile（推荐）

```bash
# 在项目根目录
make dev
```

#### 方法 2: 手动启动

**终端 1 - 后端**:

```bash
cd backend
python -m app.main
```

**终端 2 - 前端**:

```bash
cd frontend
npm run dev
```

### 11. 验证安装

#### 后端验证

```bash
# 访问健康检查端点
curl http://localhost:8000/health

# 预期响应
{"status": "healthy", "timestamp": "2026-02-28T..."}
```

#### 前端验证

```bash
# 在浏览器访问
http://localhost:5173

# 应显示登录页面
```

---

## 📝 代码规范

### Python 代码规范

#### 1. 类型注解（必需）

```python
# ✅ 正确
from typing import Optional, List, Dict

def get_user(user_id: int) -> Optional[dict]:
    """获取用户信息"""
    pass

# ❌ 错误
def get_user(user_id):
    pass
```

#### 2. 异步代码

```python
# ✅ 正确 - 使用 async/await
async def fetch_data():
    async with db.session() as session:
        result = await session.execute(query)
        return result.scalar()

# ❌ 错误 - 同步代码调用异步函数
def fetch_data():
    with db.session() as session:
        result = session.execute(query)  # 错误！
```

#### 3. 文档字符串

```python
# ✅ 正确
class UserService:
    """用户服务类

    提供用户相关的业务逻辑，包括：
    - 用户创建
    - 用户认证
    - 用户管理
    """

    async def create_user(self, email: str, password: str) -> User:
        """创建新用户

        Args:
            email: 用户邮箱
            password: 用户密码

        Returns:
            User: 创建的用户对象

        Raises:
            ValueError: 当邮箱已存在时
        """
        pass

# ❌ 错误 - 缺少文档字符串
class UserService:
    async def create_user(self, email, password):
        pass
```

#### 4. 错误处理

```python
# ✅ 正确
from app.exceptions import AuthenticationError

async def login(email: str, password: str) -> TokenPair:
    try:
        user = await get_user_by_email(email)
        if not verify_password(password, user.password):
            raise AuthenticationError("密码错误")
        return generate_tokens(user)
    except AuthenticationError as e:
        logger.warning(f"登录失败：{email}, 原因：{str(e)}")
        raise

# ❌ 错误 - 捕获所有异常
async def login(email: str, password: str):
    try:
        # ...
    except Exception as e:
        print(f"错误：{e}")  # 不要使用 print
```

#### 5. 代码格式化

```bash
# 使用 ruff 格式化
ruff format .

# 使用 ruff 检查
ruff check .

# 自动修复
ruff check --fix .
```

### TypeScript 代码规范

#### 1. 严格类型

```typescript
// ✅ 正确 - 使用明确的类型
interface User {
  id: number;
  email: string;
  role: UserRole;
}

enum UserRole {
  ADMIN = "admin",
  USER = "user",
}

// ❌ 错误 - 使用 any
interface User {
  id: any;
  email: any;
}
```

#### 2. Composition API

```typescript
// ✅ 正确 - 使用 <script setup>
<script setup lang="ts">
import { ref, computed } from 'vue'

const count = ref(0)
const double = computed(() => count.value * 2)
</script>

// ❌ 错误 - 使用 Options API
<script>
export default {
  data() {
    return {
      count: 0
    }
  }
}
</script>
```

#### 3. 组件命名

```typescript
// ✅ 正确 - 使用 PascalCase
// LoginView.vue, CustomerTable.vue, AppHeader.vue

// ❌ 错误 - 使用 camelCase
// loginView.vue, customerTable.vue
```

#### 4. 代码格式化

```bash
# 使用 Prettier 格式化
npm run format

# 使用 ESLint 检查
npm run lint
```

---

## 🤖 BMAD 工作流

### 核心工作流

#### 1. 获取帮助

```bash
/bmad-help
```

#### 2. 创建产品需求

```bash
bmad-bmm-create-prd
```

#### 3. 开发用户故事

```bash
bmad-bmm-dev-story
```

#### 4. 代码审查

```bash
bmad-bmm-code-review
```

#### 5. 测试生成

```bash
bmad-tea-testarch-atdd
```

### 工作流执行规则

1. **加载配置文件**: 所有工作流必须先加载 `config.yaml`
2. **完整执行步骤**: 按顺序执行所有步骤，不跳过
3. **保存输出**: 每个 `template-output` 后立即保存
4. **用户确认**: 可选步骤询问用户（除非 #yolo 模式）

---

## 🐛 调试技巧

### 后端调试

#### 1. 使用 logging

```python
import logging

logger = logging.getLogger(__name__)

async def some_function():
    logger.debug("调试信息")
    logger.info("一般信息")
    logger.warning("警告信息")
    logger.error("错误信息")
```

#### 2. 使用断点

```python
# 在代码中插入断点
import pdb; pdb.set_trace()

# 或使用 Python 3.7+ breakpoint()
breakpoint()
```

#### 3. 查看日志

```bash
# 启动时开启详细日志
python -m app.main --log-level=DEBUG

# 或在 .env 中配置
APP_DEBUG=true
```

### 前端调试

#### 1. 浏览器 DevTools

- 按 F12 打开开发者工具
- Console 查看日志
- Network 查看 API 请求
- Vue DevTools 查看组件状态

#### 2. 使用 console.log

```typescript
// 开发环境允许使用 console
if (import.meta.env.DEV) {
  console.log("调试信息:", data);
}
```

#### 3. 使用 Vue DevTools

```bash
# 安装浏览器扩展
# Chrome: https://chrome.google.com/webstore/detail/vuejs-devtools
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/
```

---

## ❓ 常见问题

### Q1: 数据库连接失败

**错误信息**:

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**:

```bash
# 1. 检查 PostgreSQL 服务
brew services list | grep postgresql

# 2. 启动服务
brew services start postgresql@18

# 3. 检查数据库是否存在
psql -U postgres -c "\l" | grep cs_ops

# 4. 创建数据库
createdb cs_ops

# 5. 检查 .env 配置
cat backend/.env | grep DATABASE_URL
```

### Q2: 前端启动失败

**错误信息**:

```
Error: Cannot find module 'vue'
```

**解决方案**:

```bash
cd frontend

# 1. 删除 node_modules 和 lock 文件
rm -rf node_modules package-lock.json

# 2. 重新安装
npm install

# 3. 清理缓存
npm cache clean --force

# 4. 重新启动
npm run dev
```

### Q3: TypeScript 类型错误

**错误信息**:

```
Cannot find module '@/views/LoginView.vue'
```

**解决方案**:

```bash
# 1. 重启 TypeScript 服务器
# VS Code: Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"

# 2. 重新加载窗口
# VS Code: Cmd/Ctrl + Shift + P → "Developer: Reload Window"

# 3. 检查 tsconfig.json
cat frontend/tsconfig.json | grep -A 5 "paths"
```

### Q4: 测试覆盖率不达标

**目标**: 95%

**解决方案**:

```bash
# 1. 查看覆盖率报告
cd backend
pytest --cov=app --cov-report=html

# 2. 打开报告
open htmlcov/index.html

# 3. 针对红色（未覆盖）的文件编写测试
```

### Q5: BMAD 工作流不执行

**错误信息**:

```
配置文件加载失败
```

**解决方案**:

```bash
# 1. 检查 config.yaml 是否存在
ls -la _bmad/bmm/config.yaml

# 2. 检查配置文件内容
cat _bmad/bmm/config.yaml

# 3. 检查工作流文件
ls -la _bmad/bmm/workflows/
```

---

## 🎯 开发检查清单

### 提交前检查

- [ ] 代码通过类型检查（mypy / vue-tsc）
- [ ] 代码通过 lint 检查（ruff / ESLint）
- [ ] 单元测试通过（pytest / Vitest）
- [ ] 测试覆盖率达标（≥95%）
- [ ] 提交信息符合规范
- [ ] 更新了相关文档

### 发布前检查

- [ ] 所有测试通过
- [ ] 生产构建成功
- [ ] 环境变量已更新
- [ ] 数据库迁移已准备
- [ ] 回滚方案已准备
- [ ] 监控已配置

---

## 📚 相关文档

- [项目概述](README.md)
- [架构设计](architecture.md)
- [API 文档](api.md)
- [部署指南](deployment.md)

---

**最后更新**: 2026-02-28  
**维护者**: Sacrtap
