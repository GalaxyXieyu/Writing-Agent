#!/bin/bash

# 基础服务启动脚本 - 仅启动 MySQL + Redis

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  基础服务启动 (MySQL + Redis)         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker Desktop${NC}"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}🚀 启动 MySQL 和 Redis...${NC}"
docker compose up -d mysql redis

# 等待服务就绪
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"

# 等待 MySQL
for i in {1..30}; do
    if docker exec mysql mysqladmin ping -h localhost -P 3306 -u root -p123456 --silent > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MySQL 已就绪${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ MySQL 启动超时${NC}"
        exit 1
    fi
    sleep 1
done

# 等待 Redis
for i in {1..15}; do
    if docker exec redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis 已就绪${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ Redis 启动超时${NC}"
        exit 1
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}✅ 基础服务启动完成！${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📌 服务信息:${NC}"
echo -e "   MySQL:  ${YELLOW}localhost:30306${NC}"
echo -e "           用户: root"
echo -e "           密码: 123456"
echo -e "           数据库: tianshu"
echo -e ""
echo -e "   Redis:  ${YELLOW}localhost:30637${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}💡 下一步:${NC}"
echo -e "   进入 backend 目录运行: ${YELLOW}./start_dev.sh${NC}"
echo ""
