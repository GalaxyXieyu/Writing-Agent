# 使用说明功能实现文档

## 功能概述
在顶部 Header 增加"使用说明" tab，管理员可以配置链接，用户点击后跳转到外部链接。

## 功能实现详情

### 1. 后端实现

#### 1.1 数据模型
- **文件**: `backend/models/system_config.py`
- **表名**: `system_config`
- **配置项**: `usage_doc_url` - 存储使用说明文档的链接地址

#### 1.2 后端接口

##### 公共接口（无需登录）
- **接口**: `GET /api/public-configs`
- **文件**: `backend/api/routes/public.py`
- **功能**: 获取公共配置，包括 `usage_doc_url`
- **返回格式**:
```json
{
  "code": 200,
  "data": {
    "usage_doc_url": "https://example.com/docs"
  }
}
```

##### 管理员接口（需要管理员权限）
- **接口**: `GET /api/admin/system-configs`
- **功能**: 获取所有系统配置
- **文件**: `backend/api/routes/admin.py`

- **接口**: `POST /api/admin/system-configs`
- **功能**: 更新系统配置
- **文件**: `backend/api/routes/admin.py`
- **请求格式**:
```json
[
  {
    "config_key": "usage_doc_url",
    "config_value": "https://example.com/docs"
  }
]
```

#### 1.3 数据库初始化
- **文件**: `backend/initialization.py`
- 已添加 `system_config` 模型导入，确保表在启动时自动创建
- 在 `get_system_configs` 接口中，会自动初始化 `usage_doc_url` 配置项（如果不存在）

### 2. 前端实现

#### 2.1 API 层
- **文件**: `frontend/src/service/api.public.js`
- **方法**: `getPublicConfigs()` - 获取公共配置

- **文件**: `frontend/src/service/api.admin.js`
- **方法**: `adminGetSystemConfigs()` - 获取系统配置
- **方法**: `adminUpdateSystemConfigs(configs)` - 更新系统配置

#### 2.2 状态管理
- **文件**: `frontend/src/store/modules/system.js`
- **Store**: `useSystemStore`
- **状态**: `configs` - 存储配置数据
- **Getter**: `usageDocUrl` - 获取使用说明链接
- **Action**: `fetchPublicConfigs()` - 从后端获取公共配置

#### 2.3 主布局组件
- **文件**: `frontend/src/layouts/MainLayout.vue`
- **功能**:
  1. 在 `onMounted` 时调用 `systemStore.fetchPublicConfigs()` 获取配置
  2. 在 `navMenus` 计算属性中，如果 `usageDocUrl` 有值，则添加"使用说明"菜单项
  3. 在 `handleNavClick` 中处理使用说明的点击事件，使用 `window.open` 在新标签页打开链接

#### 2.4 管理员配置页面
- **文件**: `frontend/src/pages/admin/system/index.vue`
- **功能**:
  1. 动态渲染所有系统配置项
  2. 管理员可以编辑 `usage_doc_url` 配置
  3. 点击保存按钮更新配置

### 3. 使用流程

#### 3.1 管理员配置流程
1. 管理员登录系统
2. 点击顶部导航的"系统设置"
3. 在"使用说明文档链接"输入框中输入完整的 URL（如：https://docs.example.com）
4. 点击"保存设置"按钮
5. 配置保存成功后，所有用户的顶部导航栏会显示"使用说明" tab

#### 3.2 用户使用流程
1. 用户登录系统
2. 如果管理员配置了使用说明链接，顶部导航栏会显示"使用说明" tab
3. 点击"使用说明" tab
4. 系统在新标签页打开配置的文档链接

### 4. 技术特点

1. **动态显示**: 只有当管理员配置了链接后，"使用说明" tab 才会显示
2. **新标签页打开**: 点击后使用 `window.open(url, '_blank')` 在新标签页打开，不影响当前页面
3. **无需登录即可获取**: 公共配置接口无需登录，确保所有用户都能看到配置
4. **响应式设计**: 在桌面端和移动端都能正常显示和使用
5. **自动初始化**: 后端会自动创建 `system_config` 表和 `usage_doc_url` 配置项

### 5. 注意事项

1. 管理员配置的链接必须是完整的 URL（包含 http:// 或 https://）
2. 如果没有配置链接，"使用说明" tab 不会显示
3. 修改配置后，用户刷新页面即可看到更新
4. 外部链接在新标签页打开，不会影响当前应用状态
