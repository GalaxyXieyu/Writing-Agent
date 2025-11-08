<template>
	<div
		:class="cn(
			'flex h-16 items-center border-b px-6',
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

