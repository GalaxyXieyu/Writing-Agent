<template>
	<label
		:for="forId"
		:class="cn(
			'text-sm font-medium leading-none text-charcoal-700 peer-disabled:cursor-not-allowed peer-disabled:opacity-70 dark:text-neutral-200',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</label>
</template>

<script setup>
import { cn } from '@/lib/utils';

defineProps({
	forId: {
		type: String,
		default: '',
	},
	className: {
		type: String,
		default: '',
	},
});
</script>

