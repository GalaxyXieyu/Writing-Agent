import { http } from './request';

const BASE = (import.meta.env.VITE_BASE_API_HOST || 'http://localhost:29847');
const PROXY = BASE.endsWith('/api') ? '' : '/api';

export const adminCreateInvite = ({ expire_hours = 24 } = {}) => {
  return http({ method: 'POST', url: `${BASE}${PROXY}/admin/invite/create`, data: { expire_hours } });
};

export const adminListUsers = ({ kw = '', pageNum = 1, pageSize = 50 } = {}) => {
  return http({ method: 'GET', url: `${BASE}${PROXY}/admin/users`, params: { kw, pageNum, pageSize } });
};

export const adminResetPassword = ({ user_id, new_password }) => {
  return http({ method: 'POST', url: `${BASE}${PROXY}/admin/users/reset-password`, data: { user_id, new_password } });
};

export const adminSetStatus = ({ user_id, status }) => {
  return http({ method: 'POST', url: `${BASE}${PROXY}/admin/users/status`, data: { user_id, status } });
};

export const adminListRecords = ({ member_user_id = '', member_phone = '', type = '', kw = '', time_from = '', time_to = '', pageNum = 1, pageSize = 50 } = {}) => {
  return http({ method: 'GET', url: `${BASE}${PROXY}/admin/records`, params: { member_user_id, member_phone, type, kw, time_from, time_to, pageNum, pageSize } });
};
