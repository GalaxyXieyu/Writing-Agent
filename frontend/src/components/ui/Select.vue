<template>
	<div class="relative" ref="selectRef">
		<button
			type="button"
			@click="toggleOpen"
			:class="cn(
				'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors',
				'placeholder:text-muted-foreground',
				'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
				'disabled:cursor-not-allowed disabled:opacity-50',
				className
			)"
			:disabled="disabled"
			v-bind="$attrs"
		>
			<span :class="{ 'text-muted-foreground': !selectedLabel }">
				{{ selectedLabel || placeholder }}
			</span>
			<svg
				class="h-4 w-4 opacity-50 transition-transform"
				:class="{ 'rotate-180': isOpen }"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>
		<Transition
			enter-active-class="transition ease-out duration-100"
			enter-from-class="transform opacity-0 scale-95"
			enter-to-class="transform opacity-100 scale-100"
			leave-active-class="transition ease-in duration-75"
			leave-from-class="transform opacity-100 scale-100"
			leave-to-class="transform opacity-0 scale-95"
		>
			<div
				v-if="isOpen"
				:class="cn(
					'absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-popover text-popover-foreground shadow-md',
					contentClassName
				)"
			>
				<div class="p-1">
					<slot />
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, provide, watch } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps({
	modelValue: {
		type: [String, Number],
		default: null,
	},
	placeholder: {
		type: String,
		default: '请选择...',
	},
	disabled: {
		type: Boolean,
		default: false,
	},
	className: {
		type: String,
		default: '',
	},
	contentClassName: {
		type: String,
		default: '',
	},
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const selectRef = ref(null);
const selectedLabel = ref('');

const toggleOpen = () => {
	if (!props.disabled) {
		isOpen.value = !isOpen.value;
	}
};

const handleClickOutside = (event) => {
	if (selectRef.value && !selectRef.value.contains(event.target)) {
		isOpen.value = false;
	}
};

const handleSelect = (value, label) => {
	emit('update:modelValue', value);
	selectedLabel.value = label;
	isOpen.value = false;
};

provide('selectValue', computed(() => props.modelValue));
provide('handleSelect', handleSelect);

onMounted(() => {
	document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
	document.removeEventListener('click', handleClickOutside);
});

defineExpose({
	handleSelect,
});
</script>

