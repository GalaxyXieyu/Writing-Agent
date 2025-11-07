module.exports = {
	// 达到 120 字符换行
	printWidth: 120,
	// 指定每个缩进级别的空格数: 2
	tabWidth: 2,
	// 用制表符而不是空格缩进行
	useTabs: true,
	// 行尾需要有分号
	semi: true,
	// 使用单引号而不是双引号
	singleQuote: true,
	// 仅在需要时在对象属性周围添加引号
	quoteProps: 'as-needed',
	// 在 JSX 中使用单引号而不是双引号
	jsxSingleQuote: false,
	// 尽可能在尾随逗号（包括 函数参数和调用）
	trailingComma: 'all',
	// 对象字面量中括号之间的空格，如 { foo: bar }
	bracketSpacing: true,
	// 将多行 HTML（HTML、JSX、Vue、Angular）元素的 > 放在最后一行的末尾，而不是单独放在下一行（不适用于自关闭元素）
	bracketSameLine: false,
	// 在唯一的箭头函数参数周围包含括号，如 (x) => x
	arrowParens: 'always',
	// 使用默认的折行标准
	proseWrap: 'preserve',
	// 指定 HTML、Vue、Angular 和 Handlebars 的全局空白敏感度，遵守 CSS display 属性的默认值
	htmlWhitespaceSensitivity: 'css',
	// 换行符使用 lf
	endOfLine: 'lf',
};
