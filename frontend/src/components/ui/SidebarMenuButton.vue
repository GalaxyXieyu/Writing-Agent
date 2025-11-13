<template>
	<component
		:is="asChild ? 'slot' : 'button'"
		:class="cn(
			'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
			'hover:bg-accent hover:text-accent-foreground',
			'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
			isActive && 'bg-accent text-accent-foreground',
			// 响应式文字显示：在小屏幕上隐藏文字，只显示图标
			'group/sidebar',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
		<span
			class="transition-opacity duration-300 overflow-hidden"
		>
			<slot name="text" />
		</span>
	</component>
</template>

<script setup>
import { cn } from '@/lib/utils';

defineProps({
	asChild: {
		type: Boolean,
		default: false,
	},
	isActive: {
		type: Boolean,
		default: false,
	},
	className: {
		type: String,
		default: '',
	},
});
</script>

