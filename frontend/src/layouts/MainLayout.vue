<template>
	<div class="flex h-screen flex-col bg-background">
		<!-- 顶部 Header -->
		<header class="flex h-16 shrink-0 items-center justify-between border-b bg-background px-6">
			<div class="flex items-center gap-4">
				<h1 class="text-lg font-semibold text-foreground">AI 写作助手</h1>
			</div>
			<div class="flex items-center gap-4">
				<DropdownMenu>
					<template #trigger>
						<button class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
							{{ userStore.profile.name || '管理员' }}
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>
					</template>
					<DropdownMenuItem @click="handleLogout">退出登录</DropdownMenuItem>
				</DropdownMenu>
			</div>
		</header>

		<div class="flex flex-1 overflow-hidden">
			<!-- 侧边栏 -->
			<Sidebar>
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
								<span>文章生成</span>
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
								<span>提示词配置</span>
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
								<span>模型配置</span>
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
								<span>历史记录</span>
							</SidebarMenuButton>
						</SidebarMenuItem>
					</SidebarMenu>
				</SidebarContent>
			</Sidebar>

			<!-- 主内容区 -->
			<main class="flex-1 overflow-hidden bg-background p-6">
				<router-view />
			</main>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue';
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

const activeSidebarMenu = computed(() => {
	const routeMap = {
		'/web-solution-assistant': 'generate',
		'/history': 'history',
		'/model-config': 'model-config',
		'/prompt-config': 'prompt-config',
	};
	return routeMap[route.path] || 'generate';
});

const handleSidebarSelect = (key) => {
	const routeMap = {
		generate: '/web-solution-assistant',
		history: '/history',
		'model-config': '/model-config',
		'prompt-config': '/prompt-config',
	};
	const targetRoute = routeMap[key];
	if (targetRoute) {
		router.push(targetRoute);
	}
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
// 使用 Tailwind CSS，不需要额外样式
</style>

