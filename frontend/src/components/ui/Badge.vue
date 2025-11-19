<template>
	<span
		:class="cn(
			'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
			variants[variant],
			className
		)"
		v-bind="$attrs"
	>
		<slot />
	</span>
</template>

<script setup>
import { cn } from '@/lib/utils';

const props = defineProps({
	variant: {
		type: String,
		default: 'default',
		validator: (value) => ['default', 'brand', 'secondary', 'destructive', 'outline'].includes(value),
	},
	className: {
		type: String,
		default: '',
	},
});

const variants = {
	default: 'bg-charcoal-900 text-white dark:bg-white dark:text-black',
	brand: 'bg-brand/10 text-brand',
	secondary: 'bg-gray-100 text-charcoal-700 dark:bg-neutral-800 dark:text-neutral-100',
	destructive: 'bg-destructive/10 text-destructive',
	outline: 'border border-divide text-foreground',
};
</script>

