import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

// 创建实例
const pinia = createPinia();
// 使用持久化插件
pinia.use(piniaPluginPersistedstate);

// 给 main.js 使用
export default pinia;


export * from './modules/user';
export * from './modules/router';
export * from './modules/system';
