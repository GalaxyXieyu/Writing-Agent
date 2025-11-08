<template>
	<div :class="cn('rounded-xl border bg-card text-card-foreground shadow-sm', className)" v-bind="$attrs">
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

