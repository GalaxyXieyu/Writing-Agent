<template>
	<h3 :class="cn('font-semibold leading-none tracking-tight text-charcoal-700 dark:text-neutral-100', className)" v-bind="$attrs">
		<slot />
	</h3>
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

