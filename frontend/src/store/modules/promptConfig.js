import { defineStore } from 'pinia'
import { promptConfigApi } from '@/service/api.promptConfig'

export const usePromptConfigStore = defineStore('promptConfig', {
  state: () => ({
    promptList: [],
    loading: false,
  }),
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const { data } = await promptConfigApi.getList()
        this.promptList = data || []
      } finally {
        this.loading = false
      }
    },
    async getByType(promptType) {
      const { data } = await promptConfigApi.getByType(promptType)
      return data
    },
    async update(id, payload) {
      await promptConfigApi.update(id, payload)
      await this.fetchList()
    },
    async updateByType(promptType, payload) {
      await promptConfigApi.updateByType(promptType, payload)
      await this.fetchList()
    },
  },
})

