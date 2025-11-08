<template>
	<div
		:class="cn(
			'flex-1 overflow-y-auto p-2',
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

