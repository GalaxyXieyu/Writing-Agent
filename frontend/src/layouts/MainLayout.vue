<template>
	<div class="flex h-screen flex-col bg-background">
		<!-- 顶部 Header -->
		<header class="flex h-16 shrink-0 items-center justify-between border-b bg-background px-3 sm:px-4 md:px-6">
			<div class="flex items-center gap-6">
				<h1 class="text-base sm:text-lg font-semibold text-foreground whitespace-nowrap">AI 写作助手</h1>
				
				<!-- 桌面端横向导航菜单 -->
				<nav class="hidden md:flex items-center gap-1">
					<button
						v-for="menu in navMenus"
						:key="menu.key"
						@click="handleNavClick(menu.key)"
						:class="[
							'px-3 py-1.5 text-sm rounded-md transition-colors',
							activeNavMenu === menu.key
								? 'bg-primary/10 text-primary font-medium'
								: 'text-muted-foreground hover:text-foreground hover:bg-accent'
						]"
					>
						{{ menu.label }}
					</button>
				</nav>

				<!-- 移动端汉堡按钮 -->
				<button
					class="md:hidden inline-flex h-9 w-9 items-center justify-center rounded hover:bg-accent"
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
						<button class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-muted-foreground hover:text-foreground">
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
				<div class="absolute inset-0 bg-black/40" @click="showMobileSidebar = false"></div>
				<!-- 抽屉面板 -->
				<transition name="slide">
				<aside class="absolute inset-y-0 left-0 w-64 max-w-[80vw] bg-background border-r shadow-xl flex flex-col">
					<div class="flex items-center justify-between h-12 px-3 border-b">
						<span class="text-sm font-medium">导航</span>
						<button class="inline-flex h-8 w-8 items-center justify-center rounded hover:bg-accent" @click="showMobileSidebar = false">
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
									'w-full text-left px-3 py-2 text-sm rounded-md transition-colors',
									activeNavMenu === menu.key
										? 'bg-primary/10 text-primary font-medium'
										: 'text-muted-foreground hover:text-foreground hover:bg-accent'
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
		<main class="flex-1 min-w-0 min-h-0 overflow-hidden bg-background px-3 sm:px-4 md:px-6">
			<router-view />
		</main>

		<!-- 修改密码对话框 -->
		<ChangePasswordDialog v-model:open="showChangePasswordDialog" />
	</div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/store';
import { ElMessage, ElMessageBox } from 'element-plus';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
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
	
	// 如果是管理员，添加管理菜单
	if (userStore?.profile?.is_admin) {
		baseMenus.push(
			{ key: 'admin-members', label: '成员管理' },
			{ key: 'admin-records', label: '成员记录' }
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
	};
	return routeMap[route.path] || 'generate';
});

// 处理导航点击
const handleNavClick = (key) => {
	const routeMap = {
		generate: '/web-solution-assistant',
		history: '/history',
		'model-config': '/model-config',
		'prompt-config': '/prompt-config',
		'admin-members': '/admin/members',
		'admin-records': '/admin/records',
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
</script>

<style scoped lang="scss">
/* 过渡动画 */
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-enter-active, .slide-leave-active { transition: transform .22s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }

/* 主题色 */
.bg-primary\/10 {
	background: linear-gradient(90deg, rgba(165, 151, 245, 0.1) 1%, rgba(85, 113, 255, 0.1) 98%);
}

.text-primary {
	background: linear-gradient(90deg, #a597f5 1%, #5571ff 98%);
	-webkit-background-clip: text;
	-webkit-text-fill-color: transparent;
	background-clip: text;
}
</style>

