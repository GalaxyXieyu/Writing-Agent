import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useRouterStore = defineStore(
	'routerStore',
	() => {
		/** 定义菜单项 */
		const menuList = [
			{
				icon: 'chat',
				name: 'solution',
				route: '/web-solution-assistant',
				text: '解决方案助手',
			},
		];

		/** 当前选中的路由 */
		const currentRoute = ref({});

		/**
		 * @description: 设置当前路由
		 * @param {string} name
		 * @return {void}
		 */
		const setCurrentRoute = (name) => {
			const route = menuList.find((el) => el.name === name);
			// INFO: 找不到时设置为默认首页
			currentRoute.value = route?.name ? route : menuList[0];
		};

		return {
			menuList,
			currentRoute,
			setCurrentRoute,
		};
	},
	// 持久化
	{
		// 网页模式
		// persist: true,
		// 兼容多端模式
		persist: {
			storage: {
				getItem: (key) => {
					return localStorage.getItem(key);
				},
				setItem: (key, value) => {
					return localStorage.setItem(key, value);
				},
			},
		},
	},
);
