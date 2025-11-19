<template>
	<th
		:class="cn(
			'h-10 px-3 text-left align-middle font-medium text-gray-600 bg-gray-100 [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] dark:text-gray-300 dark:bg-neutral-800',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</th>
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

