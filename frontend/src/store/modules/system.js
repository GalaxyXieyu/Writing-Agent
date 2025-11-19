import { defineStore } from 'pinia';
import { getPublicConfigs } from '@/service/api.public';

export const useSystemStore = defineStore('system', {
  state: () => ({
    configs: {},
  }),
  getters: {
    usageDocUrl: (state) => state.configs.usage_doc_url || '',
  },
  actions: {
    async fetchPublicConfigs() {
      try {
        const res = await getPublicConfigs();
        if (res.code === 200) {
          this.configs = res.data;
        }
      } catch (error) {
        console.error('Failed to fetch public configs:', error);
      }
    },
  },
});


