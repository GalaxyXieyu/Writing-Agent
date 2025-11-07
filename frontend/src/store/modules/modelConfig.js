import { defineStore } from 'pinia'
import { modelConfigApi } from '@/service/api.modelConfig'

export const useModelConfigStore = defineStore('modelConfig', {
  state: () => ({
    modelList: [],
    currentModelId: null,
    defaultModel: null,
    loading: false,
    pagination: { page: 1, pageSize: 20, total: 0 },
  }),
  actions: {
    async fetchList(params = {}) {
      this.loading = true
      try {
        const { data } = await modelConfigApi.getList({ page: this.pagination.page, page_size: this.pagination.pageSize, ...params })
        this.modelList = data.data.list
        this.pagination.total = data.data.total
      } finally {
        this.loading = false
      }
    },
    async createModel(payload) {
      await modelConfigApi.create(payload)
      await this.fetchList()
    },
    async updateModel(id, payload) {
      await modelConfigApi.update(id, payload)
      await this.fetchList()
    },
    async deleteModel(id) {
      await modelConfigApi.delete(id)
      await this.fetchList()
    },
    async setDefault(id) {
      await modelConfigApi.setDefault(id)
      await this.fetchList()
    },
    setCurrent(id) {
      this.currentModelId = id
    },
    async fetchDefault(userId) {
      const { data } = await modelConfigApi.getDefault(userId)
      this.defaultModel = data.data
    },
  },
  getters: {
    currentOrFirst(state) {
      if (state.currentModelId) return state.currentModelId
      if (state.defaultModel) return state.defaultModel.id
      return state.modelList?.[0]?.id || null
    }
  },
  persist: {
    key: 'model-config-store',
    paths: ['currentModelId']
  }
})
