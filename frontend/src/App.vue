<script setup>
import { onMounted } from 'vue';
import { useRouterStore, useUserStore } from '@/store';
import { useRoute } from 'vue-router';
import 'simplebar-vue/dist/simplebar.min.css';

const userStore = useUserStore();
const routerStore = useRouterStore();
const route = useRoute();

onMounted(async () => {
	// 根据当前路由设置当前路由
	const routeMap = {
		'/web-solution-assistant': 'solution',
		'/history': 'solution',
		'/model-config': 'model-config',
	};
	const routeName = routeMap[route.path] || 'solution';
	routerStore.setCurrentRoute(routeName);
});
</script>

<template>
	<router-view />
</template>

<style lang="scss">
/*每个页面公共css */
@use 'styles/globals.scss';

/* 只在非登录页面应用背景色，避免覆盖登录页面的 Tailwind 样式 */
body:not(.login-page) {
	background-color: #f9fbff;
	overflow: hidden;
	height: 100vh;
}

html {
	overflow: hidden;
	height: 100vh;
}

#app {
	height: 100vh;
	overflow: hidden;
}

:deep(.simplebar-scrollbar) {
	&::before {
		background: linear-gradient(90deg, #a597f5 1%, #5571ff 98%);
	}
}

:deep(.simplebar-vertical) {
	width: 8px !important;
}

:deep(.simplebar-content-wrapper) {
	scroll-behavior: smooth;
}

::-webkit-scrollbar {
	width: 5px;
	height: 4px;
}

::-webkit-scrollbar-thumb {
	background-color: #cbd5e1;
	border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
	background-color: #94a3b8;
}

::-webkit-scrollbar-track {
	background-color: #f1f5f9;
	border-radius: 5px;
}
</style>
