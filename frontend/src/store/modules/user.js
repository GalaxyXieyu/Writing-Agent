import { defineStore } from 'pinia';
import { ref } from 'vue';
import { verifyTokenExpired } from '@/service/api.solution';
import { useRouterStore } from '@/store';
import { ElMessage } from 'element-plus';
// import { ROUTER_BASE, LOGIN_ROUTE_MAP, HOME_ROUTE_MAP } from '@/constants';

export const useUserStore = defineStore(
	'userStore',
	() => {
		// 初始数据
		const profile = ref({});
		const token = ref('');

		/**
		 * @description: 保存用户信息
		 * @param {object} info
		 * @return {void}
		 */
		const setProfile = (info) => {
			profile.value = info || {};
			// 兼容旧字段：如果未提供 mobile，则用 user_id 兜底
			if (!profile.value.mobile && profile.value.user_id) {
				profile.value.mobile = profile.value.user_id;
			}
		};

		/**
		 * @description: 保存token
		 * @param {string} value
		 * @return {void}
		 */
		const setToken = (value) => {
			token.value = value;
		};

		/**
		 * @description: 重置token
		 * @return {void}
		 */
		const resetToken = () => {
			token.value = '';
		};

		/**
		 * @description: 重置用户信息
		 * @return {void}
		 */
		const resetProfile = () => {
			profile.value = {};
		};

		/**
		 * @description: 验证token是否过期
		 * @param {string} path 当前路径
		 * @return {void}
		 */
		const verifyToken = async (path) => {
			function redirectLogin(message = '登录已过期，请重新登录') {
				ElMessage.warning(message);
				resetToken();
				resetProfile();
				// 路由跳转需要在组件中使用 useRouter
				window.location.href = '/web/web-solution-assistant';
			}
		};

		return {
			profile,
			token,
			setToken,
			resetToken,
			setProfile,
			resetProfile,
			verifyToken,
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
