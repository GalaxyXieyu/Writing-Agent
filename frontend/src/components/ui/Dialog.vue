<template>
	<Teleport to="body">
		<Transition
			enter-active-class="transition ease-out duration-200"
			enter-from-class="opacity-0"
			enter-to-class="opacity-100"
			leave-active-class="transition ease-in duration-150"
			leave-from-class="opacity-100"
			leave-to-class="opacity-0"
		>
			<div
				v-if="modelValue"
				class="fixed inset-0 z-50 flex items-center justify-center"
			>
				<div
					class="absolute inset-0 bg-black/50 backdrop-blur-sm"
					@click="handleOverlayClick"
				/>
				<Transition
					enter-active-class="transition ease-out duration-200"
					enter-from-class="opacity-0 scale-95"
					enter-to-class="opacity-100 scale-100"
					leave-active-class="transition ease-in duration-150"
					leave-from-class="opacity-100 scale-100"
					leave-to-class="opacity-0 scale-95"
				>
					<div
						v-if="modelValue"
						:class="cn(
							'relative z-10 flex w-full max-w-lg max-h-[85vh] overflow-hidden flex-col rounded-2xl border border-divide bg-white dark:bg-neutral-900 p-6 shadow-2xl',
							className
						)"
						@click.stop
					>
						<slot />
					</div>
				</Transition>
			</div>
		</Transition>
	</Teleport>
</template>

<script setup>
import { cn } from '@/lib/utils';

const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
	},
	closeOnOverlay: {
		type: Boolean,
		default: true,
	},
	className: {
		type: String,
		default: '',
	},
});

const emit = defineEmits(['update:modelValue']);

const handleOverlayClick = () => {
	if (props.closeOnOverlay) {
		emit('update:modelValue', false);
	}
};
</script>

