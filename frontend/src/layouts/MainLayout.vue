<template>
	<div class="flex h-screen flex-col bg-background">
		<!-- 顶部 Header -->
		<header class="flex h-16 shrink-0 items-center justify-between border-b bg-background px-3 sm:px-4 md:px-6">
			<div class="flex items-center gap-2 sm:gap-3 md:gap-4">
				<!-- 小屏汉堡按钮：仅在 md 以下显示，用于打开抽屉侧边栏 -->
				<button
					class="md:hidden inline-flex h-9 w-9 items-center justify-center rounded hover:bg-accent"
					aria-label="打开侧边栏"
					@click="showMobileSidebar = true"
				>
					<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
					</svg>
				</button>
				<h1 class="text-base sm:text-lg font-semibold text-foreground">AI 写作助手</h1>
			</div>
			<div class="flex items-center gap-2 sm:gap-3 md:gap-4">
				<DropdownMenu>
					<template #trigger>
						<button class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-muted-foreground hover:text-foreground">
							<span class="hidden sm:inline">{{ userStore.profile.name || '管理员' }}</span>
							<span class="sm:hidden">管理员</span>
							<svg class="h-3 w-3 sm:h-4 sm:w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>
					</template>
					<DropdownMenuItem @click="handleLogout">退出登录</DropdownMenuItem>
				</DropdownMenu>
			</div>
		</header>

		<div class="flex flex-1 min-h-0">
			<!-- 侧边栏 -->
			<!-- 桌面侧边栏：md 及以上展示，常驻 -->
			<Sidebar class="hidden md:flex flex-shrink-0">
				<SidebarContent>
					<SidebarMenu>
						<SidebarMenuItem>
							<SidebarMenuButton
								:isActive="activeSidebarMenu === 'generate'"
								@click="handleSidebarSelect('generate')"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
								<template #text>
									<span>文章生成</span>
								</template>
							</SidebarMenuButton>
						</SidebarMenuItem>
						<SidebarMenuItem>
							<SidebarMenuButton
								:isActive="activeSidebarMenu === 'prompt-config'"
								@click="handleSidebarSelect('prompt-config')"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
								</svg>
								<template #text>
									<span>提示词配置</span>
								</template>
							</SidebarMenuButton>
						</SidebarMenuItem>
						<SidebarMenuItem>
							<SidebarMenuButton
								:isActive="activeSidebarMenu === 'model-config'"
								@click="handleSidebarSelect('model-config')"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
								</svg>
								<template #text>
									<span>模型配置</span>
								</template>
							</SidebarMenuButton>
						</SidebarMenuItem>
						<SidebarMenuItem>
							<SidebarMenuButton
								:isActive="activeSidebarMenu === 'history'"
								@click="handleSidebarSelect('history')"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								<template #text>
									<span>历史记录</span>
								</template>
							</SidebarMenuButton>
						</SidebarMenuItem>
    <!-- 管理入口：仅管理员可见 -->
    <SidebarMenuItem v-if="userStore?.profile?.is_admin">
      <SidebarMenuButton
        :isActive="activeSidebarMenu === 'admin-members'"
        @click="handleSidebarSelect('admin-members')"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A4 4 0 018 16h8a4 4 0 012.879 1.804M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <template #text>
          <span>成员管理</span>
        </template>
      </SidebarMenuButton>
    </SidebarMenuItem>
    <SidebarMenuItem v-if="userStore?.profile?.is_admin">
      <SidebarMenuButton
        :isActive="activeSidebarMenu === 'admin-records'"
        @click="handleSidebarSelect('admin-records')"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <template #text>
          <span>成员记录</span>
        </template>
      </SidebarMenuButton>
    </SidebarMenuItem>
					</SidebarMenu>
				</SidebarContent>
			</Sidebar>

			<!-- 移动端抽屉侧边栏 -->
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
							<SidebarMenu>
								<SidebarMenuItem>
									<SidebarMenuButton :isActive="activeSidebarMenu === 'generate'" @click="handleMobileGo('generate')">
										<template #text><span>文章生成</span></template>
									</SidebarMenuButton>
								</SidebarMenuItem>
								<SidebarMenuItem>
									<SidebarMenuButton :isActive="activeSidebarMenu === 'prompt-config'" @click="handleMobileGo('prompt-config')">
										<template #text><span>提示词配置</span></template>
									</SidebarMenuButton>
								</SidebarMenuItem>
								<SidebarMenuItem>
									<SidebarMenuButton :isActive="activeSidebarMenu === 'model-config'" @click="handleMobileGo('model-config')">
										<template #text><span>模型配置</span></template>
									</SidebarMenuButton>
								</SidebarMenuItem>
								<SidebarMenuItem>
									<SidebarMenuButton :isActive="activeSidebarMenu === 'history'" @click="handleMobileGo('history')">
										<template #text><span>历史记录</span></template>
									</SidebarMenuButton>
								</SidebarMenuItem>
								<SidebarMenuItem v-if="userStore?.profile?.is_admin">
									<SidebarMenuButton :isActive="activeSidebarMenu === 'admin-members' || activeSidebarMenu === 'admin-records'" @click="handleMobileGo('admin-members')">
										<template #text><span>管理</span></template>
									</SidebarMenuButton>
								</SidebarMenuItem>
							</SidebarMenu>
						</div>
					</aside>
					</transition>
				</div>
			</transition>

			<!-- 主内容区：高度由父级控制，具体页面内部单独滚动 -->
			<main class="flex-1 min-w-0 min-h-0 overflow-hidden bg-background px-3 sm:px-4 md:px-6">
				<router-view />
			</main>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/store';
import { ElMessage, ElMessageBox } from 'element-plus';
import Sidebar from '@/components/ui/Sidebar.vue';
import SidebarHeader from '@/components/ui/SidebarHeader.vue';
import SidebarContent from '@/components/ui/SidebarContent.vue';
import SidebarMenu from '@/components/ui/SidebarMenu.vue';
import SidebarMenuItem from '@/components/ui/SidebarMenuItem.vue';
import SidebarMenuButton from '@/components/ui/SidebarMenuButton.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const showMobileSidebar = ref(false);

const activeSidebarMenu = computed(() => {
	const routeMap = {
		'/web-solution-assistant': 'generate',
		'/history': 'history',
		'/model-config': 'model-config',
		'/prompt-config': 'prompt-config',
    '/admin/members': 'admin-members',
    '/admin/records': 'admin-records',
	};
	return routeMap[route.path] || 'generate';
});

const handleSidebarSelect = (key) => {
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

const handleMobileGo = (key) => {
	handleSidebarSelect(key);
	showMobileSidebar.value = false;
};

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
</style>

