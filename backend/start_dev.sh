#!/bin/bash

# 开发环境启动脚本 - 源码运行 API + Worker，Docker 运行 MySQL + Redis
# 使用方法: ./start_dev.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_ROOT/deploy"

echo -e "${GREEN}=== Writing Agent 开发环境启动脚本 ===${NC}"
echo "项目根目录: $PROJECT_ROOT"
echo "后端目录: $SCRIPT_DIR"
echo "部署目录: $DEPLOY_DIR"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker 未运行，请先启动 Docker Desktop${NC}"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${RED}错误: 虚拟环境不存在，请先运行: python3 -m venv .venv${NC}"
    exit 1
fi

# 启动 MySQL 和 Redis（如果未运行）
echo -e "${YELLOW}1. 检查并启动 Docker 服务 (MySQL + Redis)...${NC}"
cd "$DEPLOY_DIR"

# 只启动 MySQL 和 Redis
if ! docker compose ps mysql | grep -q "Up"; then
    echo "启动 MySQL..."
    docker compose up -d mysql
fi

if ! docker compose ps redis | grep -q "Up"; then
    echo "启动 Redis..."
    docker compose up -d redis
fi

# 等待 MySQL 和 Redis 就绪
echo -e "${YELLOW}2. 等待数据库服务就绪...${NC}"
echo "等待 MySQL 启动..."
for i in {1..30}; do
    if docker exec mysql mysqladmin ping -h localhost -P 3306 -u root -p123456 --silent > /dev/null 2>&1; then
        echo -e "${GREEN}MySQL 已就绪${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}MySQL 启动超时${NC}"
        exit 1
    fi
    sleep 1
done

echo "等待 Redis 启动..."
for i in {1..15}; do
    if docker exec redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}Redis 已就绪${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}Redis 启动超时${NC}"
        exit 1
    fi
    sleep 1
done

# 返回后端目录
cd "$SCRIPT_DIR"

# 创建日志目录
mkdir -p logs

# 激活虚拟环境并启动服务
echo -e "${YELLOW}3. 启动后端服务...${NC}"

# 清理之前的 PID 文件
rm -f /tmp/writingagent-api.pid /tmp/writingagent-worker.pid

# 启动 FastAPI 服务
echo "启动 API 服务 (端口 29847)..."
source .venv/bin/activate
nohup .venv/bin/python main.py > logs/api.log 2>&1 &
API_PID=$!
echo $API_PID > /tmp/writingagent-api.pid
echo -e "${GREEN}API 已启动 (PID: $API_PID)${NC}"

# 启动 Celery Worker
echo "启动 Celery Worker..."
nohup .venv/bin/celery -A tasks.celery_app worker --loglevel=info --concurrency=4 -E > logs/worker.log 2>&1 &
WORKER_PID=$!
echo $WORKER_PID > /tmp/writingagent-worker.pid
echo -e "${GREEN}Worker 已启动 (PID: $WORKER_PID)${NC}"

# 可选：启动 Flower 监控
read -p "是否启动 Flower 监控界面? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "启动 Flower (端口 5555)..."
    nohup .venv/bin/celery -A tasks.celery_app flower --port=5555 > logs/flower.log 2>&1 &
    FLOWER_PID=$!
    echo $FLOWER_PID > /tmp/writingagent-flower.pid
    echo -e "${GREEN}Flower 已启动 (PID: $FLOWER_PID) - http://localhost:5555${NC}"
fi

echo ""
echo -e "${GREEN}=== 启动完成 ===${NC}"
echo -e "API 服务: ${GREEN}http://localhost:29847${NC}"
echo -e "API 日志: ${YELLOW}tail -f logs/api.log${NC}"
echo -e "Worker 日志: ${YELLOW}tail -f logs/worker.log${NC}"
echo ""
echo -e "停止服务: ${YELLOW}./stop_dev.sh${NC}"
echo -e "查看状态: ${YELLOW}./status_dev.sh${NC}"
