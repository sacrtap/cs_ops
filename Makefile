# Makefile - 内部运营中台客户信息管理与运营系统
# 
# 用途：统一管理和运行测试命令
# ===========================================

# ===========================================
# 变量定义
# ===========================================

PYTHON := python3
PIP := pip
NODE := node
NPM := npm
PYTEST := pytest
PLAYWRIGHT := npx playwright

# 测试目录
TEST_DIR := tests
TEST_REPORT_DIR := test-results
COVERAGE_DIR := test-results/coverage-html

# 测试标记
PYTEST_MARKS := unit integration api e2e

# 覆盖率要求
COVERAGE_FAIL_UNDER := 95

# ===========================================
# 默认目标
# ===========================================

.DEFAULT_GOAL := help

.PHONY: help
help: ## 显示帮助信息
	@echo "内部运营中台客户信息管理与运营系统 - 测试命令"
	@echo "=========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ===========================================
# 安装与设置
# ===========================================

.PHONY: install install-frontend install-backend install-playwright
install: install-backend install-frontend install-playwright ## 安装所有依赖

install-frontend: ## 安装前端依赖
	@echo "正在安装前端依赖..."
	$(NPM) install

install-backend: ## 安装后端依赖
	@echo "正在安装后端依赖..."
	$(PYTHON) -m pip install -e ".[dev]"

install-playwright: ## 安装 Playwright 浏览器
	@echo "正在安装 Playwright 浏览器..."
	$(PLAYWRIGHT) install
	@echo "Playwright 安装完成"

.PHONY: setup-env
setup-env: ## 设置测试环境
	@echo "正在设置测试环境..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "已创建 .env 文件，请根据实际环境修改配置"; \
	else \
		echo ".env 文件已存在"; \
	fi

# ===========================================
# 运行测试 - 后端 (pytest)
# ===========================================

.PHONY: test test-backend test-api test-unit test-integration test-cov
test: test-backend ## 运行所有后端测试

test-backend: ## 运行所有后端测试
	@echo "正在运行后端测试..."
	$(PYTEST) $(TEST_DIR)/ -v --tb=short

test-api: ## 运行 API 测试
	@echo "正在运行 API 测试..."
	$(PYTEST) $(TEST_DIR)/api/ -v -m api --tb=short

test-unit: ## 运行单元测试
	@echo "正在运行单元测试..."
	$(PYTEST) $(TEST_DIR)/unit/ -v -m unit --tb=short

test-integration: ## 运行集成测试
	@echo "正在运行集成测试..."
	$(PYTEST) $(TEST_DIR)/ -v -m integration --tb=short

test-cov: ## 运行测试并生成覆盖率报告
	@echo "正在运行测试并生成覆盖率报告..."
	$(PYTEST) $(TEST_DIR)/ -v --tb=short \
		--cov=backend \
		--cov-report=term-missing \
		--cov-report=html:$(COVERAGE_DIR) \
		--cov-report=xml:$(TEST_REPORT_DIR)/coverage.xml \
		--cov-fail-under=$(COVERAGE_FAIL_UNDER)
	@echo "覆盖率报告已生成：$(COVERAGE_DIR)/index.html"

test-customer: ## 运行客户管理相关测试
	@echo "正在运行客户管理测试..."
	$(PYTEST) $(TEST_DIR)/ -v -m customer --tb=short

test-billing: ## 运行结算管理相关测试
	@echo "正在运行结算管理测试..."
	$(PYTEST) $(TEST_DIR)/ -v -m billing --tb=short

test-health: ## 运行健康度监控相关测试
	@echo "正在运行健康度监控测试..."
	$(PYTEST) $(TEST_DIR)/ -v -m health --tb=short

# ===========================================
# 运行测试 - 前端 (Playwright + Vitest)
# ===========================================

.PHONY: test-frontend test-e2e test-e2e-ui test-e2e-headed test-e2e-debug
test-frontend: test-e2e test-unit-frontend ## 运行所有前端测试

test-e2e: ## 运行 E2E 测试（无头模式）
	@echo "正在运行 E2E 测试..."
	$(PLAYWRIGHT) test

test-e2e-ui: ## 运行 E2E 测试（UI 模式）
	@echo "正在启动 Playwright UI 模式..."
	$(PLAYWRIGHT) test --ui

test-e2e-headed: ## 运行 E2E 测试（有头模式）
	@echo "正在运行 E2E 测试（有头模式）..."
	$(PLAYWRIGHT) test --headed

test-e2e-debug: ## 运行 E2E 测试（调试模式）
	@echo "正在启动 Playwright 调试模式..."
	$(PLAYWRIGHT) test --debug

test-e2e-chromium: ## 仅运行 Chromium 浏览器测试
	@echo "正在运行 Chromium 浏览器测试..."
	$(PLAYWRIGHT) test --project=chromium

test-e2e-firefox: ## 仅运行 Firefox 浏览器测试
	@echo "正在运行 Firefox 浏览器测试..."
	$(PLAYWRIGHT) test --project=firefox

test-e2e-webkit: ## 仅运行 WebKit 浏览器测试
	@echo "正在运行 WebKit 浏览器测试..."
	$(PLAYWRIGHT) test --project=webkit

test-e2e-mobile: ## 运行移动端测试
	@echo "正在运行移动端测试..."
	$(PLAYWRIGHT) test --project='Mobile Chrome' --project='Mobile Safari'

test-unit-frontend: ## 运行前端单元测试
	@echo "正在运行前端单元测试..."
	$(NPM) run test

test-unit-frontend-ui: ## 运行前端单元测试（UI 模式）
	@echo "正在启动 Vitest UI 模式..."
	$(NPM) run test:ui

test-e2e-report: ## 查看 E2E 测试报告
	@echo "正在打开 E2E 测试报告..."
	$(PLAYWRIGHT) show-report

test-e2e-trace: ## 查看 E2E 测试追踪
	@echo "正在打开 E2E 测试追踪..."
	$(PLAYWRIGHT) show-trace

# ===========================================
# 特定模块测试
# ===========================================

.PHONY: test-customer-e2e test-billing-e2e test-auth-e2e
test-customer-e2e: ## 运行客户管理 E2E 测试
	@echo "正在运行客户管理 E2E 测试..."
	$(PLAYWRIGHT) test $(TEST_DIR)/e2e/customer/

test-billing-e2e: ## 运行结算管理 E2E 测试
	@echo "正在运行结算管理 E2E 测试..."
	$(PLAYWRIGHT) test $(TEST_DIR)/e2e/billing/

test-auth-e2e: ## 运行认证授权 E2E 测试
	@echo "正在运行认证授权 E2E 测试..."
	$(PLAYWRIGHT) test $(TEST_DIR)/e2e/auth/

# ===========================================
# 代码质量
# ===========================================

.PHONY: lint lint-backend lint-frontend format
lint: lint-backend lint-frontend ## 运行所有代码检查

lint-backend: ## 检查后端代码质量
	@echo "正在检查后端代码..."
	@$(PYTHON) -m ruff check backend/
	@$(PYTHON) -m mypy backend/

lint-frontend: ## 检查前端代码质量
	@echo "正在检查前端代码..."
	$(NPM) run lint

format: format-backend format-frontend ## 格式化所有代码

format-backend: ## 格式化后端代码
	@echo "正在格式化后端代码..."
	@$(PYTHON) -m ruff format backend/
	@$(PYTHON) -m ruff check --fix backend/

format-frontend: ## 格式化前端代码
	@echo "正在格式化前端代码..."
	$(NPM) run format

# ===========================================
# 清理
# ===========================================

.PHONY: clean clean-test clean-cov
clean: clean-test clean-cov ## 清理所有生成的文件

clean-test: ## 清理测试产物
	@echo "正在清理测试产物..."
	@rm -rf $(TEST_REPORT_DIR)/
	@rm -rf playwright-report/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "测试产物清理完成"

clean-cov: ## 清理覆盖率报告
	@echo "正在清理覆盖率报告..."
	@rm -rf $(COVERAGE_DIR)/
	@rm -f $(TEST_REPORT_DIR)/coverage.xml
	@echo "覆盖率报告清理完成"

# ===========================================
# 开发服务器
# ===========================================

.PHONY: dev dev-backend dev-frontend
dev: ## 同时启动前后端开发服务器
	@echo "正在启动开发服务器..."
	@echo "提示：使用 'make dev-backend' 和 'make dev-frontend' 分别启动"

dev-backend: ## 启动后端开发服务器
	@echo "正在启动后端开发服务器..."
	@$(PYTHON) -m sanic backend.app:app --debug --auto-reload

dev-frontend: ## 启动前端开发服务器
	@echo "正在启动前端开发服务器..."
	$(NPM) run dev

# ===========================================
# CI/CD
# ===========================================

.PHONY: ci-test ci-test-backend ci-test-frontend
ci-test: ci-test-backend ci-test-frontend ## CI 环境运行所有测试

ci-test-backend: ## CI 环境运行后端测试
	@echo "[CI] 运行后端测试..."
	$(PYTEST) $(TEST_DIR)/ -v --tb=short \
		--cov=backend \
		--cov-report=xml:$(TEST_REPORT_DIR)/coverage.xml \
		--junitxml=$(TEST_REPORT_DIR)/junit-backend.xml \
		-n auto

ci-test-frontend: ## CI 环境运行前端测试
	@echo "[CI] 运行前端测试..."
	$(NPM) run test
	$(PLAYWRIGHT) test --reporter=list,junit

# ===========================================
# 部署
# ===========================================

.PHONY: deploy deploy-dev deploy-prod deploy-docker
deploy: deploy-dev ## 部署到开发环境

deploy-dev: ## 部署到开发环境
	@echo "部署到开发环境..."
	./scripts/deploy.sh development

deploy-prod: ## 部署到生产环境
	@echo "部署到生产环境..."
	@echo "警告：这将部署到生产环境！"
	./scripts/deploy-prod.sh

deploy-docker: ## 使用 Docker Compose 部署
	@echo "使用 Docker Compose 部署..."
	docker-compose up -d
	docker-compose --profile migrate up migrate

.PHONY: docker-build docker-up docker-down docker-logs
docker-build: ## 构建 Docker 镜像
	@echo "构建 Docker 镜像..."
	docker-compose build

docker-up: ## 启动 Docker 服务
	@echo "启动 Docker 服务..."
	docker-compose up -d

docker-down: ## 停止 Docker 服务
	@echo "停止 Docker 服务..."
	docker-compose down

docker-logs: ## 查看 Docker 日志
	@echo "查看 Docker 日志..."
	docker-compose logs -f

.PHONY: backup-db
backup-db: ## 备份数据库
	@echo "备份数据库..."
	@if command -v pg_dump &> /dev/null; then \
		mkdir -p backups; \
		pg_dump $(DATABASE_URL) > backups/backup_$$(date +%Y%m%d_%H%M%S).sql; \
		echo "备份完成"; \
	else \
		echo "pg_dump 未安装"; \
	fi
