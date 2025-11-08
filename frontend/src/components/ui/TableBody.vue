<template>
	<tbody
		:class="cn('[&_tr:last-child]:border-0', className)"
		v-bind="$attrs"
	>
		<slot />
	</tbody>
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

