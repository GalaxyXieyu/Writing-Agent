<template>
  <div :class="['w-full', wrapperClass]">
    <div class="h-2.5 w-full rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
      <div
        class="h-full rounded-full bg-gradient-to-r from-orange-400 to-orange-500 transition-all duration-300 ease-out"
        :style="{ width: Math.max(0, Math.min(100, value)) + '%' }"
      />
    </div>
    <div v-if="showLabel" class="mt-1 text-xs text-muted-foreground text-right">{{ Math.floor(value) }}%</div>
  </div>
</template>

<script setup>
// 简单进度条（shadcn 风格）：用于上传与“解析中”的占位进度
const props = defineProps({
  value: { type: Number, default: 0 },
  showLabel: { type: Boolean, default: false },
  wrapperClass: { type: String, default: '' },
})
</script>

<style scoped>
.bg-muted { @apply bg-gray-200 dark:bg-gray-800; }
.bg-primary { @apply bg-indigo-500; }
.text-muted-foreground { @apply text-gray-500 dark:text-gray-400; }
</style>
