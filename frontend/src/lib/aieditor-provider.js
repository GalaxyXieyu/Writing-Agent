
// 基于环境变量的直连配置（兜底回退用，严格贴合 AiEditor 官方结构）
function buildEnvAiConfig() {
  const env = import.meta.env
  const providerType = String(env.VITE_AI_PROVIDER_TYPE || 'openai').trim().toLowerCase()
  // 通用
  const baseURL = String(env.VITE_AI_BASE_URL || '').trim()
  const apiKey = String(env.VITE_AI_API_KEY || '').trim()
  const modelStr = String(env.VITE_AI_MODEL || '').trim()

  // Spark/Wenxin 可能的变量（若用户需要可在 .env 填写）
  const sparkAppId = String(env.VITE_SPARK_APP_ID || '').trim()
  const sparkApiKey = String(env.VITE_SPARK_API_KEY || '').trim()
  const sparkApiSecret = String(env.VITE_SPARK_API_SECRET || '').trim()
  const sparkVersion = String(env.VITE_SPARK_VERSION || 'v3.5').trim()
  const sparkProtocol = String(env.VITE_SPARK_PROTOCOL || '').trim() // ws/wss，可留空使用默认

  // 选择不同 Provider 的映射（与官方文档一致）
  if (providerType === 'openai') {
    // openai: 需要 apiKey 与 model；可选 endpoint
    if (!apiKey || !modelStr) return null
    const model = modelStr.split(',').map(s => s.trim()).filter(Boolean)[0]
    const cfg = {
      models: {
        openai: {
          apiKey,
          model,
        },
      },
      bubblePanelModel: 'openai',
      commandPanelModel: 'openai',
    }
    if (baseURL) {
      // 若提供自定义 OpenAI 兼容网关，根据文档用 endpoint（AiEditor 自动补 /v1/chat/completions）
      // 为避免出现 /v1/v1/chat/completions，剥离尾部 /vN 及 /vN/chat/completions
      let base = baseURL.replace(/\/$/, '')
      base = base.replace(/\/v\d+(\/chat\/completions)?$/, '')
      cfg.models.openai.endpoint = base
    }
    return cfg
  }

  if (providerType === 'gitee') {
    // gitee: 使用 endpoint + apiKey；model 可选
    if (!baseURL || !apiKey) return null
    // 计算最终 endpoint：允许用户既传完整 /chat/completions，也传网关根
    const base = baseURL.replace(/\/$/, '')
    const lower = base.toLowerCase()
    let endpoint = base
    const endsWithChat = /\/chat\/completions\/?$/.test(lower)
    const endsWithV1Chat = /\/v1\/chat\/completions\/?$/.test(lower)
    const hasV1 = /\/(v\d+)(\/|$)/.test(lower)
    const isBigModel = lower.includes('open.bigmodel.cn') || /\/paas\/(v\d+)/.test(lower)
    if (endsWithChat || endsWithV1Chat) {
      endpoint = base
    } else if (hasV1 || isBigModel) {
      endpoint = `${base}/chat/completions`
    } else {
      endpoint = `${base}/v1/chat/completions`
    }
    const model = modelStr.split(',').map(s => s.trim()).filter(Boolean)[0]
    return {
      models: {
        gitee: {
          endpoint,
          apiKey,
          ...(model ? { model } : {}),
        },
      },
      bubblePanelModel: 'gitee',
      commandPanelModel: 'gitee',
    }
  }

  if (providerType === 'spark') {
    // 星火：必须 appId，通常还需 apiKey/apiSecret
    if (!sparkAppId) return null
    return {
      models: {
        spark: {
          appId: sparkAppId,
          ...(sparkApiKey ? { apiKey: sparkApiKey } : {}),
          ...(sparkApiSecret ? { apiSecret: sparkApiSecret } : {}),
          ...(sparkVersion ? { version: sparkVersion } : {}),
          ...(sparkProtocol ? { protocol: sparkProtocol } : {}),
        },
      },
      bubblePanelModel: 'spark',
      commandPanelModel: 'spark',
    }
  }

  if (providerType === 'wenxin') {
    const accessToken = String(env.VITE_WENXIN_ACCESS_TOKEN || '').trim()
    if (!accessToken) return null
    const wenxinProtocol = String(env.VITE_WENXIN_PROTOCOL || '').trim()
    const wenxinVersion = String(env.VITE_WENXIN_VERSION || '').trim()
    return {
      models: {
        wenxin: {
          access_token: accessToken,
          ...(wenxinProtocol ? { protocol: wenxinProtocol } : {}),
          ...(wenxinVersion ? { version: wenxinVersion } : {}),
        },
      },
      bubblePanelModel: 'wenxin',
      commandPanelModel: 'wenxin',
    }
  }

  return null
}

// 从后端拉取 AiEditor 配置，优先使用服务端代理，避免浏览器直连外网 LLM
async function fetchServerAiConfig() {
  // 附带可选的 Authorization（若用户已登录）
  const headers = {}
  try {
    const raw = localStorage.getItem('userStore')
    const data = raw ? JSON.parse(raw) : {}
    const t = data?.token
    if (t) headers['Authorization'] = `Bearer ${t}`
  } catch {}

  const res = await fetch('/api/aieditor/model-config/aieditor', { headers })
  if (!res.ok) throw new Error(`fetch /api/model-config/aieditor failed: ${res.status}`)
  const json = await res.json()
  if (!json || json.code !== 200 || !json.data) throw new Error('invalid aieditor config payload')
  const { providers, models, defaults } = json.data || {}
  if (!providers || !models) throw new Error('missing providers/models in server config')

  // 将后端的 providers+models 结构，转换为 AiEditor 官方文档期望的结构：
  // ai = { models: { openai|gitee|spark|wenxin: {...} }, bubblePanelModel, commandPanelModel }
  const defaultModelKey = (defaults && (defaults.bubblePanelModel || defaults.commandPanelModel))
    || Object.keys(models)[0]
  if (!defaultModelKey) throw new Error('missing default model from server config')
  const defaultModel = models[defaultModelKey]
  const providerName = defaultModel?.provider
  const provider = providerName ? providers[providerName] : null
  if (!provider) throw new Error('missing provider for default model')

  const type = String(provider.type || 'openai').toLowerCase()
  const baseURL = String(provider.baseURL || '').replace(/\/$/, '')
  const apiKey = provider.apiKey || ''

  let mapped
  if (type === 'openai') {
    // 通过服务端代理：endpoint 指向我们的后端，AiEditor 自动拼接 /v1/chat/completions
    const includeKey = apiKey && apiKey !== 'use-header'
    mapped = {
      models: {
        openai: {
          model: defaultModelKey,
          // 剥离尾部 /vN 及 /vN/chat/completions，避免 /v1/v1 重复
          ...(baseURL ? { endpoint: baseURL.replace(/\/v\d+(\/chat\/completions)?$/, '') } : {}),
          ...(includeKey ? { apiKey } : {}),
        },
      },
      bubblePanelModel: 'openai',
      commandPanelModel: 'openai',
    }
  } else if (type === 'gitee') {
    // gitee: 直接使用完整 endpoint
    const endpoint = /\/chat\/completions\/?$/.test(baseURL) ? baseURL : `${baseURL}/chat/completions`
    mapped = {
      models: {
        gitee: {
          endpoint,
          ...(apiKey ? { apiKey } : {}),
          model: defaultModelKey,
        },
      },
      bubblePanelModel: 'gitee',
      commandPanelModel: 'gitee',
    }
  } else if (type === 'spark') {
    mapped = {
      models: { spark: provider },
      bubblePanelModel: 'spark',
      commandPanelModel: 'spark',
    }
  } else if (type === 'wenxin') {
    mapped = {
      models: { wenxin: provider },
      bubblePanelModel: 'wenxin',
      commandPanelModel: 'wenxin',
    }
  } else if (type === 'custom') {
    // 若后端提供 custom 结构，直接透传
    mapped = {
      models: { custom: provider },
      bubblePanelModel: 'custom',
      commandPanelModel: 'custom',
    }
  } else {
    // 未知类型时，尝试按 openai 处理
    mapped = {
      models: {
        openai: {
          model: defaultModelKey,
          ...(baseURL ? { endpoint: baseURL } : {}),
          ...(apiKey ? { apiKey } : {}),
        },
      },
      bubblePanelModel: 'openai',
      commandPanelModel: 'openai',
    }
  }

  return mapped
}

export async function getAiEditorConfig() {
  // 1) 优先使用后端配置（走代理 /api/aieditor，安全且稳定）
  try {
    const serverAi = await fetchServerAiConfig()
    try { window.__AIEDITOR_CFG__ = { models: Object.keys(serverAi?.models || {}) } } catch {}
    return { ai: serverAi }
  } catch (e) {
    try { console.warn('[aieditor] 后端配置获取失败，将回退到环境变量直连方案：', e) } catch {}
  }

  // 2) 回退到环境变量（仅调试/兜底，不建议生产使用）
  const envAi = buildEnvAiConfig()
  if (!envAi) return { ai: false }
  try { window.__AIEDITOR_CFG__ = { models: Object.keys(envAi.models || {}) } } catch {}
  return { ai: envAi }
}
