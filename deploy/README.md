# 部署文档

## 快速启动指南

### 1. 启动所有服务（MySQL、Redis、Celery Worker、Flower）

在 `deploy` 目录下执行：

```bash
cd deploy
docker-compose up -d
```

查看服务状态：
```bash
docker-compose ps
```

查看日志：
```bash
docker-compose logs -f mysql
docker-compose logs -f redis
docker-compose logs -f celery-worker
docker-compose logs -f flower
```

### 2. 初始化数据库

等待 MySQL 服务完全启动后（约10-30秒），执行初始化脚本：

```bash
cd deploy
python3 init_db.py
```

初始化脚本会：
- 自动创建所有数据库表
- 插入测试用户账号
- 生成测试数据

### 3. 启动后端服务

```bash
cd backend
python3 main.py
```

后端服务将在 `http://localhost:29847` 启动

### 4. 测试登录接口

使用以下命令测试登录：

```bash
curl -X POST http://localhost:29847/api/v2/solution/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 测试账号

系统预置了以下测试账号：

| 用户名 | 密码 | 说明 |
|--------|------|------|
| admin | admin123 | 管理员账号 |
| test | test123 | 测试账号 |

## 数据库配置

### 默认配置

- **主机**: localhost
- **端口**: 30306 (宿主机) -> 3306 (容器内)
- **数据库**: tianshu
- **用户名**: root
- **密码**: 123456

### 环境变量配置

可以通过环境变量覆盖默认配置：

```bash
export DB_HOST=localhost
export DB_PORT=30306
export DB_USER=root
export DB_PASSWORD=123456
export DB_NAME=tianshu
export REDIS_HOST=localhost
export REDIS_PORT=30637
export REDIS_DB=0
```

## 数据库表结构

系统包含以下数据库表：

1. **ai_user** - 用户表
2. **ai_user_token** - 用户Token表
3. **ai_solution_save** - 方案保存表
4. **ai_file_rel** - 文件关联表
5. **ai_writing_template** - 写作模板表
6. **ai_template_title** - 模板标题表
7. **ai_create_template** - AI生成模板表
8. **ai_usually_template** - 常用模板表
9. **ai_task** - 异步任务表（新增）

## Celery 异步任务

### 服务说明

- **Redis**: 消息队列和任务结果存储（宿主机端口 30637）
- **Celery Worker**: 后台任务执行器
- **Flower**: Celery 任务监控界面（宿主机端口 30555）

### 访问 Flower 监控界面

打开浏览器访问：`http://localhost:30555`

### 异步任务 API

#### 提交文章生成任务

**POST** `/api/tasks/generate-article`

请求体：
```json
{
  "outline": {...},
  "templateId": "xxx",
  "userId": "xxx"
}
```

响应：
```json
{
  "code": 200,
  "message": "任务已提交",
  "type": "success",
  "data": {
    "task_id": "uuid-string"
  }
}
```

#### SSE 流式获取任务结果

**GET** `/api/tasks/{task_id}/stream`

支持断线重连，会自动从 Redis Stream 读取所有已生成内容并流式返回。

#### 查询任务状态

**GET** `/api/tasks/{task_id}`

#### 查询用户任务列表

**GET** `/api/tasks/user/{user_id}`

#### 取消任务

**POST** `/api/tasks/{task_id}/cancel`

## 常用操作

### 停止服务

```bash
cd deploy
docker-compose down
```

### 重启服务

```bash
cd deploy
docker-compose restart
```

### 查看MySQL日志

```bash
cd deploy
docker-compose logs -f mysql
```

### 连接到MySQL

```bash
mysql -h 127.0.0.1 -P 30306 -u root -p123456 tianshu
```

或使用Docker：

```bash
docker exec -it writingagent-mysql mysql -uroot -p123456 tianshu
```

### 重新初始化数据库

如果需要重新初始化数据库（会删除所有数据）：

```bash
cd deploy
docker-compose down -v
docker-compose up -d
# 等待MySQL启动
sleep 10
python3 init_db.py
```

## 故障排查

### 1. 无法连接数据库

检查MySQL服务是否启动：
```bash
docker-compose ps
```

检查端口是否被占用：
```bash
lsof -i :30306
```

### 2. 初始化失败

查看详细错误信息：
```bash
cd deploy
python3 init_db.py
```

确保MySQL已完全启动（等待10-30秒）

### 3. 登录接口返回500错误

检查后端日志，确认数据库连接配置是否正确

## API接口文档

### 登录接口

**POST** `/api/v2/solution/login`

请求体：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "type": "success",
  "data": {
    "token": "abc123...",
    "user_id": "admin",
    "username": "admin",
    "name": "管理员"
  }
}
```

### Token验证接口

**POST** `/api/v2/solution/checkToken`

请求体：
```json
{
  "key": "abc123..."
}
```

响应：
```json
{
  "code": 200,
  "message": "Token有效",
  "type": "success",
  "data": {
    "user_id": "admin",
    "username": "admin",
    "name": "管理员"
  }
}
```

## 注意事项

1. Token有效期为7天
2. 密码为明文存储（生产环境需要加密）
3. 数据持久化在 `./mysql_data` 目录
4. 首次启动可能需要等待MySQL完全初始化

