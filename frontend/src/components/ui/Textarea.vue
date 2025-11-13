<template>
	<textarea
		:value="modelValue"
		@input="handleInput"
		:maxlength="maxlength"
		:class="cn(
			'flex min-h-[32px] w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors',
			'placeholder:text-muted-foreground',
			'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
			'disabled:cursor-not-allowed disabled:opacity-50',
			'resize-y',
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

