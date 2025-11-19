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
		validator: (value) => ['default', 'destructive', 'outline', 'brand', 'secondary', 'ghost', 'link'].includes(value),
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
	const base = 'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium transition duration-150 disabled:pointer-events-none disabled:opacity-50 outline-none active:scale-[0.98]';
	
	const variants = {
		default: 'bg-brand text-white hover:bg-brand/90 shadow-sm hover:shadow-md',
		destructive: 'bg-destructive text-white hover:bg-destructive/90',
		outline: 'border-2 border-brand text-brand bg-white hover:bg-brand/5 dark:bg-neutral-950 dark:hover:bg-brand/10',
		brand: 'bg-brand text-white hover:bg-brand/90 shadow-sm hover:shadow-md',
		secondary: 'bg-gray-100 text-charcoal-700 hover:bg-gray-200 dark:bg-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-700',
		ghost: 'hover:bg-accent hover:text-accent-foreground',
		link: 'text-brand underline-offset-4 hover:underline hover:text-brand/80',
	};
	
	const sizes = {
		default: 'h-9 px-6 py-2',
		sm: 'h-8 rounded-lg gap-1.5 px-4',
		lg: 'h-11 rounded-xl px-8',
		icon: 'h-9 w-9',
		'icon-sm': 'h-8 w-8',
		'icon-lg': 'h-10 w-10',
	};
	
	return cn(base, variants[props.variant], sizes[props.size], props.className);
});
</script>

