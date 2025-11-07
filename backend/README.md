# SmartAgent 2.0

## 1. 项目简介

(请在这里填写项目的具体介绍，例如：SmartAgent 2.0 是一个用于...的智能代理项目，主要功能包括...)

## 2. 项目结构

```
smartagent2.0/
├── .git/               # Git 版本控制目录
├── .idea/              # IDE (例如 PyCharm) 配置目录
├── __pycache__/        # Python 编译的缓存文件
├── ai/                 # AI 相关模块
├── api/                # API 接口定义和实现
├── logs/               # 项目运行日志目录
├── models/             # 数据模型或机器学习模型
├── services/           # 业务逻辑服务层
├── templates/          # (如果存在)Web应用的HTML模板
├── tests/              # 测试代码
├── utils/              # 工具函数模块
├── venv/               # Python 虚拟环境目录
├── config.json         # 项目配置文件
├── Dockerfile          # Docker 配置文件
├── initialization.py   # 项目初始化脚本
├── logging_config.py   # 日志配置脚本
├── main.py             # 项目主入口文件
├── markdown.txt        # (用途待确认)
├── nohup.out           # nohup 命令的默认输出文件
├── requirements.txt    # Python 依赖包列表
├── requirements_copy.txt # Python 依赖包列表备份
├── solution-assistant-new.tar  # (用途待确认)
├── solution-assistant-update.tar # (用途待确认)
├── test.ipynb          # Jupyter Notebook 测试文件
└── 部署步骤.md         # 部署步骤文档 (当前为空)
```

## 3. 环境配置与启动方法

### 3.1 环境准备

本项目建议使用 Conda 来管理环境。

**激活 Conda 环境**:
    ```bash
    conda activate /data/xieyu/smartagent2.0/venv
    ```

### 3.2 启动服务

使用以下命令在后台启动 `main.py` 服务：

```bash
nohup python main.py &
```

日志输出默认会保存在项目根目录下的 `nohup.out` 文件中。你也可以在 `logging_config.py` 中配置更详细的日志行为。

### 3.3 启动 Celery Worker（重要）

确保后端与 Worker 使用“同一个” Redis Broker，否则任务会提交成功但 Worker 收不到。

- Docker 部署（docker-compose 已内置）：
  - Worker 在容器内连接 `redis:6379`（内部网络），命令：
    - `celery -A tasks.celery_app worker --loglevel=info --concurrency=4`
  - 后端若跑在宿主机，请将后端 Redis 指向宿主机映射端口 `30637`：
    - `export REDIS_HOST=localhost && export REDIS_PORT=30637 && export REDIS_DB=0`
    - 或将 `backend/config.json` 中 `redis.port` 改为 `30637`

- 本地开发（无 Docker）：
  1) 启动 Redis（端口假设为 6379，或按实际端口调整）
  2) 配置环境变量或修改 `backend/config.json` 使后端与 Worker 指向相同 Redis：
     - 例如：`export REDIS_HOST=localhost && export REDIS_PORT=6379 && export REDIS_DB=0`
  3) 启动 Worker：
     - `celery -A tasks.celery_app worker -l info -Q celery`

注意：
- 模块 `tasks/celery_app.py` 已导出 `celery` 变量，确保命令 `-A tasks.celery_app` 能正确加载应用。
- 默认队列为 `celery`，若自定义 `-Q`，请与任务路由保持一致。

### 3.4 常见问题排查

- 提交任务成功但 Worker 无任务：
  - 大概率是后端与 Worker 连接到不同的 Redis。请核对两边的 `REDIS_HOST/REDIS_PORT/REDIS_DB`。
  - 使用 `redis-cli -p <port> monitor` 或 `xrange` 检查是否有队列消息写入。
  - 确认 Worker 日志中显示的 `broker` 与后端一致。

### 3.5 取消任务说明

当前 API 使用业务 `task_id`（UUID）标识业务任务，Celery 自身也有任务 ID。取消任务需要 Celery 任务 ID；如需精确取消，建议在提交时保存 `AsyncResult.id`，后续可扩展模型字段或 Redis 元信息以进行映射。

## 4. (可选) Docker 部署

项目中包含 `Dockerfile`，你也可以选择使用 Docker 进行构建和部署。具体步骤请参考 `Dockerfile` 中的内容或补充相关说明。

---

*请根据你的项目实际情况修改和补充上述内容，特别是项目简介和 `venv/` 的确切使用方式。* 