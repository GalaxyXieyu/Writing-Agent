# Writing-Agent

AI写作助手系统 - 基于FastAPI + Vue3 + Celery的智能写作平台

## 快速开始

### 开发环境启动

```bash
# 启动所有服务（开发模式，支持热重载）
cd deploy
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
docker-compose logs -f frontend
```

### 访问地址

- **前端**: http://localhost:30080
- **API文档**: http://localhost:29847/docs
- **Flower监控**: http://localhost:30555
- **MySQL**: localhost:30306
- **Redis**: localhost:30637

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 架构概览

### 技术栈

**后端**:
- FastAPI (异步Web框架)
- SQLAlchemy 2.0 (ORM，异步模式)
- Celery (异步任务队列)
- MySQL 8.0 (数据库)
- Redis (缓存 + Celery broker)
- aiomysql (异步MySQL驱动)

**前端**:
- Vue 3 + Vite
- Element Plus
- Pinia (状态管理)

### 服务架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│     API     │────▶│    MySQL    │
│  (Vue3)     │     │  (FastAPI)  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    Redis    │◀────│   Worker    │
                    │             │     │  (Celery)   │
                    └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Flower    │
                                        │  (监控)     │
                                        └─────────────┘
```

## 数据库管理

### 管理方式

本项目使用 **SQLAlchemy ORM** 自动管理数据库表结构，不需要手动编写建表SQL。

**工作原理**:
1. 表结构定义在 `backend/models/` 目录
2. 启动时 `initialization.py` 中的 `Base.metadata.create_all()` 自动创建表
3. `migrate_database()` 函数检查并添加缺失的字段

**添加新表**:
1. 在 `backend/models/` 创建模型文件
2. 在 `initialization.py` 导入模型
3. 重启服务，表会自动创建

**添加新字段**:
- 在模型类中添加字段
- 在 `initialization.py` 的 `migrate_database()` 中添加迁移逻辑

详见: [backend/migrations/README.md](backend/migrations/README.md)

## 部署方式

### Docker Compose部署（推荐）

```bash
# 1. 克隆代码
git clone <repository-url>
cd Writing-Agent

# 2. 配置环境变量（可选）
cp backend/.env.example backend/.env
# 编辑 backend/.env 修改配置

# 3. 启动服务
cd deploy
docker-compose up -d

# 4. 查看日志确认启动成功
docker-compose logs -f
```

### 生产环境配置

**修改 `deploy/docker-compose.yml`**:
- 移除 `volumes` 挂载（避免代码热重载）
- 修改端口映射为生产端口
- 配置环境变量（数据库密码、Redis密码等）
- 添加 `restart: always` 策略

**安全建议**:
- 修改默认管理员密码
- 配置防火墙规则
- 使用HTTPS（配置Nginx反向代理）
- 定期备份MySQL数据

## 开发指南

### 后端开发

```bash
# 进入容器
docker exec -it writing-agent-api bash

# 安装依赖
pip install -r requirements.txt

# 代码已挂载，修改后自动重载
```

### 前端开发

```bash
# 进入容器
docker exec -it writing-agent-frontend sh

# 安装依赖
npm install

# 代码已挂载，修改后自动热更新
```

### 数据库操作

```bash
# 连接MySQL
docker exec -it writing-agent-mysql mysql -uroot -proot123 writing_agent

# 查看表结构
SHOW TABLES;
DESC ai_model_config;
```

## 常见问题

**Q: 前端构建失败 "cannot replace to directory...node_modules"**
A: 删除 `frontend/node_modules` 后重新构建
```bash
rm -rf frontend/node_modules
docker-compose up -d --build frontend
```

**Q: API报错 "Unknown column in 'field list'"**
A: 数据库字段缺失，检查 `initialization.py` 中的 `migrate_database()` 函数

**Q: Celery任务不执行**
A: 检查Redis连接和Worker日志
```bash
docker-compose logs worker
```

## 项目结构

```
Writing-Agent/
├── backend/              # 后端代码
│   ├── models/          # SQLAlchemy模型
│   ├── routers/         # API路由
│   ├── services/        # 业务逻辑
│   ├── tasks/           # Celery任务
│   ├── initialization.py # 数据库初始化
│   └── main.py          # FastAPI入口
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── components/ # 通用组件
│   │   └── stores/     # Pinia状态
│   └── vite.config.js
├── deploy/
│   └── docker-compose.yml # 容器编排
└── migrations/          # 数据库迁移（仅参考）
```

## 许可证

[添加许可证信息]
