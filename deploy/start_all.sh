#!/bin/bash

# 完全 Docker 化启动脚本 - 一键启动所有服务

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Writing Agent - Docker 一键启动       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 未运行，请先启动 Docker Desktop${NC}"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 清理旧容器（可选）
read -p "$(echo -e ${YELLOW}是否清理旧容器和数据？ [y/N]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 清理旧容器...${NC}"
    docker compose down -v
fi

# 构建并启动所有服务
echo -e "${YELLOW}🔨 构建镜像...${NC}"
docker compose build

echo -e "${YELLOW}🚀 启动所有服务...${NC}"
docker compose up -d

# 等待服务就绪
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

# 检查服务状态
echo ""
echo -e "${GREEN}📊 服务状态:${NC}"
docker compose ps

echo ""
echo -e "${GREEN}✅ 启动完成！${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📌 服务访问地址:${NC}"
echo -e "   API 文档:    ${YELLOW}http://localhost:29847/docs${NC}"
echo -e "   Frontend:    ${YELLOW}http://localhost:30080${NC}"
echo -e "   Flower:      ${YELLOW}http://localhost:30555${NC}"
echo -e "   MySQL:       ${YELLOW}localhost:30306${NC} (用户: root, 密码: 123456)"
echo -e "   Redis:       ${YELLOW}localhost:30637${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📝 常用命令:${NC}"
echo -e "   查看日志:    ${YELLOW}docker compose logs -f [service]${NC}"
echo -e "   重启服务:    ${YELLOW}docker compose restart [service]${NC}"
echo -e "   停止服务:    ${YELLOW}docker compose down${NC}"
echo -e "   查看状态:    ${YELLOW}docker compose ps${NC}"
echo ""
