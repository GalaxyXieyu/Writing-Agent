import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store';

const routes = [
	{
		path: '/login',
		name: 'login',
		component: () => import('@/pages/login/index.vue'),
		meta: {
			title: '登录',
			requiresAuth: false,
		},
	},
	{
		path: '/',
		component: () => import('@/layouts/MainLayout.vue'),
		redirect: '/web-solution-assistant',
		meta: {
			requiresAuth: true,
		},
		children: [
			{
				path: '/web-solution-assistant',
				name: 'web-solution-assistant',
				component: () => import('@/pages/web-solution-assistant/index.vue'),
				meta: {
					title: '生成文章',
				},
			},
			{
				path: '/history',
				name: 'history',
				component: () => import('@/pages/history/index.vue'),
				meta: {
					title: '生成历史',
				},
			},
			{
				path: '/model-config',
				name: 'model-config',
				component: () => import('@/pages/model-config/index.vue'),
				meta: {
					title: '模型配置管理',
				},
			},
		],
	},
];

const router = createRouter({
	history: createWebHistory(import.meta.env.VITE_ROUTER_BASE || '/web/'),
	routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
	const userStore = useUserStore();
	const isAuthenticated = userStore.token && userStore.profile.name;

	if (to.meta.requiresAuth && !isAuthenticated) {
		next('/login');
	} else if (to.path === '/login' && isAuthenticated) {
		next('/web-solution-assistant');
	} else {
		next();
	}
});

export default router;

