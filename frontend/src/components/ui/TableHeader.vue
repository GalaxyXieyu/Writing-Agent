<template>
	<thead
		:class="cn('[&_tr]:border-b', className)"
		v-bind="$attrs"
	>
		<slot />
	</thead>
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

