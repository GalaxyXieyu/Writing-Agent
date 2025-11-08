<template>
	<span
		aria-hidden
		:class="cn('flex h-9 w-9 items-center justify-center', className)"
		v-bind="$attrs"
	>
		<svg
			class="h-4 w-4"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01" />
		</svg>
		<span class="sr-only">更多页面</span>
	</span>
</template>

<script setup>
import { cn } from '@/lib/utils';

defineProps({
	className: {
		type: String,
		default: '',
	},
});
</script>

