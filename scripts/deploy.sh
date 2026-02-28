#!/bin/bash
# CS Ops 部署脚本
# 用法：./scripts/deploy.sh [environment]
# 环境：development | staging | production

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
ENV=${1:-development}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${GREEN}======================================"
echo -e "CS Ops 部署脚本"
echo -e "环境：${YELLOW}$ENV${NC}"
echo -e "======================================${NC}"

# ==================== 1. 环境检查 ====================
echo -e "\n${YELLOW}[1/8] 检查环境...${NC}"

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本：$PYTHON_VERSION"

# 检查 Node 版本
NODE_VERSION=$(node --version)
echo "Node 版本：$NODE_VERSION"

# 检查 PostgreSQL
if command -v psql &> /dev/null; then
    echo "PostgreSQL: ✅ 已安装"
else
    echo -e "${RED}PostgreSQL 未安装${NC}"
    exit 1
fi

# ==================== 2. Git 检查 ====================
echo -e "\n${YELLOW}[2/8] 检查 Git 状态...${NC}"

cd "$PROJECT_ROOT"
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}⚠️  有未提交的变更${NC}"
    read -p "是否继续部署？(y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
fi

echo "当前分支：$(git branch --show-current)"
echo "最新提交：$(git log -1 --oneline)"

# ==================== 3. 后端依赖 ====================
echo -e "\n${YELLOW}[3/8] 安装后端依赖...${NC}"

cd "$BACKEND_DIR"

# 创建虚拟环境（如果不存在）
if [[ ! -d ".venv" ]]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt

# 验证依赖
echo "验证依赖..."
pip check || echo -e "${YELLOW}⚠️  依赖检查警告${NC}"

# ==================== 4. 数据库迁移 ====================
echo -e "\n${YELLOW}[4/8] 执行数据库迁移...${NC}"

cd "$BACKEND_DIR"
source .venv/bin/activate

# 检查 alembic
if ! command -v alembic &> /dev/null; then
    echo -e "${RED}Alembic 未安装${NC}"
    exit 1
fi

# 查看当前迁移状态
echo "当前迁移状态:"
alembic current

# 执行迁移
echo "升级到最新版本..."
alembic upgrade head

# 验证迁移
echo "验证迁移..."
alembic current

# 验证表结构
echo "验证表结构..."
python3 << EOF
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def verify():
    import os
    # 读取 .env 文件
    env_file = '.env.production' if '$ENV' == 'production' else '.env'
    with open(env_file) as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                db_url = line.split('=', 1)[1].strip()
                break
    
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        # 检查 users 表
        result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('users', 'token_blacklists')
        """))
        tables = [row[0] for row in result]
        print(f"找到的表：{tables}")
        
        if 'users' not in tables or 'token_blacklists' not in tables:
            raise Exception("表结构验证失败")
        
        print("✅ 表结构验证通过")
    
    await engine.dispose()

asyncio.run(verify())
EOF

# ==================== 5. 前端构建 ====================
echo -e "\n${YELLOW}[5/8] 构建前端...${NC}"

cd "$FRONTEND_DIR"

# 安装依赖
echo "安装 Node 依赖..."
npm install

# 构建生产版本
echo "构建前端..."
npm run build

# 验证构建
if [[ -d "dist" ]]; then
    echo "✅ 前端构建成功"
    ls -lh dist/
else
    echo -e "${RED}前端构建失败${NC}"
    exit 1
fi

# ==================== 6. 运行测试 ====================
echo -e "\n${YELLOW}[6/8] 运行测试...${NC}"

cd "$BACKEND_DIR"
source .venv/bin/activate

# 运行单元测试
echo "运行单元测试..."
PYTHONPATH="$BACKEND_DIR" pytest tests/unit/ -v --tb=short

# 检查测试结果
if [[ $? -eq 0 ]]; then
    echo "✅ 单元测试通过"
else
    echo -e "${RED}单元测试失败${NC}"
    exit 1
fi

# ==================== 7. 应用启动 ====================
echo -e "\n${YELLOW}[7/8] 启动应用...${NC}"

cd "$BACKEND_DIR"
source .venv/bin/activate

# 检查端口占用
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  端口 $PORT 被占用${NC}"
    read -p "是否继续？(y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
fi

# 启动应用（后台）
echo "启动应用（端口 $PORT）..."
gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --daemon

# 等待应用启动
echo "等待应用启动..."
sleep 5

# 检查应用状态
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ 应用启动成功"
else
    echo -e "${RED}应用启动失败${NC}"
    exit 1
fi

# ==================== 8. 健康检查 ====================
echo -e "\n${YELLOW}[8/8] 健康检查...${NC}"

# 健康检查端点
HEALTH_URL="http://localhost:$PORT/health"

echo "检查健康状态..."
for i in {1..10}; do
    if curl -s $HEALTH_URL > /dev/null; then
        echo "✅ 健康检查通过"
        break
    fi
    echo "等待中... ($i/10)"
    sleep 2
done

# 最终检查
if ! curl -s $HEALTH_URL > /dev/null; then
    echo -e "${RED}健康检查失败${NC}"
    exit 1
fi

# 显示健康状态
curl -s $HEALTH_URL | python3 -m json.tool

# ==================== 完成 ====================
echo -e "\n${GREEN}======================================"
echo -e "✅ 部署完成！"
echo -e "======================================${NC}"
echo ""
echo "后端 API: http://localhost:$PORT"
echo "健康检查：$HEALTH_URL"
echo "日志查看：tail -f /var/log/cs_ops/backend.log"
echo ""
echo -e "${YELLOW}下一步:${NC}"
echo "1. 验证功能端点（参考 docs/DEPLOYMENT_CHECKLIST.md）"
echo "2. 配置监控系统"
echo "3. 配置备份策略"
echo ""
