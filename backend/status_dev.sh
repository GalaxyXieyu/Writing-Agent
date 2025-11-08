#!/bin/bash

# 查看开发环境服务状态

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Writing Agent 服务状态 ===${NC}"
echo ""

# 检查 Docker 服务
echo -e "${YELLOW}Docker 服务:${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_ROOT/deploy"

if docker info > /dev/null 2>&1; then
    cd "$DEPLOY_DIR"
    docker compose ps mysql redis
else
    echo -e "${RED}Docker 未运行${NC}"
fi

echo ""
echo -e "${YELLOW}后端服务:${NC}"

# 检查 API
if [ -f /tmp/writingagent-api.pid ]; then
    API_PID=$(cat /tmp/writingagent-api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        echo -e "API: ${GREEN}运行中${NC} (PID: $API_PID, 端口: 29847)"
    else
        echo -e "API: ${RED}已停止${NC} (PID 文件存在但进程不存在)"
    fi
else
    echo -e "API: ${RED}未启动${NC}"
fi

# 检查 Worker
if [ -f /tmp/writingagent-worker.pid ]; then
    WORKER_PID=$(cat /tmp/writingagent-worker.pid)
    if ps -p $WORKER_PID > /dev/null 2>&1; then
        echo -e "Worker: ${GREEN}运行中${NC} (PID: $WORKER_PID)"
    else
        echo -e "Worker: ${RED}已停止${NC} (PID 文件存在但进程不存在)"
    fi
else
    echo -e "Worker: ${RED}未启动${NC}"
fi

# 检查 Flower
if [ -f /tmp/writingagent-flower.pid ]; then
    FLOWER_PID=$(cat /tmp/writingagent-flower.pid)
    if ps -p $FLOWER_PID > /dev/null 2>&1; then
        echo -e "Flower: ${GREEN}运行中${NC} (PID: $FLOWER_PID, 端口: 5555)"
    else
        echo -e "Flower: ${RED}已停止${NC} (PID 文件存在但进程不存在)"
    fi
else
    echo -e "Flower: ${YELLOW}未启动${NC}"
fi

echo ""
echo -e "${YELLOW}快速访问:${NC}"
echo -e "API 文档: http://localhost:29847/docs"
echo -e "Flower 监控: http://localhost:5555"
