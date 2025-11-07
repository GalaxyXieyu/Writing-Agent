# 模型配置功能开发任务计划 (精简版)

## 📋 项目概述

### 功能目标
- 后台管理界面配置多种AI大模型
- 数据库持久化模型配置
- 生成报告时可选择不同模型
- 用户级别的模型配置管理

### 技术栈
- **后端**: FastAPI + SQLAlchemy (异步) + MySQL + Langchain
- **前端**: Vue 3 + Element Plus + Pinia + Axios

### 当前问题
- LLM配置硬编码在agent文件中 (gpt.py, qwen.py等)
- 无法动态切换模型
- 多个地方重复配置API Key
- 缺少统一的模型管理入口

---

## 🏗️ 系统架构

### 后端架构
```
models/model_config.py       # 数据模型层 (ORM + Pydantic)
services/model_config.py     # 业务逻辑层 (CRUD + 默认模型管理)
ai/llm/llm_factory.py        # LLM工厂模式 (动态创建LLM实例)
api/routes/model_config.py  # API路由层 (8个REST接口)
utils/encryption.py          # API Key加密工具
```

### 前端架构
```
store/modules/modelConfig.js         # 状态管理 (Pinia)
service/api.modelConfig.js           # API封装
pages/model-config/index.vue         # 管理页面
pages/model-config/components/       # 列表、表单组件
components/ModelSelector.vue         # 模型选择器 (可复用)
```

### 数据流
```
用户配置模型 → 加密存储数据库 → LLM工厂读取 → 创建实例 → Agent使用 → 生成内容
```

---

## 🗂️ 任务列表

### 一、后端开发 (21小时)

#### 任务1: 数据库设计与迁移
**优先级**: 🔴 高 | **工时**: 2h

**核心表**: `ai_model_config`
- 关键字段: model_id, user_id, model_name, model_key, api_key(加密), api_base, temperature, max_tokens, model_type, model_provider, is_default, status_cd
- 索引: user_id, model_type, status_cd
- 初始数据: GPT-4o, Qwen2.5-72B (generation/optimization/planning)

**交付物**:
- `migrations/001_create_model_config_table.sql`
- `migrations/002_init_model_config_data.sql`
- `migrations/rollback_model_config.sql`

---

#### 任务2: 后端模型层
**优先级**: 🔴 高 | **工时**: 3h

**核心模型**:
- `AiModelConfig`: SQLAlchemy ORM模型
- `ModelConfigCreate/Update/Query/Response`: Pydantic模型
- `SetDefaultModelRequest`: 设置默认模型

**关键验证**:
- API Base必须是http/https开头
- model_type枚举: generation/optimization/planning
- temperature: 0-2.0

**交付物**: `models/model_config.py`

---

#### 任务3: 安全工具 - API Key加密
**优先级**: 🔴 高 | **工时**: 2h

**核心功能**:
- 使用 `cryptography` 库 + Fernet加密
- 基于PBKDF2派生密钥
- 加密密钥从环境变量读取 `ENCRYPTION_SECRET_KEY`

**交付物**:
- `utils/encryption.py` - `encrypt_api_key()`, `decrypt_api_key()`
- 更新 `config.py` 添加加密配置
- 更新 `requirements.txt` 添加cryptography

---

#### 任务4: 服务层业务逻辑
**优先级**: 🔴 高 | **工时**: 4h

**核心服务**:
```python
async def create_model_config()      # 创建配置 (自动加密API Key)
async def get_model_config()         # 获取单个配置
async def list_model_configs()       # 列表查询 (支持按type/provider筛选)
async def update_model_config()      # 更新配置
async def delete_model_config()      # 软删除
async def set_default_model()        # 设置默认 (取消其他默认)
async def get_default_model()        # 获取默认 (优先用户级>全局)
def get_decrypted_api_key()          # 解密API Key
```

**关键逻辑**:
- 创建/设置默认时,自动取消同类型其他默认模型
- 优先查找用户级配置,回退到全局配置
- 所有操作记录日志

**交付物**: `services/model_config.py`

---

#### 任务5: LLM工厂模式
**优先级**: 🔴 高 | **工时**: 3h

**核心类**: `LLMFactory`
```python
def create_llm(config, use_cache=True)  # 根据配置创建LLM实例
def clear_cache(model_id=None)          # 清除缓存
async def get_llm_by_id(db, model_id)   # 根据ID获取LLM
async def get_llm_by_type(db, type)     # 根据类型获取默认LLM
```

**关键特性**:
- 实例缓存 (避免重复创建)
- 线程安全 (threading.Lock)
- 支持多provider (openai/qwen/custom)
- 自动解密API Key

**交付物**: `ai/llm/llm_factory.py`

---

#### 任务6: API路由层
**优先级**: 🔴 高 | **工时**: 4h

**8个API接口**:
```
POST   /api/model-config/create              # 创建配置
GET    /api/model-config/list                # 列表查询
GET    /api/model-config/{model_id}          # 获取详情
PUT    /api/model-config/{model_id}          # 更新配置
DELETE /api/model-config/{model_id}          # 删除配置
POST   /api/model-config/set-default         # 设置默认
GET    /api/model-config/default/{type}      # 获取默认
GET    /api/model-config/types/list          # 获取类型列表
```

**关键点**:
- 响应中不返回完整API Key (只返回has_api_key标识)
- 统一错误处理
- 统一响应格式 {code, message, type, data}

**交付物**:
- `api/routes/model_config.py`
- 在 `main.py` 中注册路由

---

#### 任务7: 生成报告API增强
**优先级**: 🟡 中 | **工时**: 3h

**修改的API**:
- `/generate-chapter` - 增加 `model_id`, `user_id` 参数
- `/generate-article` - 增加 `model_id` 参数
- `/optimize-content` - 增加 `model_id`, `user_id` 参数

**修改的服务**:
- `services/solution.py` 中的 `generate_chapter()`, `generate_article()`, `optimize_content()`
- 接收 `db`, `model_id`, `user_id` 参数
- 使用 `get_llm_by_id()` 或 `get_llm_by_type()` 获取LLM实例
- 未指定model_id时使用默认模型

**交付物**:
- 修改 `models/solution.py` 请求模型
- 修改 `services/solution.py` 服务函数
- 修改 `api/routes/solution.py` 路由

---

#### 任务8: Agent代码重构
**优先级**: 🟡 中 | **工时**: 2h

**修改的Agent文件**:
- `ai/agents/template_generator.py`
- `ai/agents/content_optimizer.py`
- `ai/agents/paragraph_writer.py`
- `ai/agents/planner.py`

**重构方式**:
- 移除硬编码的LLM定义
- 函数签名改为接收 `llm: ChatOpenAI` 参数
- 调用方通过工厂创建LLM实例后传入

**示例**:
```python
# 旧代码
llm = ChatOpenAI(model="gpt-4o", api_key="...")

# 新代码
async def generate_template(title, requirement, llm):
    # 使用传入的llm参数
```

---

### 二、前端开发 (12.5小时)

#### 任务9: Pinia Store状态管理
**优先级**: 🔴 高 | **工时**: 2h

**State**:
```javascript
modelList: []              // 模型列表
currentModel: null         // 当前选中模型
defaultModels: {}          // 默认模型映射 {generation: {...}, ...}
loading: false
modelTypes: []             // 模型类型列表
modelProviders: []         // 提供商列表
```

**Actions**:
- `fetchModelList()` - 获取模型列表
- `createModel()` - 创建模型
- `updateModel()` - 更新模型
- `deleteModel()` - 删除模型
- `setDefaultModel()` - 设置默认
- `fetchModelTypes()` - 获取类型列表
- `setCurrentModel()` - 设置当前选中

**Getters**:
- `getModelsByType(type)` - 按类型筛选
- `getDefaultModel(type)` - 获取默认模型
- `getCurrentOrDefault(type)` - 当前或默认

**持久化**: 使用 pinia-plugin-persistedstate 持久化 currentModel 和 defaultModels

**交付物**: `store/modules/modelConfig.js`

---

#### 任务10: API服务封装
**优先级**: 🔴 高 | **工时**: 1.5h

**封装的API方法**:
```javascript
modelConfigApi.getList(params)          // 获取列表
modelConfigApi.getDetail(modelId)       // 获取详情
modelConfigApi.create(data)             // 创建
modelConfigApi.update(modelId, data)    // 更新
modelConfigApi.delete(modelId)          // 删除
modelConfigApi.setDefault(data)         // 设置默认
modelConfigApi.getDefault(type, userId) // 获取默认
modelConfigApi.getTypes()               // 获取类型
```

**交付物**: `service/api.modelConfig.js`

---

#### 任务11: 后台管理界面
**优先级**: 🔴 高 | **工时**: 6h

**页面结构**:
```
pages/model-config/
├── index.vue                    # 主页面
├── components/
│   ├── ModelList.vue            # 模型列表
│   └── ModelForm.vue            # 模型表单 (新增/编辑)
```

**主要功能**:
1. **筛选区域**: 按类型、提供商筛选
2. **模型列表**: 
   - 卡片式展示
   - 显示: 模型名称、类型、提供商、API地址、参数
   - 默认模型高亮
   - 操作: 编辑、删除、设为默认
3. **新增/编辑表单**:
   - 字段: 模型名称、模型Key、API Key、API Base、温度、Tokens、类型、提供商、备注
   - 验证: 必填项、格式校验
   - 编辑时API Key留空表示不修改

**UI组件**: Element Plus (el-card, el-form, el-dialog, el-table等)

**交付物**:
- `pages/model-config/index.vue`
- `pages/model-config/components/ModelList.vue`
- `pages/model-config/components/ModelForm.vue`

---

#### 任务12: 生成报告界面增强
**优先级**: 🔴 高 | **工时**: 3h

**新增组件**: `ModelSelector.vue` (可复用的模型选择器)
- Props: modelType, label, modelValue
- 自动加载对应类型的模型列表
- 默认选中默认模型
- 支持v-model双向绑定

**集成到生成报告页面**:
- 在生成按钮旁边添加模型选择器
- 生成时传递 `model_id` 参数
- 记住用户最后选择

**修改的API调用**:
- `api.solution.js` 中的 `generateArticleApi()`, `generateChapterApi()`, `optimizeContentApi()`
- 增加 `model_id` 参数

**交付物**:
- `components/ModelSelector.vue`
- 修改 `pages/web-solution-assistant/index.vue`
- 修改 `service/api.solution.js`

---

### 三、测试与部署 (8.5小时)

#### 任务13: 数据库迁移执行
**优先级**: 🔴 高 | **工时**: 0.5h

**步骤**:
1. 备份现有数据库
2. 执行建表脚本
3. 手动加密API Key后执行初始化脚本
4. 验证数据正确性

---

#### 任务14: 集成测试
**优先级**: 🔴 高 | **工时**: 4h

**测试场景**:
1. **模型配置管理**: 创建、编辑、删除、设置默认
2. **生成报告**: 使用默认模型、切换模型生成
3. **权限控制**: 用户只能管理自己的配置
4. **异常处理**: API Key错误、网络异常、模型不可用
5. **性能测试**: LLM实例缓存、并发生成

---

#### 任务15: 环境配置
**优先级**: 🟡 中 | **工时**: 1h

**更新 .env**:
```bash
ENCRYPTION_SECRET_KEY=your-secret-key-32-chars!!
ENCRYPTION_SALT=your-salt-16-chars!
DEFAULT_MODEL_TEMPERATURE=0.2
DEFAULT_MAX_TOKENS=4096
```

**安装依赖**:
```bash
pip install cryptography==41.0.7
```

---

#### 任务16: 文档编写
**优先级**: 🟢 低 | **工时**: 2h

**文档内容**:
1. API接口文档
2. 用户操作手册
3. 开发指南 (如何扩展新provider)
4. 部署文档

---

## 📊 任务进度表

| ID | 任务名称 | 优先级 | 工时 | 状态 | 负责人 | 备注 |
|----|---------|--------|------|------|--------|------|
| 1 | 数据库设计与迁移 | 高 | 2h | ⬜ | | |
| 2 | 后端模型层 | 高 | 3h | ⬜ | | |
| 3 | 安全工具-加密 | 高 | 2h | ⬜ | | |
| 4 | 服务层业务逻辑 | 高 | 4h | ⬜ | | |
| 5 | LLM工厂模式 | 高 | 3h | ⬜ | | |
| 6 | API路由层 | 高 | 4h | ⬜ | | |
| 7 | 生成报告API增强 | 中 | 3h | ⬜ | | |
| 8 | Agent代码重构 | 中 | 2h | ⬜ | | |
| 9 | Pinia Store | 高 | 2h | ⬜ | | |
| 10 | API服务封装 | 高 | 1.5h | ⬜ | | |
| 11 | 后台管理界面 | 高 | 6h | ⬜ | | |
| 12 | 生成报告界面增强 | 高 | 3h | ⬜ | | |
| 13 | 数据库迁移执行 | 高 | 0.5h | ⬜ | | |
| 14 | 集成测试 | 高 | 4h | ⬜ | | |
| 15 | 环境配置 | 中 | 1h | ⬜ | | |
| 16 | 文档编写 | 低 | 2h | ⬜ | | |

**总计**: 42.5小时 ≈ 5-6个工作日

---

## 🎯 实施建议

### 开发阶段

**第一阶段 (Day 1-2): 后端核心**
- 任务1-6: 数据库、模型层、服务层、工厂、API路由
- 完成后进行后端单元测试

**第二阶段 (Day 2-3): 后端集成**
- 任务7-8: 生成API增强、Agent重构
- 集成测试后端完整流程

**第三阶段 (Day 3-4): 前端开发**
- 任务9-12: Store、API封装、管理界面、生成界面
- 前端功能测试

**第四阶段 (Day 5): 集成与优化**
- 任务13-14: 数据库迁移、集成测试
- Bug修复与性能优化

**第五阶段 (Day 6): 部署与文档**
- 任务15-16: 环境配置、文档编写
- 最终验收

---

## ⚠️ 风险与注意事项

### 技术风险
1. **API Key安全**: 加密密钥必须安全存储,不能提交到代码仓库
2. **LLM稳定性**: 需实现重试机制和降级策略
3. **并发问题**: LLM工厂缓存需线程安全
4. **数据库性能**: 大量配置时需查询优化

### 业务风险
1. **向后兼容**: 确保不影响现有功能
2. **用户体验**: 模型选择不应增加操作复杂度
3. **成本控制**: 不同模型成本不同,需监控
4. **数据迁移**: 现有硬编码配置需平滑迁移

### 建议措施
- 每阶段结束code review
- 关键功能单元测试
- 详细错误日志
- 添加模型调用监控统计
- 实现配置导入导出功能

---

## 📞 附录

### 关键文件路径

**后端**:
```
backend/
├── migrations/                    # 数据库迁移脚本
├── models/model_config.py        # 数据模型
├── services/model_config.py      # 业务逻辑
├── ai/llm/llm_factory.py        # LLM工厂
├── api/routes/model_config.py   # API路由
├── utils/encryption.py          # 加密工具
└── config.py                    # 配置文件
```

**前端**:
```
frontend/src/
├── store/modules/modelConfig.js          # 状态管理
├── service/api.modelConfig.js            # API封装
├── pages/model-config/                   # 管理页面
├── components/ModelSelector.vue          # 模型选择器
└── pages/web-solution-assistant/         # 生成报告页面
```

### 环境变量清单
```bash
# 数据库
DB_HOST=localhost
DB_PORT=30306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=tianshu

# 加密
ENCRYPTION_SECRET_KEY=your-secret-key-must-be-32-chars!!
ENCRYPTION_SALT=your-salt-16-char!

# 模型默认参数
DEFAULT_MODEL_TEMPERATURE=0.2
DEFAULT_MAX_TOKENS=4096
```

---

**文档版本**: v2.0 (精简版)  
**创建日期**: 2025-11-07  
**最后更新**: 2025-11-07
