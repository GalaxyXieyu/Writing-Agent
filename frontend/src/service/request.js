import axios from 'axios';
import { ElMessage } from 'element-plus';

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
				const message = error.response.data?.message || '请求错误';
				ElMessage.error(message);
			} else {
				ElMessage.error('网络错误或异常');
			}
			return Promise.reject(error);
		});
};
