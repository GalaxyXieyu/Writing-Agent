<template>
	<button
		:class="cn(
			'flex items-center w-full text-left px-3 py-2 mx-1 rounded-lg text-sm text-gray-600 hover:text-foreground hover:bg-gray-100 transition-colors duration-150 dark:text-gray-300 dark:hover:bg-neutral-800',
			className
		)"
		@click="handleClick"
		v-bind="$attrs"
	>
		<slot />
	</button>
</template>

<script setup>
import { cn } from '@/lib/utils';
import { inject } from 'vue';

const emit = defineEmits(['click']);

const props = defineProps({
	className: {
		type: String,
		default: '',
	},
});

const closeDropdown = inject('closeDropdown', null);

const handleClick = (event) => {
	emit('click', event);
	if (closeDropdown) {
		closeDropdown();
	}
};
</script>

