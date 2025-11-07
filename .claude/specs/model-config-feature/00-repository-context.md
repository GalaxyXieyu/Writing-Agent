# 仓库上下文报告（model-config-feature）

## 项目类型与目的
- 单仓多端项目：后端 FastAPI（异步）+ 前端 Uni-app(Vue3/Element Plus)。
- 目标：按任务文档实现“模型配置中心”，支持多大模型配置的持久化、选择与默认策略，并改造生成流程按模型运行。

## 技术栈总结（已检测）
- 后端：FastAPI、SQLAlchemy 2.x Async、aiomysql、Uvicorn、Celery+Redis、LangChain（openai、text-splitters 等包已存在）。
- 数据库：MySQL（连接串在 `backend/config.py`，使用异步引擎）。
- 队列/缓存：Redis（`backend/config.py` 暴露了 CELERY/REDIS 配置）。
- 测试：pytest、pytest-asyncio（requirements 中）。
- 前端：Uni-app（vite4）、Vue3、Pinia、Element Plus、Axios 等（见 `frontend/package.json`）。

## 代码组织与关键文件
- 后端入口：`backend/main.py`（注册 `api.routes.api:api_router`）。
- 已有路由聚合：`backend/api/routes/api.py`（包含 solution/templates/file/tasks 四组路由）。
- 生成相关：
  - 服务层：`backend/services/solution.py`
    - 提供 `generate_article`、`generate_chapter`、`optimize_content`（基于 `ai.agents` 的 `astream` 流式输出）。
    - 当前未传入可切换的 LLM；agent 内部可能硬编码模型。
  - Agent 实现：`backend/ai/agents/*`（未展开读取，但已从服务调用处确认依赖）。
- 现有 LLM 适配：`backend/ai/llm/` 目录下有 `gpt.py、qwen.py、mygpt.py、mygpt_qwen.py、qwen_inside.py、qwen_https.py`，符合“硬编码多处配置”的现状描述。
- 数据与会话：`backend/config.py` 中定义了异步引擎与 `get_async_db()`，尚未见 Alembic 迁移目录。

## 现有约定与风格
- 路由前缀：全局 `/api`，子路由如 `/api/solution/...`。
- 响应风格：当前路由文件未统一封装 `{code,message,type,data}`，文档提到需“统一响应格式”，需确认是否引入统一 Response 包装器。
- 用户身份：`backend/services/auth.py` 存在，但当前路由聚合未注册 auth 路由；`user_id` 获取方式需确认（Header/Token/Query）。

## 与新功能的集成点
- 新增模块：
  - `backend/models/model_config.py`（ORM + Pydantic）
  - `backend/services/model_config.py`（CRUD + 默认模型策略）
  - `backend/ai/llm/llm_factory.py`（按配置构造 LLM，含缓存与解密）
  - `backend/api/routes/model_config.py`（8 个 REST 接口）
  - `backend/utils/encryption.py`（API Key 加解密）
  - `backend/migrations/*.sql`（如采用 SQL 脚本迁移）
- 既有功能改造：
  - `backend/services/solution.py` 的 `generate_* / optimize_content`：新增 `db、model_id、user_id` 参数，调用 `LLMFactory` 获取实例；未指定 `model_id` 用默认。
  - `backend/api/routes/solution.py` 对应入参扩展与参数透传。
  - `backend/ai/agents/*` 改为接收外部传入的 `llm`（移除硬编码）。
- 前端新增：
  - `frontend/src/store/modules/modelConfig.js`（Pinia）
  - `frontend/src/service/api.modelConfig.js`（API 封装）
  - `frontend/src/pages/model-config/*`（管理页）
  - `frontend/src/components/ModelSelector.vue` 并在生成页面集成。

## 约束与注意点
- 安全：API Key 需加密落库；密钥从环境变量 `ENCRYPTION_SECRET_KEY/ENCRYPTION_SALT` 读取；后端需新增 `cryptography` 依赖。
- 默认模型策略：用户级默认优先，其次全局默认；设置默认需清除同类型其它默认。
- 可用 Provider：openai、qwen（以及保留扩展口）；需适配 `api_base / api_key / model_name / temperature / max_tokens`。
- 兼容性：改造应不破坏现有生成接口的旧用法（未传 `model_id` 时使用默认）。

## 风险与潜在缺口（待澄清）
- 认证来源：`user_id` 如何获取与校验？是否需要按用户隔离配置？
- 迁移方案：采用 Alembic 还是 SQL 文件？是否需要回滚脚本集成到部署流程？
- 统一响应：是否落地统一响应包装（code/message/type/data）？如果是，需要通用异常处理器。
- Provider 列表与初始数据：是否仅 OpenAI/Qwen？默认模型与类型映射的初值？
- 并发策略：LLM 工厂的缓存生命周期、清理接口与并发锁粒度。

---

本报告用于 Phase 1 的需求确认与规格编写基线。
