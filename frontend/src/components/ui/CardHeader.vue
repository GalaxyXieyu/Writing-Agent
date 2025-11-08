<template>
	<div :class="cn('flex flex-col space-y-1.5 p-6', className)" v-bind="$attrs">
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

