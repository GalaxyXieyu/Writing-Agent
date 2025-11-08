<template>
	<li
		:class="cn(
			'relative',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</li>
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

