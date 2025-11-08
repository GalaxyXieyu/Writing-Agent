import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import * as path from 'path';

// https://vitejs.dev/config/
export default ({ mode }) => {
	const env = loadEnv(mode, process.cwd());
	console.log('🚀 ~ env:', env.VITE_BASE_API_HOST);

	return defineConfig({
		base: '/web/',
		plugins: [
			vue(),
		],
		css: {
			preprocessorOptions: {
				scss: {
					api: 'modern-compiler',
					silenceDeprecations: ['legacy-js-api', 'import'],
				},
			},
		},
		resolve: {
			// 设置别名
			alias: {
				'@': path.resolve(__dirname, 'src'),
			},
		},
		define: {
			// 定义全局常量
			__VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
		},
		optimizeDeps: {
			include: ['vuetify'],
		},
		build: {
			sourcemap: false,
		},
		server: {
			// INFO: 开启ssl需要引入`@vitejs/plugin-basic-ssl`
			https: false,
			host: '0.0.0.0',
			// 启动端口（8080 被 ClashX 占用，改用 8081）
			port: 8081,
			// 在HBuilder编辑器里的时候需要设置为false
			open: false,
			hmr: {
				overlay: false,
			},
			// 设置代理
			proxy: {
				'/api': {
					target: env.VITE_BASE_API_HOST,
					changeOrigin: true,
					rewrite: (path) => path.replace(/^\/api/, ''),
					timeout: 180000,
				}
			},
		},
	});
};
