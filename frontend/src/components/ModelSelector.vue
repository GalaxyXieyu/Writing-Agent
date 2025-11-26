<template>
	<div class="model-selector">
		<div class="selector-inner">
			<el-select 
				v-model="innerValue" 
				placeholder="请选择模型" 
				@change="onChange" 
				:loading="loading" 
				class="w-full"
			>
				<el-option v-for="m in list" :key="m.id" :label="`${m.name} (${m.model})`" :value="m.id"/>
			</el-select>
		</div>
	</div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useModelConfigStore } from '@/store/modules/modelConfig'

const props = defineProps({
  modelValue: { type: Number, default: null }
})
const emit = defineEmits(['update:modelValue','manage'])

const store = useModelConfigStore()
const loading = ref(false)
const list = ref([])
const innerValue = ref(props.modelValue)

watch(() => props.modelValue, v => innerValue.value = v)

const refresh = async () => {
  loading.value = true
  // 使用 fetchVisibleList 获取当前用户可见的模型列表
  await store.fetchVisibleList()
  list.value = store.modelList
  loading.value = false
  if (!innerValue.value && store.currentOrFirst) {
    innerValue.value = store.currentOrFirst
    emit('update:modelValue', innerValue.value)
    store.setCurrent(innerValue.value)
  }
}

const onChange = (val) => {
  emit('update:modelValue', val)
  store.setCurrent(val)
}

onMounted(refresh)
</script>

<style scoped>
.model-selector { 
	display: flex; 
	align-items: center; 
	width: 100%;
}

.selector-inner {
	flex: 1;
	min-width: 0; /* 允许在父级 flex 下收缩，不把整行撑爆 */
}
</style>
