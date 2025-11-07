# 模型配置功能需求确认（已确认）
 
 ## 一、原始需求概述
 - 依据任务文档 `task_docs/model_config_feature.md` 实现“模型配置中心”。
 - 目标：后端支持多大模型配置的持久化、默认策略与按用户级/全局级获取；前端提供模型管理页与在生成流程中的模型选择；生成/优化接口可按 `model_id` 切换。
 
 ## 二、仓库上下文影响与集成点
 - 架构与栈：后端 FastAPI + SQLAlchemy Async + MySQL，前端 Uni-app(Vue3/Pinia/Element Plus)。
 - 路由聚合：`backend/api/routes/api.py` -> 当前已挂载 `solution/templates/file/tasks`；需新增 `model_config` 路由。
 - 异步会话：`backend/config.py` 已提供 `get_async_db()` 和异步引擎；但 `backend/api/routes/solution.py` 存在硬编码 DB URL 的自建引擎，建议统一改为 `config.get_async_db()` 以避免配置分裂（与本次改造相关）。
 - Agent 使用：`backend/services/solution.py` 通过 `ai.agents.*.astream()` 产出流；现无可注入 LLM，需重构为“从工厂取 llm → 传入 agent”。
 - 现有 LLM：`backend/ai/llm/` 已有多实现（gpt/qwen 等），印证“硬编码/多处配置”的现状。
 
## 三、最终落地范围（根据你的确认）
 1) 数据库与模型
- 新表：`ai_model_config`
  - 字段（最终）：`id(PK)`, `user_id(可空=全局)`, `name(展示名)`, `model(如 gpt-4o)`, `api_key(明文存储)`, `base_url`, `temperature(0~2)`, `max_tokens`, `is_default(bool)`, `status_cd('Y'|'N')`, `remark(可空)`, `created_at`, `updated_at`
  - 不区分 `model_type`，也不区分 provider，统一走 OpenAI 兼容协议字段（base_url + api_key + model）。
  - 索引：`(user_id, status_cd)`、`(status_cd)`。
- ORM/Pydantic：`models/model_config.py` 定义 ORM + Create/Update/Query/Response + `SetDefaultModelRequest`。
 
2) 安全与配置
- 不做加密与安全强化，`api_key` 明文入库与返回（按你确认执行）。
 
 3) 服务层
 - `services/model_config.py`：CRUD、筛选与默认策略（设置默认时清除同类型其它默认；优先用户级默认，若无则回退全局默认）。
 
4) LLM 工厂
- `ai/llm/llm_factory.py`：
  - `create_llm(config, use_cache=True)`、`clear_cache(model_id=None)`、`get_llm_by_id(db, id)`、`get_default_llm(db, user_id=None)`。
  - 统一使用 LangChain `ChatOpenAI`（openai 兼容），传入 `base_url/api_key/model/temperature/max_tokens`。
  - 线程安全内存缓存（key=模型ID），支持简单 TTL（默认 15 分钟）。
 
5) 路由
- `api/routes/model_config.py`（7 个接口）
  - POST `/api/model-config/create`
  - GET  `/api/model-config/list`（支持分页与筛选）
  - GET  `/api/model-config/{model_id}`
  - PUT  `/api/model-config/{model_id}`
  - DELETE `/api/model-config/{model_id}`（软删 `status_cd='N'`）
  - POST `/api/model-config/set-default`（取消同用户其它默认）
  - GET  `/api/model-config/default`（按 `user_id` 取默认；无 user_id 走全局默认）
- 统一响应：`{code, message, type, data}` 与现有接口风格一致。
 
6) 生成流程改造
- `services/solution.py`：
  - `generate_chapter/optimize_content/generate_article` 增加 `db, model_id, user_id` 参数。
  - 获取 `llm = await LLMFactory.get_llm_by_id(...)`；若未提供 `model_id` 或找不到对应配置，则返回 400（不允许生成）。
  - `ai/agents/*` 改为接收外部传入的 `llm`（彻底移除硬编码）。
- `api/routes/solution.py`：
  - 请求体新增并要求提供 `model_id`（与可选 `userId`），透传到服务层；若缺失 `model_id` 直接返回错误提示。
  - 统一改为使用 `backend/config.py:get_async_db()` 提供的会话（消除硬编码连接串）。
 
7) 前端
- Pinia：`store/modules/modelConfig.js`（state/actions/getters，持久化 current/default）。
- API：`service/api.modelConfig.js`（封装上述 7 个后端接口）。
- 页面：`pages/model-config/`（列表、表单）；`components/ModelSelector.vue` 集成至生成页面，强制选择 `model_id` 后才能触发生成按钮。
- 可见性：管理页“需要登录态可见”（前端路由守卫处理即可，后端不做强校验）。
 
## 四、你已确认的关键决策（汇总）
1) 不做鉴权/校验，后端简单实现即可。
2) 不区分 `model_type`，统一使用 `ChatOpenAI` 初始化；只需能选择模型并调用。
3) 不做安全加密，API Key 明文存储与返回。
4) 列表支持分页（后端与前端皆实现）。
5) 接受 LLM 工厂 + 缓存（内存+TTL）方案。
6) 不需要向后兼容，全面改为基于配置的 LLM；若未配置模型则禁止生成。
7) 不区分管理员，统一 OpenAI 兼容格式字段（base_url/api_key/model/temperature/...）。
8) 不需要示例初始数据。
9) API 不兼容老前端，旧前端需跟进修改。
10) 统一使用 `backend/config.py` 的 DB 会话。
11) 不需要审计；管理页需要“登录态可见”。
 
## 五、成功标准（验收）
 - 能创建/编辑/删除模型配置；API Key 加密落库；编辑时 API Key 留空不改值。
 - 能设置默认模型（同类型仅 1 个），并区分用户默认与全局默认。
- 生成/优化接口必须显式提供 `model_id`；若未提供或无对应模型，返回明确错误，前端禁止发起生成。
 - 前端可在管理页完成全流程，并在生成页面选择模型并生效。
 - 单元/集成验证：基本 CRUD、默认策略、生成链路可切换生效。
 
## 六、需求质量评分（最终确认）
- 功能清晰度（/30）：29  
- 技术具体度（/25）：23  
- 实施完整性（/25）：23  
- 业务上下文（/20）：18  
- 最终总分：93/100（达到实现阈值 ≥ 90）
 
 ## 七、后续产物
 - 待确认后，补充技术规格 `requirements-spec.md`（接口契约、模型字段、错误码、时序图）。
 
 ---
需求已清晰且评分≥90。是否开始进入实现阶段？（回复“yes/确认/继续”以执行实现；或提出调整）
