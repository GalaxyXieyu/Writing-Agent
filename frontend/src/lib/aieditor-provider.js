import { httpAuth, getToken } from '@/service/request'

export async function getAiEditorConfig() {
  // 从后端拉取供 AiEditor 使用的 provider + models + defaults
  const res = await httpAuth({ method: 'GET', url: '/api/aieditor/model-config/aieditor' })
  // 注意：后端返回形如 { code, type, message, data }，真实数据在 data.data
  const data = res?.data?.data || {}
  try { console.debug('[aieditor] config resp data:', data) } catch {}
  // providers：优先使用后端对象字典；否则兜底为写死 provider
  const providers = (data.providers && typeof data.providers === 'object')
    ? data.providers
    : { 'writing-agent': { type: 'openai', baseURL: '/api/aieditor', apiKey: 'use-header' } }
  // 后端返回字典：key 为真实模型名
  const modelsDict = (data.models && typeof data.models === 'object') ? data.models : {}
  let modelNames = Object.keys(modelsDict)
  const firstModelName = modelNames[0] || null
  let bubble = data?.defaults?.bubblePanelModel || firstModelName
  let command = data?.defaults?.commandPanelModel || firstModelName
  const token = getToken()
  // 同时提供两种结构：数组 + 映射，兼容不同版本 AiEditor
  const modelProviders = {}
  modelNames.forEach(n => { modelProviders[n] = 'writing-agent' })
  // 临时强制：若包含 'glm-4-flashx'，将其设为唯一模型以先跑通
  if (modelNames.includes('glm-4-flashx')) {
    modelNames = ['glm-4-flashx']
    modelProviders['glm-4-flashx'] = 'writing-agent'
    bubble = 'glm-4-flashx'
    command = 'glm-4-flashx'
  }

  const ai = {
    providers,
    models: modelNames, // 数组形式，形如 ['glm-4-flashx','gpt-4o']
    modelProviders,     // 名称到 provider 的映射
    bubblePanelModel: bubble,
    commandPanelModel: command,
    // 兼容一些版本可能读取的默认字段
    defaultModel: bubble,
    model: bubble,
    // 兼容不同版本：提供函数式与静态请求头
    requestHeaders: () => (token ? { Authorization: `Bearer ${token}` } : {}),
    requestOptions: {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    }
  }
  // 便于调试：
  try { window.__AIEDITOR_CFG__ = { providers, models: modelsDict, ai } } catch {}
  try { console.log('[aieditor] ai options:', ai) } catch {}
  return { ai }
}
