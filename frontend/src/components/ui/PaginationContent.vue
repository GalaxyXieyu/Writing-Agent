<template>
	<ul
		:class="cn('flex flex-row items-center gap-1', className)"
		v-bind="$attrs"
	>
		<slot />
	</ul>
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

