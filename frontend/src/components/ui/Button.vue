<template>
	<button
		:class="buttonClass"
		v-bind="$attrs"
	>
		<slot />
	</button>
</template>

<script setup>
import { computed } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps({
	variant: {
		type: String,
		default: 'default',
		validator: (value) => ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'].includes(value),
	},
	size: {
		type: String,
		default: 'default',
		validator: (value) => ['default', 'sm', 'lg', 'icon', 'icon-sm', 'icon-lg'].includes(value),
	},
	className: {
		type: String,
		default: '',
	},
});

const buttonClass = computed(() => {
	const base = 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 outline-none focus-visible:ring-2 focus-visible:ring-ring';
	
	const variants = {
		default: 'bg-primary text-primary-foreground hover:bg-primary/90',
		destructive: 'bg-destructive text-white hover:bg-destructive/90',
		outline: 'border bg-background shadow-sm hover:bg-accent hover:text-accent-foreground',
		secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
		ghost: 'hover:bg-accent hover:text-accent-foreground',
		link: 'text-primary underline-offset-4 hover:underline',
	};
	
	const sizes = {
		default: 'h-9 px-4 py-2',
		sm: 'h-8 rounded-md gap-1.5 px-3',
		lg: 'h-10 rounded-md px-6',
		icon: 'h-9 w-9',
		'icon-sm': 'h-8 w-8',
		'icon-lg': 'h-10 w-10',
	};
	
	return cn(base, variants[props.variant], sizes[props.size], props.className);
});
</script>

