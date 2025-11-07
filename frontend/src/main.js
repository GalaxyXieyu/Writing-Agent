import { createSSRApp } from 'vue';

import App from './App.vue';
import pinia from '@/store';
import 'virtual:svg-icons-register';
import Simplebar from 'simplebar-vue';
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { vuetifyProTipTap } from './plugins/tiptap'; // 引入tiptap配置
// import {createVuetify} from "vuetify/dist/vuetify";
import 'vuetify-pro-tiptap/style.css'
import 'vuetify/styles'
import 'element-plus/dist/index.css'
import { createVuetify } from 'vuetify'
const vuetify = createVuetify()


export function createApp() {
	const app = createSSRApp(App);
	app.use(ElementPlus, {
		locale: zhCn,
	})
	app.use(vuetify)
	// 使用Vuetify和Vuetify Pro Tiptap插件
	app.use(vuetifyProTipTap);
	// 修复tiptap的警告
	app.config.unwrapInjectedRef = true;
	app.use(pinia);
	// 注册全局组件
	app.component('SimpleBar', Simplebar);

	return {
		app,
	};
}
