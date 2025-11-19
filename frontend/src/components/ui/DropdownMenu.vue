<template>
	<div class="relative inline-block text-left" ref="dropdownRef">
		<div @click="toggleMenu">
			<slot name="trigger" />
		</div>
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
					'absolute right-0 z-50 mt-2 w-56 origin-top-right rounded-xl bg-white/95 backdrop-blur-sm shadow-xl border border-divide focus:outline-none dark:bg-neutral-900/95',
					align === 'left' && 'left-0 right-auto',
					className
				)"
			>
				<div class="py-2">
					<slot />
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, provide } from 'vue';
import { cn } from '@/lib/utils';

const props = defineProps({
	align: {
		type: String,
		default: 'right',
		validator: (value) => ['left', 'right'].includes(value),
	},
	className: {
		type: String,
		default: '',
	},
});

const isOpen = ref(false);
const dropdownRef = ref(null);

const toggleMenu = () => {
	isOpen.value = !isOpen.value;
};

const closeMenu = () => {
	isOpen.value = false;
};

const handleClickOutside = (event) => {
	if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
		closeMenu();
	}
};

provide('closeDropdown', closeMenu);

onMounted(() => {
	document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
	document.removeEventListener('click', handleClickOutside);
});

defineExpose({
	closeMenu,
});
</script>

