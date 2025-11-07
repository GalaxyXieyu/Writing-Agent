module.exports = {
	parser: 'vue-eslint-parser',
	env: {
		browser: true,
		es2021: true,
		node: true,
	},
	extends: ['plugin:vue/vue3-recommended', 'prettier', 'plugin:prettier/recommended'],
	overrides: [
		{
			env: {
				node: true,
			},
			files: ['.eslintrc.{js,cjs}'],
			parserOptions: {
				sourceType: 'script',
			},
		},
	],
	parserOptions: {
		ecmaVersion: 'latest',
		sourceType: 'module',
		ecmaFeatures: {
			jsx: true,
		},
	},
	plugins: ['vue', 'prettier'],
	rules: {
		// override/add rules settings here
		'vue/multi-word-component-names': 'off',
	},
};
