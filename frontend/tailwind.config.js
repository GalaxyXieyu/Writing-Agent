/** @type {import('tailwindcss').Config} */
export default {
	darkMode: ['class'],
	content: [
		'./index.html',
		'./src/**/*.{vue,js,ts,jsx,tsx}',
	],
	theme: {
		container: {
			center: true,
			padding: {
				DEFAULT: '1rem',
				sm: '1rem',
				md: '2rem',
				lg: '2rem',
				xl: '2rem',
				'2xl': '2rem',
			},
		},
		extend: {
			fontFamily: {
				primary: ['Inter Display', 'sans-serif'],
				mono: ['DM Mono', 'monospace'],
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)',
			},
			colors: {
				// 设计系统颜色
				charcoal: {
					900: 'var(--color-charcoal-900)',
					800: 'var(--color-charcoal-800)',
					700: 'var(--color-charcoal-700)',
				},
				gray: {
					100: 'var(--color-gray-100)',
					200: 'var(--color-gray-200)',
					300: 'var(--color-gray-300)',
					400: 'var(--color-gray-400)',
					500: 'var(--color-gray-500)',
					600: 'var(--color-gray-600)',
				},
				brand: 'var(--color-brand)',
				
				// 语义化颜色
				divide: 'var(--divide)',
				primary: 'var(--primary)',
				'primary-light': 'var(--primary-light)',
				'footer-link': 'var(--footer-link)',
				canvas: 'var(--canvas)',
				'canvas-fill': 'var(--canvas-fill)',
				
				// Tailwind 兼容变量
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))',
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))',
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))',
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))',
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))',
				},
			},
			boxShadow: {
				aceternity: 'var(--shadow-aceternity)',
			},
			maxWidth: {
				'7xl': '80rem',
			},
		},
	},
	plugins: [],
};

