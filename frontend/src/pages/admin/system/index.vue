<template>
  <div class="p-4 sm:p-6">
    <h2 class="text-xl font-semibold mb-4">系统设置</h2>
    <div class="max-w-2xl space-y-6">
      <div v-for="config in configs" :key="config.config_key" class="space-y-2">
        <Label :for="config.config_key" class="text-sm font-medium">{{ config.remark }}</Label>
        <Input
          :id="config.config_key"
          v-model="config.config_value"
          :placeholder="`请输入 ${config.remark}`"
        />
      </div>
      <div>
        <Button @click="handleSave" :disabled="isSaving">
          {{ isSaving ? '保存中...' : '保存设置' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { adminGetSystemConfigs, adminUpdateSystemConfigs } from '@/service/api.admin.js';
import { ElMessage } from 'element-plus';
import Input from '@/components/ui/Input.vue';
import Label from '@/components/ui/Label.vue';
import Button from '@/components/ui/Button.vue';

const configs = ref([]);
const isSaving = ref(false);

const fetchConfigs = async () => {
  try {
    const res = await adminGetSystemConfigs();
    if (res.code === 200) {
      configs.value = res.data;
    } else {
      ElMessage.error(res.message || '获取配置失败');
    }
  } catch (error) {
    ElMessage.error('获取配置失败');
  }
};

const handleSave = async () => {
  isSaving.value = true;
  try {
    const payload = configs.value.map(c => ({
      config_key: c.config_key,
      config_value: c.config_value,
    }));
    const res = await adminUpdateSystemConfigs(payload);
    if (res.code === 200) {
      ElMessage.success('保存成功');
      fetchConfigs(); // Refresh data
    } else {
      ElMessage.error(res.message || '保存失败');
    }
  } catch (error) {
    ElMessage.error('保存失败');
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  fetchConfigs();
});
</script>


