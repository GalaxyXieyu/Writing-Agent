<template>
  <Dialog :open="open" @update:open="(val) => $emit('update:open', val)">
    <div class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- 遮罩 -->
      <div class="fixed inset-0 bg-black/40" @click="$emit('update:open', false)"></div>
      
      <!-- 对话框内容 -->
      <div class="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 p-6 z-10">
        <DialogHeader>
          <DialogTitle>修改密码</DialogTitle>
          <DialogDescription>请输入当前密码和新密码</DialogDescription>
        </DialogHeader>

        <form @submit.prevent="handleSubmit" class="mt-6 space-y-4">
          <div>
            <Label for="oldPassword">当前密码</Label>
            <Input
              id="oldPassword"
              type="password"
              v-model="formData.oldPassword"
              placeholder="请输入当前密码"
              class="mt-1.5"
              required
            />
          </div>

          <div>
            <Label for="newPassword">新密码</Label>
            <Input
              id="newPassword"
              type="password"
              v-model="formData.newPassword"
              placeholder="请输入新密码（至少6位）"
              class="mt-1.5"
              required
            />
          </div>

          <div>
            <Label for="confirmPassword">确认新密码</Label>
            <Input
              id="confirmPassword"
              type="password"
              v-model="formData.confirmPassword"
              placeholder="请再次输入新密码"
              class="mt-1.5"
              required
            />
          </div>

          <DialogFooter class="mt-6">
            <button
              type="button"
              @click="$emit('update:open', false)"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="ml-3 px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              {{ loading ? '提交中...' : '确认修改' }}
            </button>
          </DialogFooter>
        </form>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';
import { ElMessage } from 'element-plus';
import Dialog from '@/components/ui/Dialog.vue';
import DialogHeader from '@/components/ui/DialogHeader.vue';
import DialogTitle from '@/components/ui/DialogTitle.vue';
import DialogDescription from '@/components/ui/DialogDescription.vue';
import DialogFooter from '@/components/ui/DialogFooter.vue';
import Input from '@/components/ui/Input.vue';
import Label from '@/components/ui/Label.vue';
import { changePassword } from '@/service/api.user';

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:open', 'success']);

const loading = ref(false);
const formData = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// 重置表单
const resetForm = () => {
  formData.oldPassword = '';
  formData.newPassword = '';
  formData.confirmPassword = '';
};

// 监听对话框关闭，重置表单
watch(() => props.open, (val) => {
  if (!val) {
    resetForm();
  }
});

const handleSubmit = async () => {
  // 验证新密码长度
  if (formData.newPassword.length < 6) {
    ElMessage.error('新密码至少需要6位');
    return;
  }

  // 验证两次密码是否一致
  if (formData.newPassword !== formData.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致');
    return;
  }

  try {
    loading.value = true;
    await changePassword({
      old_password: formData.oldPassword,
      new_password: formData.newPassword,
    });
    ElMessage.success('密码修改成功');
    emit('update:open', false);
    emit('success');
  } catch (error) {
    ElMessage.error(error.message || '密码修改失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.bg-primary {
  background: linear-gradient(90deg, #a597f5 1%, #5571ff 98%);
}

.bg-primary\/90 {
  background: linear-gradient(90deg, #9489e0 1%, #4a62e6 98%);
}
</style>
