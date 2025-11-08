<template>
	<div
		@click="handleClick"
		:class="cn(
			'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 px-2 text-sm outline-none',
			'focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground',
			'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
			isSelected && 'bg-accent text-accent-foreground',
			className
		)"
		v-bind="$attrs"
	>
		<slot>{{ label }}</slot>
	</div>
</template>

<script setup>
import { cn } from '@/lib/utils';
import { inject, computed } from 'vue';

const props = defineProps({
	value: {
		type: [String, Number],
		required: true,
	},
	label: {
		type: String,
		default: '',
	},
	className: {
		type: String,
		default: '',
	},
});

const selectValue = inject('selectValue', computed(() => null));
const handleSelect = inject('handleSelect', null);

const isSelected = computed(() => {
	return selectValue?.value === props.value;
});

const handleClick = () => {
	if (handleSelect) {
		handleSelect(props.value, props.label || String(props.value));
	}
};
</script>

