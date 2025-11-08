<template>
	<PaginationLink
		:class="cn('gap-1 pr-2.5', className)"
		:size="size"
		@click="$emit('click', $event)"
		v-bind="$attrs"
	>
		<span class="hidden sm:inline">下一页</span>
		<svg
			class="h-4 w-4"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
		</svg>
	</PaginationLink>
</template>

<script setup>
import { cn } from '@/lib/utils';
import PaginationLink from './PaginationLink.vue';

defineProps({
	size: {
		type: String,
		default: 'default',
	},
	className: {
		type: String,
		default: '',
	},
});

defineEmits(['click']);
</script>

