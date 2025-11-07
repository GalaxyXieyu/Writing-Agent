<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app';
import { useRouterStore,useUserStore } from '@/store';
// 自定义滚动条
import 'simplebar-vue/dist/simplebar.min.css';

/**
 * @description: 根据设备端重定向到移动端或WEB端的首页
 * @return {void}
 */
const redirectHost = () => {
  location.href = `https://tianshu.fits.com.cn:${import.meta.env.VITE_FE_PORT}/web/#/`;

};

onLaunch(async (options) => {
	const userStore = useUserStore();

	// 部分功能需要使用到用户唯一Id记录用户使用情况
  userStore.setProfile({ name: "张三", mobile: "12345678910" });
	const routerStore = useRouterStore();
	const routeMap = {
    'pages/web-solution-assistant/index': 'solution',
	};
	routerStore.setCurrentRoute(routeMap[options.path]);

});
onShow(() => {
	console.log('App Show');
});
onHide(() => {
	console.log('App Hide');
});
</script>

<style lang="scss">
/*每个页面公共css */
@import 'styles/globals.scss';

//.uni-app--showleftwindow {
//	.uni-left-window {
//		height: 100vh;
//	}
//}

body,
uni-page-body {
	background-color: #f9fbff;
}

uni-main {
	overflow: auto;
	height: 100%;
}

:deep(.simplebar-scrollbar) {
	&::before {
		background: linear-gradient(90deg, #a597f5 1%, #5571ff 98%);
	}
}

:deep(.simplebar-vertical) {
	width: 8px !important;
}

:deep(.simplebar-content-wrapper) {
	scroll-behavior: smooth;
}

/* #ifdef H5-WEB || H5-WEB-TEST */
::-webkit-scrollbar {
	width: 5px;
	height: 4px;
}

::-webkit-scrollbar-thumb {
	background-color: #00ccff;
	border-radius: 5px;
}
/* #endif */
</style>
