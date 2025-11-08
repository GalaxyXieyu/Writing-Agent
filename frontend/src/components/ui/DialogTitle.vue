<template>
	<h2
		:class="cn(
			'text-lg font-semibold leading-none tracking-tight',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</h2>
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

