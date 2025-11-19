<template>
  <div class="page">
    <Card>
      <CardHeader>
        <CardTitle>提示词配置</CardTitle>
      </CardHeader>
      <CardContent>
        <div class="mb-4 flex justify-end">
          <Button @click="openAdd">新增提示词</Button>
        </div>
        <div v-if="loading" class="flex items-center justify-center py-8">
          <div class="text-muted-foreground">加载中...</div>
        </div>

        <div v-else class="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead class="w-[80px]">ID</TableHead>
              <TableHead>提示词类型</TableHead>
              <TableHead>状态</TableHead>
              <TableHead class="w-[280px]">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="row in list" :key="row.id">
              <TableCell>{{ row.id }}</TableCell>
              <TableCell>{{ getPromptTypeName(row.prompt_type) }}</TableCell>
              <TableCell>
                <Badge v-if="row.status_cd === 'Y'" variant="default">有效</Badge>
                <Badge v-else variant="secondary">无效</Badge>
              </TableCell>
              <TableCell>
                <div class="flex gap-2">
                  <Button variant="ghost" size="sm" @click="openEdit(row)">编辑</Button>
                  <Button variant="ghost" size="sm" @click="handleDelete(row)">删除</Button>
                </div>
              </TableCell>
            </TableRow>
            <TableRow v-if="list.length === 0">
              <TableCell colspan="4" class="text-center text-muted-foreground py-8">
                暂无数据
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog v-model="visible" className="max-w-4xl">
      <DialogHeader>
        <DialogTitle>{{ form.id ? '编辑提示词' : '新增提示词' }}</DialogTitle>
      </DialogHeader>
      <div class="space-y-4 py-4 max-h-[60vh] overflow-y-auto">
        <div class="space-y-2">
          <Label>提示词类型</Label>
          <select 
            v-if="!form.id" 
            v-model="form.prompt_type" 
            class="flex h-10 w-full rounded-lg border-2 border-gray-300 bg-white px-3 py-2 text-sm shadow-sm transition-[border-color] duration-150 hover:border-gray-400 focus-visible:outline-none focus-visible:border-brand focus-visible:ring-2 focus-visible:ring-brand/20 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-neutral-800 dark:border-neutral-600"
          >
            <option value="">请选择提示词类型</option>
            <option value="template_generate">生成大纲</option>
            <option value="paragraph_generate">生成文章</option>
            <option value="template_refresh">刷新模板</option>
          </select>
          <Input v-else :value="getPromptTypeName(form.prompt_type)" disabled />
        </div>
        <div class="space-y-2">
          <Label>提示词内容</Label>
          <Textarea 
            v-model="form.prompt_content" 
            :rows="14"
            class="font-mono text-xs leading-relaxed"
            placeholder="请输入提示词内容"
          />
          <div class="text-xs text-gray-500 leading-relaxed dark:text-gray-400">
            支持的变量：<code class="text-brand bg-brand/10 px-1 rounded">{titleName}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{writingRequirement}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{exampleOutput}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{complete_title}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{last_para_content}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{titleNames}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{requirements}</code>, <code class="text-brand bg-brand/10 px-1 rounded">{original_template}</code>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Label for="status_cd">状态</Label>
          <Switch id="status_cd" v-model="form.status_cd" :checked="form.status_cd === 'Y'" @update:checked="form.status_cd = $event ? 'Y' : 'N'" />
          <span class="text-sm font-medium" :class="form.status_cd === 'Y' ? 'text-green-600' : 'text-gray-400'">
            {{ form.status_cd === 'Y' ? '✓ 有效' : '✗ 无效' }}
          </span>
        </div>
      </div>
      <DialogFooter class="border-t border-gray-200 pt-4">
        <Button variant="outline" @click="visible = false">取消</Button>
        <Button @click="submit">保存</Button>
      </DialogFooter>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { promptConfigApi } from '@/service/api.promptConfig'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
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
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Switch from '@/components/ui/Switch.vue'

const list = ref([])
const loading = ref(false)
const visible = ref(false)
const form = ref({ id: null, prompt_type: '', prompt_content: '', status_cd: 'Y' })

const promptTypeMap = {
  'template_generate': '生成大纲',
  'paragraph_generate': '生成文章',
  'template_refresh': '刷新模板'
}

const getPromptTypeName = (type) => {
  return promptTypeMap[type] || type
}

const refresh = async () => {
  loading.value = true
  try {
    const res = await promptConfigApi.getList()
    // API 返回格式: { code: 200, type: "success", message: "查询成功", data: [...] }
    // http 函数已经返回了 response.data，所以 res 就是整个响应对象
    list.value = res?.data || []
    console.log('加载的提示词配置数据:', list.value)
  } catch (e) {
    console.error('加载失败:', e)
    ElMessage.error('加载失败: ' + (e.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const openAdd = () => {
  form.value = {
    id: null,
    prompt_type: '',
    prompt_content: '',
    status_cd: 'Y'
  }
  visible.value = true
}

const openEdit = (row) => {
  form.value = {
    id: row.id,
    prompt_type: row.prompt_type,
    prompt_content: row.prompt_content,
    status_cd: row.status_cd
  }
  visible.value = true
}

const submit = async () => {
  if (!form.value.prompt_type) {
    ElMessage.error('请选择提示词类型')
    return
  }
  if (!form.value.prompt_content) {
    ElMessage.error('请输入提示词内容')
    return
  }
  try {
    if (form.value.id) {
      // 编辑
      await promptConfigApi.updateByType(form.value.prompt_type, {
        prompt_content: form.value.prompt_content,
        status_cd: form.value.status_cd
      })
      ElMessage.success('保存成功')
    } else {
      // 新增
      await promptConfigApi.create({
        prompt_type: form.value.prompt_type,
        prompt_content: form.value.prompt_content,
        status_cd: form.value.status_cd
      })
      ElMessage.success('创建成功')
    }
    visible.value = false
    await refresh()
  } catch (e) {
    console.error('保存失败:', e)
    ElMessage.error('保存失败: ' + (e.message || '未知错误'))
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除提示词配置 "${getPromptTypeName(row.prompt_type)}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await promptConfigApi.delete(row.id)
    ElMessage.success('删除成功')
    await refresh()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败: ' + (e.message || '未知错误'))
    }
  }
}

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.page { padding: 16px; }
</style>

