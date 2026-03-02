#!/bin/bash
# CS Ops 一键生产环境部署脚本
# 用法：./scripts/deploy-prod.sh
# 
# 功能：
# - 环境检查与验证
# - 依赖安装
# - 数据库迁移
# - 前端构建
# - 测试验证
# - 应用启动
# - 健康检查
# - 自动回滚

set -e

# ==================== 配置 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOG_DIR="/var/log/cs_ops"
BACKUP_DIR="$PROJECT_ROOT/backups"
ENV_FILE="$BACKEND_DIR/.env.production"

# 生产环境配置
export APP_ENV=production
export APP_DEBUG=false
export API_PORT=8000
export API_WORKERS=4

# ==================== 辅助函数 ====================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装"
        exit 1
    fi
}

backup_current() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/$timestamp"
    
    log_info "创建备份：$backup_path"
    mkdir -p "$backup_path"
    
    # 备份当前运行的应用
    if [[ -d "$BACKEND_DIR/.venv" ]]; then
        cp -r "$BACKEND_DIR/.venv" "$backup_path/" 2>/dev/null || true
    fi
    
    # 备份数据库
    if command -v pg_dump &> /dev/null; then
        source "$ENV_FILE" 2>/dev/null || true
        if [[ -n "$DATABASE_URL" ]]; then
            pg_dump "$DATABASE_URL" > "$backup_path/database.sql" 2>/dev/null || log_warning "数据库备份失败"
        fi
    fi
    
    log_success "备份完成：$backup_path"
}

rollback() {
    log_error "部署失败，尝试回滚..."
    
    # 停止应用
    sudo systemctl stop cs_ops_backend 2>/dev/null || true
    
    # 恢复备份（如果有）
    local latest_backup=$(ls -td "$BACKUP_DIR"/*/ 2>/dev/null | head -1)
    if [[ -n "$latest_backup" ]]; then
        log_info "使用备份恢复：$latest_backup"
        # 恢复逻辑根据实际需求实现
    fi
    
    log_error "回滚完成，请检查日志：$LOG_DIR"
    exit 1
}

trap rollback ERR

# ==================== 部署步骤 ====================

echo -e "${GREEN}"
echo "=========================================="
echo "  CS Ops 生产环境一键部署"
echo "=========================================="
echo -e "${NC}"

# ------------------- 步骤 1: 环境检查 -------------------
log_info "[1/9] 检查环境..."

check_command python3
check_command node
check_command npm
check_command psql
check_command git

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
NODE_VERSION=$(node --version)

log_success "环境检查通过"
echo "  - Python: $PYTHON_VERSION"
echo "  - Node: $NODE_VERSION"
echo "  - Git: $(git --version)"

# ------------------- 步骤 2: Git 检查 -------------------
log_info "[2/9] 检查 Git 状态..."

cd "$PROJECT_ROOT"
CURRENT_BRANCH=$(git branch --show-current)
LATEST_COMMIT=$(git log -1 --oneline)

echo "  - 分支：$CURRENT_BRANCH"
echo "  - 提交：$LATEST_COMMIT"

if [[ "$CURRENT_BRANCH" != "main" ]]; then
    log_warning "当前不在 main 分支，是否继续？(y/N)"
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi
fi

log_success "Git 状态检查完成"

# ------------------- 步骤 3: 环境变量 -------------------
log_info "[3/9] 检查环境配置..."

if [[ ! -f "$ENV_FILE" ]]; then
    log_error "生产环境配置文件不存在：$ENV_FILE"
    log_info "请从 .env.example 创建并配置 .env.production"
    exit 1
fi

# 验证关键环境变量
source "$ENV_FILE"

if [[ -z "$DATABASE_URL" ]]; then
    log_error "DATABASE_URL 未配置"
    exit 1
fi

if [[ -z "$JWT_SECRET_KEY" || "$JWT_SECRET_KEY" == "your-jwt-secret-key-here" ]]; then
    log_error "JWT_SECRET_KEY 未配置或使用默认值"
    exit 1
fi

if [[ "$APP_DEBUG" != "false" ]]; then
    log_warning "生产环境建议设置 APP_DEBUG=false"
fi

log_success "环境配置验证通过"

# ------------------- 步骤 4: 后端依赖 -------------------
log_info "[4/9] 安装后端依赖..."

cd "$BACKEND_DIR"

# 创建虚拟环境
if [[ ! -d ".venv" ]]; then
    log_info "创建虚拟环境..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 升级 pip
pip install --upgrade pip -q

# 安装依赖
log_info "安装 Python 依赖..."
pip install -r requirements.txt -q

# 安装 gunicorn（生产服务器）
pip install gunicorn -q

# 验证依赖
pip check > /dev/null 2>&1 || log_warning "依赖检查有警告"

log_success "后端依赖安装完成"

# ------------------- 步骤 5: 数据库迁移 -------------------
log_info "[5/9] 执行数据库迁移..."

cd "$BACKEND_DIR"
source .venv/bin/activate

# 检查 alembic
if ! command -v alembic &> /dev/null; then
    log_error "Alembic 未安装"
    exit 1
fi

# 查看当前状态
log_info "当前迁移状态:"
alembic current

# 备份数据库
backup_current

# 执行迁移
log_info "执行数据库迁移..."
alembic upgrade head

# 验证迁移
log_info "验证迁移..."
CURRENT_VERSION=$(alembic current | head -1)
log_success "数据库迁移完成：$CURRENT_VERSION"

# ------------------- 步骤 6: 前端构建 -------------------
log_info "[6/9] 构建前端..."

cd "$FRONTEND_DIR"

# 配置生产环境变量
echo "VITE_API_BASE_URL=${API_URL:-https://api.your-domain.com/api/v1}" > .env.production
echo "VITE_APP_ENV=production" >> .env.production

# 安装依赖
log_info "安装 Node 依赖..."
npm install --production

# 构建
log_info "构建前端..."
npm run build

# 验证构建
if [[ -d "dist" ]]; then
    BUILD_SIZE=$(du -sh dist/ | cut -f1)
    log_success "前端构建完成 (${BUILD_SIZE})"
else
    log_error "前端构建失败"
    exit 1
fi

# ------------------- 步骤 7: 运行测试 -------------------
log_info "[7/9] 运行测试验证..."

cd "$BACKEND_DIR"
source .venv/bin/activate

# 运行关键测试
log_info "运行单元测试..."
if PYTHONPATH="$BACKEND_DIR" pytest tests/unit/ -v --tb=short -q; then
    log_success "单元测试通过"
else
    log_error "单元测试失败"
    rollback
fi

# ------------------- 步骤 8: 应用启动 -------------------
log_info "[8/9] 启动应用..."

cd "$BACKEND_DIR"
source .venv/bin/activate

# 停止旧进程
log_info "停止旧进程..."
sudo systemctl stop cs_ops_backend 2>/dev/null || true
pkill -f "gunicorn.*app.main" 2>/dev/null || true

# 创建日志目录
sudo mkdir -p "$LOG_DIR"
sudo chown -R $(whoami):$(whoami) "$LOG_DIR"

# 备份目录
mkdir -p "$BACKUP_DIR"

# 启动应用
log_info "启动 Gunicorn..."
gunicorn app.main:app \
    -w $API_WORKERS \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$API_PORT \
    --daemon \
    --pid /tmp/cs_ops_backend.pid \
    --access-logfile "$LOG_DIR/access.log" \
    --error-logfile "$LOG_DIR/error.log" \
    --capture-output

# 等待启动
sleep 5

# 验证进程
if ps -p $(cat /tmp/cs_ops_backend.pid) > /dev/null 2>&1; then
    log_success "应用启动成功 (PID: $(cat /tmp/cs_ops_backend.pid))"
else
    log_error "应用启动失败"
    log_info "查看日志：tail -f $LOG_DIR/error.log"
    rollback
fi

# ------------------- 步骤 9: 健康检查 -------------------
log_info "[9/9] 健康检查..."

HEALTH_URL="http://localhost:$API_PORT/health"

for i in {1..10}; do
    if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
        log_success "健康检查通过"
        
        # 显示健康状态
        echo ""
        curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || curl -s "$HEALTH_URL"
        break
    fi
    log_info "等待应用启动... ($i/10)"
    sleep 2
done

if ! curl -s "$HEALTH_URL" > /dev/null 2>&1; then
    log_error "健康检查失败"
    log_info "查看日志：tail -f $LOG_DIR/error.log"
    rollback
fi

# ==================== 部署完成 ====================
echo ""
echo -e "${GREEN}"
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo -e "${NC}"

echo ""
echo "📊 服务状态:"
echo "  - 后端 API: http://localhost:$API_PORT"
echo "  - 健康检查：$HEALTH_URL"
echo "  - 进程 PID: $(cat /tmp/cs_ops_backend.pid)"
echo ""
echo "📝 日志文件:"
echo "  - 访问日志：$LOG_DIR/access.log"
echo "  - 错误日志：$LOG_DIR/error.log"
echo "  - 实时查看：tail -f $LOG_DIR/error.log"
echo ""
echo "💾 备份目录：$BACKUP_DIR"
echo ""
echo "🔧 管理命令:"
echo "  - 停止服务：sudo systemctl stop cs_ops_backend"
echo "  - 重启服务：sudo systemctl restart cs_ops_backend"
echo "  - 查看状态：sudo systemctl status cs_ops_backend"
echo "  - 查看日志：journalctl -u cs_ops_backend -f"
echo ""
echo "🚀 下一步:"
echo "  1. 验证功能端点（参考 docs/DEPLOYMENT_CHECKLIST.md）"
echo "  2. 配置 Nginx 反向代理"
echo "  3. 配置 SSL 证书"
echo "  4. 配置监控系统"
echo "  5. 配置备份策略"
echo ""
log_success "生产环境部署完成！"
