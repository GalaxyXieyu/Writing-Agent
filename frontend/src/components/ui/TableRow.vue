<template>
	<tr
		:class="cn(
			'border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</tr>
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

