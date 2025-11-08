<template>
	<a
		:aria-current="isActive ? 'page' : undefined"
		:class="cn(
			buttonClass,
			isActive ? 'bg-background text-foreground' : '',
			className
		)"
		@click.prevent="handleClick"
		v-bind="$attrs"
	>
		<slot />
	</a>
</template>

<script setup>
import { computed } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps({
	isActive: {
		type: Boolean,
		default: false,
	},
	size: {
		type: String,
		default: 'icon',
		validator: (value) => ['default', 'sm', 'lg', 'icon'].includes(value),
	},
	className: {
		type: String,
		default: '',
	},
});

const emit = defineEmits(['click']);

const buttonClass = computed(() => {
	const base = 'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50';
	
	const variants = {
		default: props.isActive 
			? 'border bg-background shadow-sm h-9 px-4 py-2' 
			: 'hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2',
		sm: props.isActive
			? 'border bg-background shadow-sm h-8 rounded-md px-3'
			: 'hover:bg-accent hover:text-accent-foreground h-8 rounded-md px-3',
		lg: props.isActive
			? 'border bg-background shadow-sm h-10 rounded-md px-6'
			: 'hover:bg-accent hover:text-accent-foreground h-10 rounded-md px-6',
		icon: props.isActive
			? 'border bg-background shadow-sm h-9 w-9'
			: 'hover:bg-accent hover:text-accent-foreground h-9 w-9',
	};
	
	return cn(base, variants[props.size]);
});

const handleClick = (event) => {
	emit('click', event);
};
</script>

