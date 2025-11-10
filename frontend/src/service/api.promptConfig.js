import { http } from './request';

const VITE_API_BASE_PREFIX = import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847';
// 当 BASE 以 /api 结尾时，不再追加代理前缀，避免出现 /api/api 重复
const VITE_API_PROXY_PREFIX = VITE_API_BASE_PREFIX.endsWith('/api') ? '' : '/api';
const BASE = `${VITE_API_BASE_PREFIX}${VITE_API_PROXY_PREFIX}/prompt-config`;

export const promptConfigApi = {
  getList() {
    return http({ method: 'GET', url: `${BASE}/list` });
  },
  getByType(promptType) {
    return http({ method: 'GET', url: `${BASE}/type/${promptType}` });
  },
  getById(id) {
    return http({ method: 'GET', url: `${BASE}/${id}` });
  },
  create(data) {
    return http({ method: 'POST', url: `${BASE}/create`, data });
  },
  update(id, data) {
    return http({ method: 'PUT', url: `${BASE}/${id}`, data });
  },
  updateByType(promptType, data) {
    return http({ method: 'PUT', url: `${BASE}/type/${promptType}`, data });
  },
  delete(id) {
    return http({ method: 'DELETE', url: `${BASE}/${id}` });
  },
};

