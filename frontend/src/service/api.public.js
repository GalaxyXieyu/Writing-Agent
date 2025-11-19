import { http } from './request';

const BASE = (import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847');
const PROXY = BASE.endsWith('/api') ? '' : '/api';

export const getPublicConfigs = () => {
  return http({ method: 'GET', url: `${BASE}${PROXY}/public-configs` });
};



