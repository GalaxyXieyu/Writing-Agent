<template>
  <Dialog v-model="innerVisible" className="max-w-2xl">
    <DialogHeader>
      <DialogTitle>生成自定义模板</DialogTitle>
    </DialogHeader>

    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-2 rounded-lg bg-muted p-1 text-sm">
        <button :class="tab==='fast' ? act : inact" @click="tab='fast'">快速生成</button>
        <button :class="tab==='upload' ? act : inact" @click="tab='upload'">上传模板文件</button>
      </div>

      <div v-if="tab==='fast'" class="space-y-3">
        <div>
          <Label class="text-sm">模型选择</Label>
          <div class="mt-1">
            <ModelSelector v-model="modelIdRef" @manage="$emit('manageModel')" />
          </div>
        </div>
        <div>
          <Label class="text-sm">文章标题</Label>
          <Input v-model="fast.title" placeholder="请输入文章标题" class="mt-1" />
        </div>
        <div>
          <Label class="text-sm">模板要求</Label>
          <Textarea v-model="fast.need" placeholder="请输入模板要求" class="mt-1" />
        </div>
        <div v-if="isRunning" class="rounded-md border p-3 text-sm text-muted-foreground">
          正在生成模板，请稍候...
        </div>
      </div>

      <div v-else class="space-y-3">
        <div class="rounded-md border border-dashed p-6 text-center">
          <input type="file" ref="fileInput" class="hidden" @change="onPickFile" accept=".pdf,.docx,.txt,.md" />
          <p class="text-sm text-muted-foreground">将文档拖拽到此，或</p>
          <Button class="mt-2" @click="fileInput?.click()">选择文件</Button>
        </div>
        <div v-if="uploading" class="space-y-2">
          <Label class="text-sm">上传进度</Label>
          <Progress :value="uploadPercent" :showLabel="true" />
        </div>
        <div v-if="parseStatus==='0'" class="rounded-md border p-3 text-sm text-muted-foreground">
          文档已上传，解析中...
          <Progress :value="100" class="mt-2 animate-pulse" />
        </div>
      </div>

      <div v-if="result" class="rounded-lg border p-3 bg-accent/30">
        <p class="text-sm font-medium mb-2">模板生成完成</p>
        <div class="flex gap-2">
          <Button size="sm" @click="applyResult">立即使用</Button>
          <Button size="sm" variant="outline" @click="$emit('openLibrary', result)">在模板库查看</Button>
          <Button size="sm" variant="outline" @click="copyOutline">复制大纲</Button>
        </div>
      </div>
    </div>

    <DialogFooter>
      <Button variant="outline" @click="close">关闭</Button>
      <Button v-if="tab==='fast'" :disabled="!canSubmitFast || isRunning" @click="submitFast">开始生成</Button>
    </DialogFooter>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Label from '@/components/ui/Label.vue'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Button from '@/components/ui/Button.vue'
import Progress from '@/components/ui/Progress.vue'
import ModelSelector from '@/components/ModelSelector.vue'
import { useUserStore } from '@/store'
import { uploadBusiFile } from '@/service/api.solution'
import { useFileParseTask } from '@/composables/useFileParseTask'
import { useTemplateCreateTask } from '@/composables/useTemplateCreateTask'

const props = defineProps<{ visible: boolean, modelId?: any }>()
const emit = defineEmits(['update:visible','applied','openLibrary','manageModel'])

const innerVisible = computed({
  get: () => props.visible,
  set: (v: boolean) => emit('update:visible', v)
})

const tab = ref<'fast'|'upload'>('fast')
const act = 'px-3 py-1 rounded bg-background text-foreground shadow'
const inact = 'px-3 py-1 rounded text-muted-foreground hover:text-foreground'

// 模型
const modelIdRef = ref<any>(props.modelId)
watch(() => props.modelId, (v)=>{ if(v) modelIdRef.value = v })

// 快速生成
const fast = ref({ title: '', need: '', name: '' })
const createTask = useTemplateCreateTask()
const userStore = useUserStore()
const canSubmitFast = computed(() => !!fast.value.title && !!modelIdRef.value)
// 只有用户点击“开始生成”后才显示生成中提示
const started = ref(false)
const isRunning = computed(() => started.value && createTask.running.value)

async function submitFast() {
  const params = {
    titleName: fast.value.title,
    writingRequirement: fast.value.need,
    userId: userStore.profile.mobile,
    modelId: modelIdRef.value
  }
  // 若后端要求 createTemplateEntryTable 需要模板名，这里使用“标题”或默认名兜底
  ;(params as any).templateName = fast.value.name || fast.value.title || 'AI生成模板'
  started.value = true
  const data = await createTask.start(params)
  if (data) {
    // 接口返回结构为 { titleName, writingRequirement, children }
    result.value = data
  }
}

// 上传 & 解析进度
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadPercent = ref(0)
const parseStatus = ref<'0'|'1'|'2'|'unknown'>('unknown')
const parseTask = useFileParseTask(userStore.profile.mobile)

async function onPickFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const form = new FormData()
  form.append('file', file)
  form.append('createNo', userStore.profile.mobile)
  form.append('createName', userStore.profile.name)
  uploading.value = true
  uploadPercent.value = 0
  try {
    const res = await uploadBusiFile(form)
    uploadPercent.value = 100
    uploading.value = false
    const fileId = res?.data?.data?.file_id
    if (fileId) {
      parseStatus.value = '0'
      parseTask.watch(fileId)
    }
  } catch (e) {
    uploading.value = false
  }
}

// 结果与操作
const result = ref<any | null>(null)
// 监听任务结果与文件解析结果
watch(() => createTask.data.value, (v) => { if (v) result.value = v })
watch(() => parseTask.result.value, (v) => { if (v) { result.value = v; parseStatus.value = '1' } })

// 保留结果区，由用户点击“立即使用”后再进入编辑并保存

function applyResult() {
  if (!result.value) return
  emit('applied', {
    titleName: result.value.titleName,
    writingRequirement: result.value.writingRequirement,
    children: result.value.children || []
  })
  innerVisible.value = false
}

async function copyOutline() {
  if (!result.value) return
  const text = JSON.stringify(result.value, null, 2)
  await navigator.clipboard.writeText(text)
}

function close() { innerVisible.value = false }

// 弹窗打开时重置所有本地状态，避免显示历史的“正在生成中”提示
function resetState() {
  tab.value = 'fast'
  fast.value = { title: '', need: '' }
  result.value = null
  uploading.value = false
  uploadPercent.value = 0
  parseStatus.value = 'unknown'
  // 重置任务状态与错误
  createTask.error.value = null
  createTask.data.value = null
  createTask.running.value = false
  started.value = false
  // 停止可能的历史轮询
  parseTask.stop()
}

watch(innerVisible, (v) => {
  if (v) resetState()
  else parseTask.stop()
})

</script>

<style scoped>
.bg-muted { @apply bg-gray-100 dark:bg-gray-800; }
.bg-accent\/30 { @apply bg-indigo-50/50 dark:bg-indigo-900/20; }
</style>
