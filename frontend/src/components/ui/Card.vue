<template>
	<div :class="cn('rounded-2xl border-2 border-gray-200 bg-white text-card-foreground shadow-sm transition duration-200 hover:border-brand/30 hover:shadow-md dark:bg-neutral-800 dark:border-neutral-700 dark:hover:border-brand/30', className)" v-bind="$attrs">
		<slot />
	</div>
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

