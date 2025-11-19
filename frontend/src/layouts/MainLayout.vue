<style>
/* 全局样式 */
:root {
  --primary-color: #F17463;
  --secondary-color: #202020;
  --background-color: #ffffff;
  --text-color: #202020;
  --border-color: #eaedf1;
}

.dark {
  --primary-color: #F17463;
  --secondary-color: #f9f9f9;
  --background-color: #000000;
  --text-color: #f9f9f9;
  --border-color: #343434;
}

body {
  background-color: var(--background-color);
  color: var(--text-color);
}
</style>

<template>
	<div class="flex h-screen flex-col bg-white dark:bg-black">
		<!-- 顶部 Header -->
		<header class="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-divide bg-white/80 backdrop-blur-sm px-4 md:px-6 shadow-aceternity dark:bg-neutral-900/80">
			<div class="flex items-center gap-6">
				<h1 class="text-base sm:text-lg font-semibold text-charcoal-700 whitespace-nowrap tracking-tight dark:text-neutral-100">AI 写作助手</h1>
				
				<!-- 桌面端横向导航菜单 -->
				<nav class="hidden md:flex items-center gap-1">
					<button
						v-for="menu in navMenus"
						:key="menu.key"
						@click="handleNavClick(menu.key)"
						:class="[
							'px-3 py-1.5 text-sm rounded-lg transition-colors duration-150',
							activeNavMenu === menu.key
								? 'bg-brand/10 text-brand font-medium'
								: 'text-gray-600 hover:text-charcoal-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-neutral-100 dark:hover:bg-neutral-800'
						]"
					>
						{{ menu.label }}
					</button>
				</nav>

				<!-- 移动端汉堡按钮 -->
				<button
					class="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-lg hover:bg-gray-100 transition-colors dark:hover:bg-neutral-800"
					aria-label="打开导航菜单"
					@click="showMobileSidebar = true"
				>
					<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
					</svg>
				</button>
			</div>

			<div class="flex items-center gap-2 sm:gap-3 md:gap-4">
				<DropdownMenu>
					<template #trigger>
						<button class="flex items-center gap-1 sm:gap-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm text-gray-600 hover:text-charcoal-700 hover:bg-gray-100 transition-colors dark:text-gray-300 dark:hover:text-neutral-100 dark:hover:bg-neutral-800">
							<svg class="h-4 w-4 sm:h-5 sm:w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							<span class="hidden sm:inline">{{ userStore.profile.name || '管理员' }}</span>
							<span class="sm:hidden">{{ (userStore.profile.name || '管理员').slice(0, 2) }}</span>
							<svg class="h-3 w-3 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>
					</template>
					<DropdownMenuItem @click="showChangePasswordDialog = true">
						<svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
						</svg>
						修改密码
					</DropdownMenuItem>
					<DropdownMenuItem @click="handleLogout">
						<svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
						</svg>
						退出登录
					</DropdownMenuItem>
				</DropdownMenu>
			</div>
		</header>

		<!-- 移动端抽屉菜单 -->
		<transition name="fade">
			<div v-if="showMobileSidebar" class="fixed inset-0 z-40 md:hidden">
				<!-- 遮罩层 -->
				<div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showMobileSidebar = false"></div>
				<!-- 抽屉面板 -->
				<transition name="slide">
				<aside class="absolute inset-y-0 left-0 w-64 max-w-[80vw] bg-white border-r border-divide shadow-2xl flex flex-col dark:bg-neutral-900">
					<div class="flex items-center justify-between h-12 px-3 border-b border-divide">
						<span class="text-sm font-medium text-charcoal-700 dark:text-neutral-100">导航</span>
						<button class="inline-flex h-8 w-8 items-center justify-center rounded-lg hover:bg-gray-100 transition-colors dark:hover:bg-neutral-800" @click="showMobileSidebar = false">
							<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
							</svg>
						</button>
					</div>
					<div class="flex-1 overflow-y-auto p-2">
						<div class="space-y-1">
							<button
								v-for="menu in navMenus"
								:key="menu.key"
								@click="handleMobileGo(menu.key)"
								:class="[
									'w-full text-left px-3 py-2 text-sm rounded-lg transition-colors duration-150',
									activeNavMenu === menu.key
										? 'bg-brand/10 text-brand font-medium'
										: 'text-gray-600 hover:text-charcoal-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-neutral-100 dark:hover:bg-neutral-800'
								]"
							>
								{{ menu.label }}
							</button>
						</div>
					</div>
				</aside>
				</transition>
			</div>
		</transition>

		<!-- 主内容区 -->
		<main class="flex-1 min-w-0 min-h-0 overflow-hidden bg-white px-4 md:px-6 dark:bg-black">
			<router-view />
		</main>

		<!-- 修改密码对话框 -->
		<ChangePasswordDialog v-model:open="showChangePasswordDialog" />
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore, useSystemStore } from '@/store';
import { ElMessage, ElMessageBox } from 'element-plus';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const systemStore = useSystemStore();
const showMobileSidebar = ref(false);
const showChangePasswordDialog = ref(false);

// 导航菜单配置
const navMenus = computed(() => {
	const baseMenus = [
		{ key: 'generate', label: '文章生成' },
		{ key: 'prompt-config', label: '提示词配置' },
		{ key: 'model-config', label: '模型配置' },
		{ key: 'history', label: '历史记录' },
	];
	
	// 如果配置了使用说明链接，添加使用说明菜单
	if (systemStore.usageDocUrl) {
		baseMenus.push({ key: 'usage-doc', label: '使用说明', isExternal: true });
	}
	
	// 如果是管理员，添加管理菜单
	if (userStore?.profile?.is_admin) {
		baseMenus.push(
			{ key: 'admin-members', label: '成员管理' },
			{ key: 'admin-records', label: '成员记录' },
			{ key: 'admin-system', label: '系统设置' }
		);
	}
	
	return baseMenus;
});

// 当前激活的菜单
const activeNavMenu = computed(() => {
	const routeMap = {
		'/web-solution-assistant': 'generate',
		'/history': 'history',
		'/history/detail': 'history',
		'/model-config': 'model-config',
		'/prompt-config': 'prompt-config',
		'/admin/members': 'admin-members',
		'/admin/records': 'admin-records',
		'/admin/system': 'admin-system',
	};
	return routeMap[route.path] || 'generate';
});

// 处理导航点击
const handleNavClick = (key) => {
	// 处理使用说明外部链接
	if (key === 'usage-doc') {
		let url = systemStore.usageDocUrl;
		if (url) {
			// 如果 URL 没有协议前缀，自动添加 https://
			if (!/^https?:\/\//i.test(url)) {
				url = 'https://' + url;
			}
			window.open(url, '_blank');
		}
		return;
	}
	
	const routeMap = {
		generate: '/web-solution-assistant',
		history: '/history',
		'model-config': '/model-config',
		'prompt-config': '/prompt-config',
		'admin-members': '/admin/members',
		'admin-records': '/admin/records',
		'admin-system': '/admin/system',
	};
	const targetRoute = routeMap[key];
	if (targetRoute) {
		router.push(targetRoute);
	}
};

// 移动端菜单点击
const handleMobileGo = (key) => {
	handleNavClick(key);
	showMobileSidebar.value = false;
};

// 退出登录
const handleLogout = async () => {
	try {
		await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
			confirmButtonText: '确定',
			cancelButtonText: '取消',
			type: 'warning',
		});
		userStore.resetToken();
		userStore.resetProfile();
		ElMessage.success('已退出登录');
		router.push('/login');
	} catch {
		// 用户取消
	}
};

// 初始化获取系统配置
onMounted(() => {
	systemStore.fetchPublicConfigs();
});
</script>

<style scoped lang="scss">
/* 过渡动画 */
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active, .slide-leave-active { transition: transform .22s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }

</style>

