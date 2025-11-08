<template>
	<div :class="cn('p-6 pt-0', className)" v-bind="$attrs">
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

