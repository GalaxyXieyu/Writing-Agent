# 解决方案助手Web端

## 目录结构

```text
├── .env.development                开发环境
├── .env.production                 生产环境
├── .eslintignore
├── .eslintrc.cjs
├── .gitignore
├── .prettierignore
├── .prettierrc.cjs
├── cz-config.cjs
├── index.html
├── jsconfig.json
├── package.json
├── README.md
├── vite.config.js
└── src
    ├── components                  全局组件
    ├── pages                       视图页面
    ├── service                     封装API请求，统一用`api.`前缀命名，
    ├── static                      静态资源
    ├── store                       Pinia 状态管理
    ├── utils                       工具类
    ├── App.vue
    ├── main.js
    ├── pages.json                  uni-app 页面路由配置
    └── main.js
```

## 软件架构

1. @dcloudio/uni-app: 3.0.0-3090620231104002
2. @dcloudio/uni-ui: ^1.4.28
3. vue: ^3.3.7
4. pinia: 2.0.36
5. pinia-plugin-persistedstate: ^3.2.0
6. vueuse: ^10.6.1
7. dayjs: ^1.11.10
8. @microsoft/fetch-event-source: ^2.0.1
9. sass: ^1.69.5
10. nodejs: v20.0.0
11. vite: 4.0.3
12. eslint: ^8.54.0
13. prettier: ^3.1.0
14. commitizen: ^4.3.0
    > 超过此版本的其他版本会造成自定义 scope 没法正常输入，可以在 [No scope question error](https://github.com/leoforfree/cz-customizable/issues/215)、[Fix custom scopes - Add askAnswered to true](https://github.com/leoforfree/cz-customizable/pull/214) 这个两个 issue 上了解此问题
15. husky: ^8.0.3

## 安装

`yarn install` 或 `pnpm instal` 或 `npm install`

> 使用 `npm` 如出现下载不了依赖或是比较慢的时候，可以切换为淘宝镜像
> `npm config set registry http://registry.npm.taobao.org/`

## 使用说明

1. 安装完成后会自动执行 `package.json` 里的 `prepare` 脚本，此脚本是生成 `.husky` 的文件夹
2. 执行 `package.json` 里的 `hooks` 脚本，此脚本会在 `.husky` 目录下生成一个 `pre-commit` 脚本文件
3. 执行 `package.json` 里的 `commit-msg` 脚本，此脚本会在 `.husky` 目录下生成一个 `commit-msg` 脚本文件，当提交代码时会触发校验提交信息是否符合设定的规范
4. 执行 `package.json` 里的 `dev:h5` 脚本，启动本地的 H5 开发环境

## Pinia 状态库使用例子

定义模块，在 `src/store/modules` 目录并在其下面创建 `user.js`

```javascript
import { defineStore } from 'pinia';

export const useUserStore = defineStore(
	'userStore',
	() => {
		// 初始数据
		const profile = ref({});

		/**
		 * @description: 保存用户信息
		 * @param {object} info
		 * @return {void}
		 */
		const setProfile = (info) => {
			profile.value = info;
		};

		return {
			profile,
			setProfile,
		};
	},
	// 持久化
	{
		// 网页模式
		// persist: true,
		// 兼容多端模式
		persist: {
			storage: {
				getItem: (key) => {
					return uni.getStorageSync(key);
				},
				setItem: (key, value) => {
					return uni.setStorageSync(key, value);
				},
			},
		},
	},
);
```

## API 接口定义例子

定义模块，在 `src/service/modules` 目录并在其下面创建 `api.solution.js` 文件


# 启动打包流程
## 执行 `package.json` 中的 `dev:h5-test` 为本地启动
## 执行 `package.json` 中的 `build:h5-web-test` 为项目打包
