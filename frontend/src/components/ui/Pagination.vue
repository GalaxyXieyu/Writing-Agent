<template>
	<nav
		role="navigation"
		aria-label="pagination"
		:class="cn('mx-auto flex w-full justify-center', className)"
		v-bind="$attrs"
	>
		<slot />
	</nav>
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

