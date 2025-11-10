import { ref } from 'vue'
import { templateCreate } from '@/service/api.solution'

// 管理“快速生成模板”的任务状态（简化版，未来可接入 /api/tasks）
export function useTemplateCreateTask() {
  const running = ref(false)
  const error = ref<string | null>(null)
  const data = ref<any>(null)

  async function start(params: any) {
    if (running.value) return
    running.value = true
    error.value = null
    data.value = null
    try {
      // 按后端要求调用 createTemplateEntryTable（入表），模板名若未提供则用标题兜底
      const payload = {
        titleName: params.titleName,
        writingRequirement: params.writingRequirement,
        userId: params.userId,
        templateName: params.templateName || params.titleName || 'AI生成模板',
        modelId: params.modelId,
      }
      // 如果提供了示例输出，添加到 payload
      if (params.exampleOutput) {
        (payload as any).exampleOutput = params.exampleOutput
      }
      const res = await templateCreate(payload)
      // 后端统一返回 TemplateContentResponse，主体在 data 字段
      data.value = (res as any)?.data?.data
      return data.value
    } catch (e: any) {
      error.value = e?.response?.data?.message || e?.message || '生成失败'
      throw e
    } finally {
      running.value = false
    }
  }

  return { running, error, data, start }
}
