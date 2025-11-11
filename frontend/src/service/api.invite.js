import { http } from './request';
const BASE = (import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847');
const PROXY = BASE.endsWith('/api') ? '' : '/api';

export const registerWithInvite = ({ username, password, invite_code }) => {
  return http({ method: 'POST', url: `${BASE}${PROXY}/register-with-invite`, data: { username, password, invite_code } });
};
