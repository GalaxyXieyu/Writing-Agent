<template>
	<textarea
		:value="modelValue"
		@input="handleInput"
		:maxlength="maxlength"
		:class="cn(
			'flex min-h-[80px] w-full rounded-lg border-2 border-gray-300 bg-white px-3 py-2 text-sm transition-[border-color,box-shadow] duration-150 shadow-sm',
			'placeholder:text-gray-400',
			'hover:border-gray-400',
			'focus-visible:outline-none focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/20',
			'disabled:cursor-not-allowed disabled:opacity-50',
			'resize-y dark:bg-neutral-800 dark:border-neutral-600 dark:hover:border-neutral-500',
			className
		)"
		v-bind="$attrs"
	/>
</template>

<script setup>
import { cn } from '@/lib/utils';

const props = defineProps({
	modelValue: {
		type: String,
		default: '',
	},
	maxlength: {
		type: Number,
		default: undefined,
	},
	className: {
		type: String,
		default: '',
	},
});

const emit = defineEmits(['update:modelValue']);

const handleInput = (event) => {
	let value = event.target.value;
	if (props.maxlength && value.length > props.maxlength) {
		value = value.slice(0, props.maxlength);
	}
	emit('update:modelValue', value);
};
</script>

<style scoped>
/* 默认使用紧凑内边距，避免占用过多垂直空间 */
</style>

