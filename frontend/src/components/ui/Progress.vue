<template>
  <div :class="['w-full', wrapperClass]">
    <div class="h-2 w-full rounded bg-muted overflow-hidden">
      <div
        class="h-full bg-primary transition-all duration-200"
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
