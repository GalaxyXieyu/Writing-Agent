#!/bin/bash

# 停止开发环境服务

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== 停止 Writing Agent 开发环境 ===${NC}"

# 停止 API
if [ -f /tmp/writingagent-api.pid ]; then
    API_PID=$(cat /tmp/writingagent-api.pid)
    if ps -p $API_PID > /dev/null 2>&1; then
        echo "停止 API (PID: $API_PID)..."
        kill $API_PID
        echo -e "${GREEN}API 已停止${NC}"
    else
        echo "API 进程不存在"
    fi
    rm -f /tmp/writingagent-api.pid
fi

# 停止 Worker
if [ -f /tmp/writingagent-worker.pid ]; then
    WORKER_PID=$(cat /tmp/writingagent-worker.pid)
    if ps -p $WORKER_PID > /dev/null 2>&1; then
        echo "停止 Worker (PID: $WORKER_PID)..."
        kill $WORKER_PID
        echo -e "${GREEN}Worker 已停止${NC}"
    else
        echo "Worker 进程不存在"
    fi
    rm -f /tmp/writingagent-worker.pid
fi

# 停止 Flower
if [ -f /tmp/writingagent-flower.pid ]; then
    FLOWER_PID=$(cat /tmp/writingagent-flower.pid)
    if ps -p $FLOWER_PID > /dev/null 2>&1; then
        echo "停止 Flower (PID: $FLOWER_PID)..."
        kill $FLOWER_PID
        echo -e "${GREEN}Flower 已停止${NC}"
    else
        echo "Flower 进程不存在"
    fi
    rm -f /tmp/writingagent-flower.pid
fi

# 可选：停止 Docker 服务
read -p "是否同时停止 Docker 服务 (MySQL + Redis)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
    DEPLOY_DIR="$PROJECT_ROOT/deploy"
    
    cd "$DEPLOY_DIR"
    echo "停止 Docker 服务..."
    docker compose stop mysql redis
    echo -e "${GREEN}Docker 服务已停止${NC}"
fi

echo -e "${GREEN}=== 停止完成 ===${NC}"
