import axios from 'axios';
import { ElMessage } from 'element-plus';

// 从 Pinia 持久化或 localStorage 获取 token（无依赖注入，避免在 app 启动前使用 store）
export const getToken = () => {
  try {
    const raw = localStorage.getItem('userStore');
    if (!raw) return '';
    const data = JSON.parse(raw);
    return data?.token || '';
  } catch {
    return '';
  }
};

// 全局请求拦截器：自动携带 Authorization 头
axios.interceptors.request.use(
  (config) => {
    const url = (config.url || '').toLowerCase();
    const skipAuthPaths = ['/login', '/register', '/register-with-invite', '/register-admin'];
    const shouldSkip = skipAuthPaths.some(p => url.endsWith(p) || url.includes(`${p}?`));
    if (!shouldSkip) {
      const token = getToken();
      if (token) {
        config.headers = config.headers || {};
        // 若已手动传入 Authorization，则不覆盖
        if (!config.headers.Authorization) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * @description: 请求拦截器，拦截非stream流式请求
 * @param {object} opt
 * @return {promise}
 */
export const http = (opt) => {
	return axios(opt)
		.then((response) => {
			return response.data;
		})
		.catch((error) => {
			if (error.response) {
				const data = error.response.data || {};
				// 兼容后端使用 HTTPException(detail=...) 的返回格式
				const message = data.message || data.detail || data.error || data.msg || `请求错误(${error.response.status})`;
				ElMessage.error(message);
			} else {
				ElMessage.error('网络错误或异常');
			}
			return Promise.reject(error);
		});
};

// 携带 Bearer Token 的请求封装
export const httpAuth = (opt = {}) => {
  const token = getToken();
  const headers = Object.assign({}, opt.headers || {}, token ? { Authorization: `Bearer ${token}` } : {});
  return http({ ...opt, headers });
};
