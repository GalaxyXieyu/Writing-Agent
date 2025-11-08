import { http } from './request';

const VITE_API_BASE_PREFIX = import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847';
const API_PREFIX = '/api';
const BASE = `${VITE_API_BASE_PREFIX}${API_PREFIX}/model-config`;

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
