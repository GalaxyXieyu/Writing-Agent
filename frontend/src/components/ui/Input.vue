<template>
	<input
		:type="type"
		:value="modelValue"
		@input="$emit('update:modelValue', $event.target.value)"
		:class="cn(
			'flex h-9 w-full rounded-lg border-2 border-gray-300 bg-white px-3 py-2 text-sm transition-[border-color,box-shadow] duration-150 shadow-sm',
			'file:border-0 file:bg-transparent file:text-sm file:font-medium',
			'placeholder:text-gray-400',
			'hover:border-gray-400',
			'focus-visible:outline-none focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/20',
			'disabled:cursor-not-allowed disabled:opacity-50',
			'dark:bg-neutral-800 dark:border-neutral-600 dark:hover:border-neutral-500',
			className
		)"
		v-bind="$attrs"
	/>
</template>

<script setup>
import { cn } from '@/lib/utils';

defineProps({
	type: {
		type: String,
		default: 'text',
	},
	modelValue: {
		type: [String, Number],
		default: '',
	},
	className: {
		type: String,
		default: '',
	},
});

defineEmits(['update:modelValue']);
</script>

