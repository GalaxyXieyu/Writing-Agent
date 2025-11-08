<template>
	<div class="relative w-full overflow-auto">
		<table
			:class="cn('w-full caption-bottom text-sm', className)"
			v-bind="$attrs"
		>
			<slot />
		</table>
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

