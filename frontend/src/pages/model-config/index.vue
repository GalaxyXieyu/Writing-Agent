<template>
  <div class="page">
    <Card>
      <CardHeader>
        <CardTitle>模型配置</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="toolbar flex flex-wrap gap-2">
          <Input v-model="q.name" placeholder="按名称搜索" class="w-full sm:w-[220px]" />
          <Button @click="refresh">查询</Button>
          <Button @click="openEdit()">新增</Button>
        </div>

        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="text-muted-foreground">加载中...</div>
        </div>

        <div v-else class="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[80px]">序号</TableHead>
              <TableHead>名称</TableHead>
              <TableHead>模型</TableHead>
              <TableHead>Base URL</TableHead>
              <TableHead class="w-[80px]">默认</TableHead>
              <TableHead class="w-[320px]">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="(row, idx) in list" :key="row.id">
              <TableCell>{{ (page - 1) * pageSize + idx + 1 }}</TableCell>
              <TableCell>{{ row.name }}</TableCell>
              <TableCell>{{ row.model }}</TableCell>
              <TableCell>{{ row.base_url }}</TableCell>
              <TableCell>
                <Badge v-if="row.is_default" variant="default">是</Badge>
                <span v-else class="text-muted-foreground">否</span>
              </TableCell>
              <TableCell>
                <div class="flex gap-2">
                  <Button variant="outline" size="sm" @click="verify(row)">验证</Button>
                  <Button variant="ghost" size="sm" @click="setDefault(row)">设为默认</Button>
                  <Button variant="ghost" size="sm" @click="openEdit(row)">编辑</Button>
                  <Button variant="ghost" size="sm" @click="remove(row)">删除</Button>
                </div>
              </TableCell>
            </TableRow>
            <TableRow v-if="list.length === 0">
              <TableCell colspan="6" class="text-center text-muted-foreground py-8">
                暂无数据
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        </div>

        <div class="flex items-center justify-between mt-4">
          <div class="text-sm text-muted-foreground">
            共 {{ total }} 条
          </div>
          <div class="flex items-center gap-2">
            <select
              v-model.number="pageSize"
              @change="refresh"
              class="h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
            >
              <option :value="10">10 条/页</option>
              <option :value="20">20 条/页</option>
              <option :value="50">50 条/页</option>
            </select>
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    :class="{ 'pointer-events-none opacity-50': page === 1 }"
                    @click="page > 1 && (page--, refresh())"
                  />
                </PaginationItem>
                <PaginationItem v-for="p in visiblePages" :key="p">
                  <PaginationLink
                    :is-active="p === page"
                    @click="p !== '...' && (page = p, refresh())"
                  >
                    {{ p }}
                  </PaginationLink>
                </PaginationItem>
                <PaginationItem>
                  <PaginationNext
                    :class="{ 'pointer-events-none opacity-50': page >= totalPages }"
                    @click="page < totalPages && (page++, refresh())"
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        </div>
      </CardContent>
    </Card>

    <Dialog v-model="visible" className="max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ form.id ? '编辑模型' : '新增模型' }}</DialogTitle>
      </DialogHeader>
      <div class="space-y-4 py-4">
        <div class="space-y-2">
          <Label for="name">名称</Label>
          <Input id="name" v-model="form.name" />
        </div>
        <div class="space-y-2">
          <Label for="model">模型</Label>
          <Input id="model" v-model="form.model" placeholder="如 gpt-4o" />
        </div>
        <div class="space-y-2">
          <Label for="base_url">Base URL</Label>
          <Input id="base_url" v-model="form.base_url" />
        </div>
        <div class="space-y-2">
          <Label for="api_key">API Key</Label>
          <Input id="api_key" v-model="form.api_key" type="password" />
        </div>
        <div class="space-y-2">
          <Label for="temperature">Temperature</Label>
          <Input id="temperature" v-model.number="form.temperature" type="number" />
        </div>
        <div class="space-y-2">
          <Label for="max_tokens">Max Tokens</Label>
          <Input id="max_tokens" v-model.number="form.max_tokens" type="number" />
        </div>
        <div class="flex items-center gap-2">
          <Label for="is_default">设为默认</Label>
          <Switch id="is_default" v-model="form.is_default" />
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="visible = false">取消</Button>
        <Button @click="submit">保存</Button>
      </DialogFooter>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useModelConfigStore } from '@/store/modules/modelConfig'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Table from '@/components/ui/Table.vue'
import TableHeader from '@/components/ui/TableHeader.vue'
import TableBody from '@/components/ui/TableBody.vue'
import TableRow from '@/components/ui/TableRow.vue'
import TableHead from '@/components/ui/TableHead.vue'
import TableCell from '@/components/ui/TableCell.vue'
import Badge from '@/components/ui/Badge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Label from '@/components/ui/Label.vue'
import Switch from '@/components/ui/Switch.vue'
import Pagination from '@/components/ui/Pagination.vue'
import PaginationContent from '@/components/ui/PaginationContent.vue'
import PaginationItem from '@/components/ui/PaginationItem.vue'
import PaginationLink from '@/components/ui/PaginationLink.vue'
import PaginationPrevious from '@/components/ui/PaginationPrevious.vue'
import PaginationNext from '@/components/ui/PaginationNext.vue'

const store = useModelConfigStore()
const q = ref({ name: '' })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const list = ref([])
const loading = ref(false)

const visible = ref(false)
const form = ref({ id: null, name: '', model: '', base_url: '', api_key: '', temperature: 0.2, max_tokens: null, is_default: false })

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = page.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 3; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  return pages
})

const refresh = async () => {
  loading.value = true
  try {
    await store.fetchList({ page: page.value, page_size: pageSize.value, name: q.value.name })
    list.value = store.modelList
    total.value = store.pagination.total
  } finally {
    loading.value = false
  }
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
  // 保存前做一次实时验证，失败仅提示，不阻断保存
  try {
    const verifyRes = await store.verifyModel(undefined, undefined, form.value)
    if (verifyRes?.code !== 200) {
      ElMessage.warning(verifyRes?.message || '验证失败，已仍然保存，可稍后在“验证”中重试')
    }
  } catch (_) { /* http 已提示，不阻断保存 */ }
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

const verify = async (row) => {
  try {
    const res = await store.verifyModel(row.id)
    if (res?.code === 200) {
      ElMessage.success('验证通过')
    } else {
      ElMessage.error(res?.message || '验证失败')
    }
  } catch (e) {
    // http 封装已弹出错误
  }
}

const remove = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该模型？', '提示')
    await store.deleteModel(row.id)
    ElMessage.success('删除成功')
    await refresh()
  } catch {
    // 用户取消
  }
}

refresh()
</script>

<style scoped>
.page { padding: 16px; }

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  align-items: center;
}
</style>
