import { http } from './request';

const BASE_URL = import.meta.env.VITE_API_BASE || '/api';

/**
 * 修改密码
 * @param {object} data - { old_password, new_password }
 * @returns {Promise}
 */
export const changePassword = async (data) => {
  const response = await http({
    url: `${BASE_URL}/user/change-password`,
    method: 'post',
    data,
  });
  
  // 后端返回格式为 { code, message, type, data }
  if (response.code === 200) {
    return response.data;
  } else {
    throw new Error(response.message || '修改密码失败');
  }
};

/**
 * 获取用户信息
 * @returns {Promise}
 */
export const getUserProfile = async () => {
  const response = await http({
    url: `${BASE_URL}/user/profile`,
    method: 'get',
  });
  
  if (response.code === 200) {
    return response.data;
  } else {
    throw new Error(response.message || '获取用户信息失败');
  }
};

/**
 * 更新用户信息
 * @param {object} data - { name, email, etc. }
 * @returns {Promise}
 */
export const updateUserProfile = async (data) => {
  const response = await http({
    url: `${BASE_URL}/user/profile`,
    method: 'put',
    data,
  });
  
  if (response.code === 200) {
    return response.data;
  } else {
    throw new Error(response.message || '更新用户信息失败');
  }
};
