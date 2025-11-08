<template>
	<div
		:class="cn(
			'flex flex-col gap-2 text-center sm:text-left',
			className
		)"
		v-bind="$attrs"
	>
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

