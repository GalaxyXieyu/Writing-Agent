<template>
	<aside
		:class="cn(
			'flex h-full flex-col border-r bg-background transition-all duration-300',
			'w-16 sm:w-20 md:w-56 lg:w-64 xl:w-72 flex-shrink-0',
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</aside>
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

