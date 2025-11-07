<template>
  <div class="model-selector">
    <el-select v-model="innerValue" placeholder="请选择模型" @change="onChange" :loading="loading" style="width: 260px;">
      <el-option v-for="m in list" :key="m.id" :label="`${m.name} (${m.model})`" :value="m.id"/>
    </el-select>
    <el-button type="primary" link @click="$emit('manage')" style="margin-left: 8px;">管理模型</el-button>
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
  await store.fetchList()
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
.model-selector { display: inline-flex; align-items: center; }
</style>
