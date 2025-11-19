# 样式系统更新文档

## 概述
已根据设计指南（style.md）对整个前端应用进行了全面的样式系统升级，采用现代极简设计语言。

## 主要更新内容

### 1. 全局CSS变量（src/assets/index.css）
- ✅ 新增 **Charcoal 色系**：#202020, #29292e, #343434
- ✅ 新增 **Gray 色系**：#f9f9f9, #f5f5f5, #eaedf1, #d7d7d7, #c0c0c0, #8b8b8b
- ✅ 新增 **Brand 色**：#F17463
- ✅ 添加语义化颜色令牌：`--divide`, `--primary`, `--primary-light`, `--footer-link`, `--canvas`, `--canvas-fill`
- ✅ 新增 `--shadow-aceternity` 阴影变量
- ✅ 完善明暗主题切换支持

### 2. Tailwind配置（tailwind.config.js）
- ✅ 扩展颜色系统：charcoal、gray、brand 色系
- ✅ 添加语义化颜色：divide、primary、primary-light、footer-link、canvas
- ✅ 添加字体配置：font-primary、font-mono
- ✅ 新增 shadow-aceternity 阴影工具类
- ✅ 调整容器内边距策略

### 3. UI组件更新

#### Button（components/ui/Button.vue）
- ✅ 圆角改为 `rounded-xl`
- ✅ 主按钮：charcoal-900 背景，暗色模式白色
- ✅ 新增 `brand` variant：Brand色背景
- ✅ 添加 `active:scale-[0.98]` 按压效果
- ✅ 优化 hover 状态过渡

#### Card（components/ui/Card.vue）
- ✅ 圆角改为 `rounded-2xl`
- ✅ 边框使用 `border-divide`
- ✅ 背景：`bg-gray-50 dark:bg-neutral-800`
- ✅ 阴影：`shadow-aceternity`
- ✅ 添加 `hover:bg-transparent` 效果

#### Input（components/ui/Input.vue）
- ✅ 阴影改为 `shadow-aceternity`
- ✅ 过渡改为 `transition-[color,box-shadow]`
- ✅ 增强 focus 样式：ring-2
- ✅ 添加暗色模式背景

#### Textarea（components/ui/Textarea.vue）
- ✅ 最小高度提升到 80px
- ✅ 应用 `shadow-aceternity`
- ✅ 改进 focus 效果
- ✅ 支持暗色模式

#### Badge（components/ui/Badge.vue）
- ✅ 圆角改为 `rounded-full`
- ✅ 新增 `brand` variant：`bg-brand/10 text-brand`
- ✅ 优化各 variant 配色
- ✅ 完善暗色模式

#### DropdownMenu（components/ui/DropdownMenu.vue）
- ✅ 圆角改为 `rounded-xl`
- ✅ 磨砂浮层：`bg-white/95 backdrop-blur-sm`
- ✅ 边框使用 `border-divide`
- ✅ 增强阴影效果

#### DropdownMenuItem（components/ui/DropdownMenuItem.vue）
- ✅ 添加圆角 `rounded-lg`
- ✅ 优化间距和边距
- ✅ 改进 hover 效果
- ✅ 完善暗色模式

#### Dialog（components/ui/Dialog.vue）
- ✅ 遮罩层磨砂效果：`bg-black/50 backdrop-blur-sm`
- ✅ 内容区圆角改为 `rounded-2xl`
- ✅ 边框使用 `border-divide`
- ✅ 优化暗色背景

#### Table组件（TableHead.vue, TableRow.vue）
- ✅ 表头添加浅灰背景：`bg-gray-100`
- ✅ 行边框使用 `border-divide`
- ✅ 改进 hover 效果：`hover:bg-gray-50`
- ✅ 完善暗色模式

### 4. MainLayout布局（layouts/MainLayout.vue）
- ✅ 导航栏磨砂效果：`bg-white/80 backdrop-blur-sm`
- ✅ 添加 `shadow-aceternity` 阴影
- ✅ 激活状态改为 brand 色：`bg-brand/10 text-brand`
- ✅ 优化导航按钮样式：`rounded-lg`，改进颜色
- ✅ 移动端抽屉磨砂遮罩：`bg-black/50 backdrop-blur-sm`
- ✅ 统一圆角和间距
- ✅ 移除旧的渐变色样式
- ✅ 全面支持暗色模式

## 设计原则应用

### ✅ 颜色系统
- **品牌色小面积使用**：仅用于激活状态、徽章、强调
- **中性色为主**：Gray、Charcoal 色系占主导
- **明暗主题一致性**：所有组件支持暗色模式

### ✅ 圆角策略
- 小组件：`rounded-md/lg`
- 卡片/按钮：`rounded-xl/2xl`
- 徽章：`rounded-full`

### ✅ 间距系统
- 容器内边距：`px-4 md:px-6`
- 按钮内边距：`px-6 py-2`
- 组件间距：`gap-4/6`

### ✅ 阴影层次
- 细腻阴影：`shadow-aceternity`（卡片、输入）
- 强阴影：`shadow-2xl`（Dialog、抽屉）

### ✅ 动效
- 过渡时长：`duration-150/200`
- 按钮按压：`active:scale-[0.98]`
- 磨砂浮层：`backdrop-blur-sm`

## CSS Lint 说明
文件中的 `@tailwind` 和 `@apply` CSS lint 警告是正常的，这些指令由 Tailwind CSS 处理，不影响运行。

## 后续建议

### 可选优化
1. **字体集成**：考虑添加 Inter Display 和 DM Mono 字体文件
2. **页面组件**：逐步更新各页面组件以匹配新设计系统
3. **动效增强**：考虑使用 framer-motion 添加序列入场动画
4. **响应式优化**：进一步优化移动端体验

### 使用新样式
```vue
<!-- Button 使用 -->
<Button variant="default">默认按钮</Button>
<Button variant="brand">品牌按钮</Button>
<Button variant="outline">次级按钮</Button>

<!-- Badge 使用 -->
<Badge variant="brand">New</Badge>
<Badge variant="secondary">Beta</Badge>

<!-- Card 使用 -->
<Card class="p-5">
  <!-- 内容 -->
</Card>
```

## 验证清单
- ✅ 全局CSS变量已更新
- ✅ Tailwind配置已扩展
- ✅ 所有基础UI组件已更新
- ✅ MainLayout已现代化
- ✅ 明暗主题支持完善
- ⏳ 需要在浏览器中验证视觉效果

## 运行测试
```bash
cd frontend
npm run dev
```

然后检查：
1. 导航栏磨砂效果
2. 按钮品牌色和圆角
3. 卡片阴影和hover效果
4. 输入框focus状态
5. 下拉菜单磨砂浮层
6. 暗色模式切换（如果已实现）
