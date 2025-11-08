<template>
	<aside
		:class="cn(
			'flex h-full w-64 flex-col border-r bg-background',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</aside>
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

