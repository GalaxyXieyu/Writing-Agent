<template>
	<h3 :class="cn('font-semibold leading-none tracking-tight', className)" v-bind="$attrs">
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

