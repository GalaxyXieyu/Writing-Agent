/**
 * @description: 请求拦截器，拦截非stream流式请求
 * @param {object} opt
 * @return {promise}
 */
export const http = (opt) => {
	return new Promise((resolve, reject) => {
		uni.request({
			...opt,
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data);
				} else {
					uni.showToast({
						icon: 'error',
						title: res.data?.message || '请求错误',
					});
					reject(res);
				}
			},
			// 网络错误或异常
			fail: (err) => {
				uni.showToast({
					icon: 'none',
					title: '网络错误或异常',
				});
				reject(err);
			},
		});
	});
};
