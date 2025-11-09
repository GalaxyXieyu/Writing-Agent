import { http } from './request';

const VITE_API_BASE_PREFIX = import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847';
// 当 BASE 以 /api 结尾时，不再追加代理前缀，避免出现 /api/api 重复
const VITE_API_PROXY_PREFIX = VITE_API_BASE_PREFIX.endsWith('/api') ? '' : '/api';
const BASE = `${VITE_API_BASE_PREFIX}${VITE_API_PROXY_PREFIX}/model-config`;

export const modelConfigApi = {
  getList(params) {
    return http({ method: 'GET', url: `${BASE}/list`, params });
  },
  getDetail(modelId) {
    return http({ method: 'GET', url: `${BASE}/${modelId}` });
  },
  create(data) {
    return http({ method: 'POST', url: `${BASE}/create`, data });
  },
  update(modelId, data) {
    return http({ method: 'PUT', url: `${BASE}/${modelId}` , data});
  },
  delete(modelId) {
    return http({ method: 'DELETE', url: `${BASE}/${modelId}` });
  },
  setDefault(modelId) {
    return http({ method: 'POST', url: `${BASE}/set-default`, params: { model_id: modelId } });
  },
  getDefault(userId) {
    return http({ method: 'GET', url: `${BASE}/default`, params: { user_id: userId } });
  }
}
