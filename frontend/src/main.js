import { createApp } from 'vue';

import App from './App.vue';
import router from './router';
import pinia from '@/store';
import Simplebar from 'simplebar-vue';
import ElementPlus from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { vuetifyProTipTap } from './plugins/tiptap';
// Tailwind CSS 必须在最前面，确保基础样式先加载
import '@/assets/index.css';
// 其他 UI 库样式
import 'vuetify-pro-tiptap/style.css';
import 'vuetify/styles';
import 'element-plus/dist/index.css';
import { createVuetify } from 'vuetify';

const vuetify = createVuetify();

const app = createApp(App);

app.use(ElementPlus, {
	locale: zhCn,
});
app.use(vuetify);
app.use(vuetifyProTipTap);
app.config.unwrapInjectedRef = true;
app.use(pinia);
app.use(router);
app.component('SimpleBar', Simplebar);

app.mount('#app');
