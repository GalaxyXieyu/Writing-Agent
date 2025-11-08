<template>
	<button
		:class="cn(
			'block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors',
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

