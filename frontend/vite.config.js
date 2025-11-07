import { defineConfig, loadEnv } from 'vite';
import uni from '@dcloudio/vite-plugin-uni';
import * as path from 'path';
import basicSsl from '@vitejs/plugin-basic-ssl';
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';
import prismjs from 'vite-plugin-prismjs';

// https://vitejs.dev/config/
export default async (option) => {
	const { mode } = option;
	const env = loadEnv(mode, process.cwd());
	console.log('🚀 ~ env:', process.env.UNI_CUSTOM_DEFINE, process.env.ROUTER_BASE, env.VITE_BASE_API_HOST);


	return defineConfig({
		/* 构建后静态文件指向/web/，代表在域名的/web目录下部署运行 */
		// base: routerBase,
		plugins: [
			uni(),
			basicSsl(),
			createSvgIconsPlugin({
				// 指定需要缓存的图标文件夹
				iconDirs: [path.resolve(process.cwd(), 'src/static/icons')],
				// 指定symbolId格式
				symbolId: 'icon-[dir]-[name]',
			}),
			prismjs({
				languages: 'all',
				plugins: [],
				theme: 'tomorrow',
			}),
		],
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
			include: ['vue', 'vuetify'],
		},
		server: {
			// INFO: 开启ssl需要引入`@vitejs/plugin-basic-ssl`
			https: false,
			host: '0.0.0.0',
			// 启动端口
			port: 8080,
			// 在HBuilder编辑器里的时候需要设置为false
			open: false,
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
