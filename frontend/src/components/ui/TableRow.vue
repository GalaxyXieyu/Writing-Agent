<template>
	<tr
		:class="cn(
			'border-b border-divide transition-colors duration-150 hover:bg-gray-50 data-[state=selected]:bg-gray-50 dark:hover:bg-neutral-800 dark:data-[state=selected]:bg-neutral-800',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</tr>
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

