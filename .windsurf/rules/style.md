---
trigger: model_decision
---

---
trigger: model_decision
description: frontend-style
---


设计风格：


1. 概览（Overview）
设计语言：现代极简、低饱和中性色 + 单一品牌色点缀，强调层次与留白。
技术栈：Tailwind CSS v4（@theme 令牌驱动）+ @tailwindcss/typography + next/font（本地 Inter Display、Google DM Mono）。
主题机制：使用 CSS 变量语义化（--divide、--primary 等），.dark 根切换一键反相；@custom-variant dark (&:where(.dark, .dark *)); 确保选择器简洁。
组件模式：Container 容器 + 语义分割线 + 卡片/表格 + 文字等级 + 微动效；品牌色用于提示/徽章/强调而非大面积底色。
2. 设计令牌（Design Tokens）
源文件：app/globals.css


字体
--font-primary: var(--font-inter), Inter Display, sans-serif
--font-mono: var(--font-mono), DM Mono, monospace
配色（基础）
Charcoal：--color-charcoal-900: #202020、-800: #29292e、-700: #343434
Gray：--color-gray-100: #f9f9f9、-200: #f5f5f5、-300: #eaedf1、-400: #d7d7d7、-500: #c0c0c0、-600: #8b8b8b
品牌：--color-brand: #F17463
明暗语义映射（root/.dark 上下文）
明亮：--divide（边框/分割）= gray-300；--primary（主文本）= neutral-900；--footer-link = #676767
暗色：--divide= neutral-800；--primary= neutral-100；--footer-link= neutral-300
Tailwind v4 inline 暴露
--color-divide、--color-primary、--color-canvas(-fill)、--color-dots、--color-line、--color-footer-link
阴影
--shadow-aceternity: 细腻描边 + 轻投影，用于小卡片/按钮徽标/输入等
背景图案
--background-repeating-gradient + --repeat-gradient-size（点阵/网格）
动效变量/关键帧
--animate-orbit / --animate-counter-orbit；@keyframes orbit、counter-orbit
推荐：优先使用语义令牌 border-divide、text-primary、text-footer-link 等代替硬编码色号，保证明暗切换一致。


3. 配色系统（Color Palette）
文本
主体：text-primary（明：neutral-900；暗：neutral-100）或 text-black/dark:text-white
次要/说明：text-gray-600、text-gray-500（暗：dark:text-neutral-300/400）
品牌强调：text-brand（用于图标/徽章/微交互）
背景
页面：bg-white dark:bg-black
区块/卡片：bg-gray-50 dark:bg-neutral-800
浮层：bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm
强调条：bg-brand/10
边框与分割
border-divide、divide-divide（自动跟随主题切换）
用法建议：


品牌色面积要小，多用于状态徽标、标签、活跃态描边、轻扫光背景（conic gradient）。
列表/表格交替行：亮色 bg-gray-50，暗色 dark:bg-neutral-800。
4. 排版（Typography）
字体来源：fonts/inter-display/inter.tsx（本地 Inter Display 300~900），fonts/dm-mono.tsx（DM Mono 400）。


字体栈
主字体：font-primary（body 默认）
等宽：font-mono（标签/小标题/数据）
标题体系
页标题 Heading：text-3xl md:text-4xl lg:text-6xl font-medium tracking-tight
分节标题 SectionHeading：text-2xl md:text-3xl lg:text-4xl text-charcoal-700
副标题 SubHeading：text-sm lg:text-base text-gray-600
单行 Kicker/组标题：font-mono text-sm uppercase tracking-tight text-neutral-500
正文与文章
一般正文：text-sm ~ text-base；
博客文：prose prose-base dark:prose-invert（由 @tailwindcss/typography 控制 h1~h4、list、code、pre 等）
字重建议
300-400：正文/注释；500-600：标题/按钮/要点；700+：极少数强强调位
字距/行高
标题 tracking-tight；正文遵循 Tailwind 默认行高，长段落可用 leading-relaxed
5. 间距系统（Spacing System）
容器与栅格
Container: max-w-7xl mx-auto
内边距：页面区块常用 px-4 md:px-8，纵向 py-16/20/40
网格与间隔
grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3/4
常用 gap：gap-4、gap-6、gap-10、gap-20
尺寸原子（常见）
size-40/60/70/100/120/200、min-h-40/60/80/120
建议：区块与区块之间≥ py-16，同层级卡片之间 gap-6~10，文字组与标题之间 mt-2~6。


6. 组件风格（Component Styles）
Navbar（导航）
固顶、半透明磨砂：bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm
统一阴影：shadow-aceternity；链接：text-gray-600 hover:text-neutral-900 dark:text-gray-300
Button（按钮）components/button.tsx
主按钮：bg-charcoal-900 text-white dark:bg-white dark:text-black
品牌：bg-brand text-white
次级：border-divide border bg-white hover:bg-gray-300 dark:bg-neutral-950
通用：rounded-xl px-6 py-2 text-sm font-medium transition duration-150 active:scale-[0.98]
Card/Info Block
背景：bg-gray-50 dark:bg-neutral-800
圆角：rounded-lg~2xl；边框：border-divide
Hover：hover:bg-transparent transition duration-200
表格/价格表
表头浅灰 + 选项卡：bg-gray-100；列间 divide-x，行间 divide-y
徽章/标签
bg-brand/10 text-brand rounded-full px-2 py-1 text-xs
输入框（UI）
rounded-md border border-input shadow-aceternity px-3 py-1 transition-[color,box-shadow] dark:bg-neutral-800
7. 阴影与层次（Shadows & Elevation）
令牌阴影：shadow-aceternity（细描边 + 轻投影），用于徽标、输入、卡片小件
标准：shadow-xl/shadow-2xl（大卡/浮窗）；内阴影：shadow-inner
自定义：shadow-[0px_2px_12px_0px_rgba(0,0,0,0.08)]（工具条、输入工具栏）
8. 动效与过渡（Animations & Transitions）
通用过渡：transition duration-150~200，hover 色彩/位移轻微变更
旋转/能量环：animate-spin bg-conic from-transparent via-blue-500 ... [animation-duration:2s~4s]
扫光/滑入：group-hover:*、mask-*-from-* 显隐渐变；序列入场由 motion（framer-motion）驱动（时长 0.2~1s）
环绕动画：--animate-orbit/--animate-counter-orbit 应用于环形装饰
9. 圆角（Border Radius）
输入/小徽章：rounded-md/lg
卡片/容器：rounded-xl/2xl/3xl
圆形/装饰：rounded-full；继承：rounded-[inherit]，精细化：rounded-[5px]
建议：页面主卡用 rounded-2xl，卡内元素用 rounded-md 形成层次差
10. 透明度与磨砂（Opacity & Transparency）
遮罩：bg-black/50 backdrop-blur-sm
浮层：bg-white/80 dark:bg-neutral-900/80（导航、浮动工具条）
退场弱化：opacity-50~70 grayscale（合作 Logo 墙、底图）
文本半透：text-white/50、text-neutral-400（说明/辅文）
11. 常用 Tailwind 使用模式（Common Tailwind CSS Usage）
令牌优先：border-divide、text-primary、text-footer-link 等语义类 > 直接色值类
明暗主题：dark:* 全覆盖；@custom-variant dark 确保 .dark 作用域生效
布局与容器：Container + px-4 md:px-8 + max-w-7xl
网格：grid-cols-1~4 + gap-6~20；表格/列表使用 divide-divide
动效：transition-[color,box-shadow]、active:scale-[0.98]、group-hover:*
背景图案：bg-[image:repeating-linear-gradient(...)]、bg-[radial-gradient(...)]、bg-conic
文章：prose prose-base dark:prose-invert（统一文档/博客样式）
12. 示例代码（Example Component Reference Design Code）
12.1 基础区块（容器 + 分节标题 + 副标题）


import { Container } from "@/components/container";
import { SectionHeading } from "@/components/seciton-heading";
import { SubHeading } from "@/components/subheading";


export function SectionBlock() {
return (
<Container className="border-divide border-x py-16 px-4 md:px-8">
<SectionHeading className="text-center">Build with Notus</SectionHeading>
<SubHeading className="mx-auto mt-4 max-w-lg">
Declarative UI primitives with a consistent token-based design system.
</SubHeading>
</Container>
);
}
12.2 Feature 卡片（卡片层次 + 品牌徽章 + 动效）


import { cn } from "@/lib/utils";
import { Button } from "@/components/button";


export function FeatureCard({ title, description, className }: { title: string; description: string; className?: string }) {
return (
<div
className={cn(
"rounded-2xl border border-divide bg-gray-50 p-5 shadow-aceternity transition duration-200 hover:bg-transparent",
"dark:bg-neutral-800",
className
)}
>
<div className="flex items-center justify-between">
<h3 className="text-charcoal-700 text-lg font-medium dark:text-neutral-100">{title}</h3>
<span className="bg-brand/10 text-brand rounded-full px-2 py-1 text-xs font-medium">New</span>
</div>
<p className="mt-2 text-sm text-gray-600 dark:text-neutral-300">{description}</p>
<div className="mt-4 flex items-center gap-2">
<Button variant="brand">Get Started</Button>
<Button variant="secondary" className="text-sm">Learn More</Button>
</div>
</div>
);
}
12.3 导航（磨砂 + 令牌阴影 + 渐显）


export function NavBarShell({ left, right }: { left: React.ReactNode; right: React.ReactNode }) {
return (
<div className="shadow-aceternity fixed inset-x-0 top-0 z-50 mx-auto hidden max-w-[calc(80rem-4rem)] items-center justify-between bg-white/80 px-2 py-2 backdrop-blur-sm xl:rounded-2xl md:flex dark:bg-neutral-900/80">
<div className="flex items-center gap-6 text-gray-600 dark:text-gray-300">{left}</div>
<div className="flex items-center gap-4 text-gray-600 dark:text-gray-300">{right}</div>
</div>
);
}
12.4 表格（分隔令牌 + 交替底色）


export function PricingTableShell({ head, rows }: { head: React.ReactNode; rows: React.ReactNode }) {
return (
<div className="border-divide border-x">
<div className="overflow-x-auto">
<table className="w-full text-left">
<thead>
<tr className="border-divide divide-divide divide-x border-b">{head}</tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</div>
</div>
);
}
12.5 About 创始人卡（快照复刻：底部渐显 + 底部信息条）


export function FounderCard({ image, name, title, onLinkedIn }: { image: string; name: string; title: string; onLinkedIn?: () => void }) {
return (
<div className="group relative h-60 overflow-hidden rounded-2xl md:h-100">
<img src={image} alt={name} className="h-full w-full object-cover object-top" />
{/* 底部渐显条（hover 出现）*/}
<div className="pointer-events-none absolute bottom-0 left-0 hidden h-[30%] w-full transition-all duration-200 group-hover:block" style={{
background: "linear-gradient(to top, rgba(0,0,0,0.6), transparent)"
}} />
{/* 信息条 */}
<div className="absolute inset-x-4 bottom-4 flex items-center justify-between rounded-xl bg-black/80 px-4 py-2">
<div>
<h3 className="text-sm font-medium text-white">{name}</h3>
<p className="text-sm text-neutral-300">{title}</p>
</div>
<button onClick={onLinkedIn} className="cursor-pointer">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white"><path d="M4.98 3.5C4.98 4.88 3.86 6 2.5 6C1.12 6 0 4.88 0 3.5C0 2.12 1.12 1 2.5 1C3.86 1 4.98 2.12 4.98 3.5ZM0.22 8.34H4.78V23.5H0.22V8.34ZM8.9 8.34H13.3V10.34H13.36C13.98 9.18 15.46 7.96 17.66 7.96C22.06 7.96 23 10.86 23 15.02V23.5H18.44V15.86C18.44 13.92 18.4 11.44 15.84 11.44C13.24 11.44 12.86 13.56 12.86 15.72V23.5H8.3L8.9 8.34Z" fill="currentColor"/></svg>
</button>
</div>
</div>
);
}
12.6 能量环装饰（conic + spin + 模糊）


export function EnergyRing() {
return (
<div className="relative h-16 w-16 overflow-hidden rounded-md bg-gray-200 p-px shadow-xl dark:bg-neutral-700">
<div className="absolute inset-0 scale-[1.4] animate-spin rounded-full bg-conic [background-image:conic-gradient(at_center,transparent,var(--color-blue-500)_20%,transparent_30%)] [animation-duration:2s]"></div>
<div className="via-brand absolute inset-0 scale-[1.4] animate-spin rounded-full bg-conic [background-image:conic-gradient(at_center,transparent,var(--color-brand)_20%,transparent_30%)] [animation-delay:1s] [animation-duration:2s]"></div>
<div className="relative z-20 flex h-full w-full items-center justify-center rounded-[5px] bg-white dark:bg-neutral-900" />
</div>
);
}
13. 背景与装饰（Patterns & Masks）
网格/线性图案：
bg-[image:repeating-linear-gradient(315deg,_var(--pattern-fg)_0,_var(--pattern-fg)_1px,_transparent_0,_transparent_50%)] + bg-[size:10px_10px]，通过 body 上的 --pattern-fg 控制深浅。
点阵：
bg-[radial-gradient(var(--color-dots)_1px,transparent_1px)] [background-size:10px_10px]
遮罩（部分组件用到）：
mask-*-from-* 自定义渐隐/渐显；group-hover:* 显示底部条或扫光。
14. 无障碍与对比度（A11y）
文本与背景建议对比 ≥ 4.5:1，深色背景上文本使用 text-neutral-100 或 text-white。
交互控件 hover/focus 有明显状态：transition + 颜色/阴影/位移微调；键盘焦点可考虑 focus-visible:ring-[3px]。
15. 约定与最佳实践（Do & Don’t）
Do：
使用语义令牌类（border-divide、text-primary）代替直写色值。
通过 Container 统一宽度与左右留白，区块使用 px-4 md:px-8。
标题体系按 Heading > SectionHeading > SubHeading 递进，不随机字号。
品牌色用于小面积强调，避免大面积背景造成视觉噪声。
Don’t：
不要在深色模式硬编码浅色边框/背景（请使用 dark:* 或令牌）。
不要在同层级卡片使用过多不同圆角/阴影风格。
16. 实施速查（Cheat Sheet）
分割/描边：border-divide、divide-divide
主要文字：text-primary
次要文字：text-gray-600 dark:text-neutral-400
卡片：rounded-2xl border border-divide bg-gray-50 dark:bg-neutral-800 shadow-aceternity
按钮：<Button variant="primary|secondary|brand" />
容器：<Container className="px-4 md:px-8 py-16" />
文章：prose prose-base dark:prose-invert
装饰：bg-conic animate-spin blur-2xl、mask-*-from-*、bg-[image:repeating-linear-gradient(...)]