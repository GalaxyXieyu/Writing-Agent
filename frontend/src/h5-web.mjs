// INFO: H5-WEB环境下使用的页面路由配置信息
const router = {
	// 组件自动导入配置
	easycom: {
		// 是否开启自动扫描
		autoscan: true,
		custom: {
			// uni-ui 规则如下配置
			'^uni-(.*)': '@dcloudio/uni-ui/lib/uni-$1/uni-$1.vue',
			SvgIcon: '@/components/SvgIcon/index.vue',
			NonData: '@/components/NonData/index.vue',
		},
	},
	pages: [
		// pages数组中第一项表示应用启动页，参考：https://uniapp.dcloud.io/collocation/pages
		{
			path: 'pages/web-solution-assistant/index',
			style: {
				navigationBarTitleText: '解决方案助手',
			},
		},

	],
};

export default router;
