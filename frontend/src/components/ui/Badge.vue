<template>
	<span
		:class="cn(
			'inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-semibold transition-colors',
			'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
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
		validator: (value) => ['default', 'secondary', 'destructive', 'outline'].includes(value),
	},
	className: {
		type: String,
		default: '',
	},
});

const variants = {
	default: 'bg-primary text-primary-foreground',
	secondary: 'bg-secondary text-secondary-foreground',
	destructive: 'bg-destructive text-destructive-foreground',
	outline: 'border border-input text-foreground',
};
</script>

