<template>
  <div class="page">
    <div class="toolbar">
      <el-input v-model="q.name" placeholder="按名称搜索" style="width: 220px;"/>
      <el-button type="primary" @click="refresh">查询</el-button>
      <el-button @click="openEdit()">新增</el-button>
    </div>
    <el-table :data="list" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"/>
      <el-table-column prop="name" label="名称"/>
      <el-table-column prop="model" label="模型"/>
      <el-table-column prop="base_url" label="Base URL"/>
      <el-table-column prop="is_default" label="默认" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success">是</el-tag>
          <span v-else>否</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button link type="primary" @click="setDefault(row)">设为默认</el-button>
          <el-button link @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, sizes, prev, pager, next"
      :page-sizes="[10,20,50]"
      @current-change="refresh"
      @size-change="refresh"
    />

    <el-dialog v-model="visible" :title="form.id ? '编辑模型' : '新增模型'" width="520">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name"/></el-form-item>
        <el-form-item label="模型"><el-input v-model="form.model" placeholder="如 gpt-4o"/></el-form-item>
        <el-form-item label="Base URL"><el-input v-model="form.base_url"/></el-form-item>
        <el-form-item label="API Key"><el-input v-model="form.api_key"/></el-form-item>
        <el-form-item label="Temperature"><el-input v-model.number="form.temperature"/></el-form-item>
        <el-form-item label="Max Tokens"><el-input v-model.number="form.max_tokens"/></el-form-item>
        <el-form-item label="设为默认"><el-switch v-model="form.is_default"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
  
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useModelConfigStore } from '@/store/modules/modelConfig'

const store = useModelConfigStore()
const q = ref({ name: '' })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const list = ref([])
const loading = ref(false)

const visible = ref(false)
const form = ref({ id: null, name: '', model: '', base_url: '', api_key: '', temperature: 0.2, max_tokens: null, is_default: false })

const refresh = async () => {
  loading.value = true
  await store.fetchList({ page: page.value, page_size: pageSize.value, name: q.value.name })
  list.value = store.modelList
  total.value = store.pagination.total
  loading.value = false
}

const openEdit = (row) => {
  if (row) {
    form.value = { ...row }
  } else {
    form.value = { id: null, name: '', model: '', base_url: '', api_key: '', temperature: 0.2, max_tokens: null, is_default: false }
  }
  visible.value = true
}

const submit = async () => {
  if (!form.value.name || !form.value.model || !form.value.base_url || !form.value.api_key) {
    ElMessage.error('请填写完整信息')
    return
  }
  if (form.value.id) {
    await store.updateModel(form.value.id, form.value)
  } else {
    await store.createModel(form.value)
  }
  visible.value = false
  await refresh()
}

const setDefault = async (row) => {
  await store.setDefault(row.id)
  ElMessage.success('已设为默认')
  await refresh()
}

const remove = async (row) => {
  await ElMessageBox.confirm('确认删除该模型？','提示')
  await store.deleteModel(row.id)
  ElMessage.success('删除成功')
  await refresh()
}

refresh()
</script>

<style scoped>
.page { padding: 16px; }
.toolbar { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; }
</style>
