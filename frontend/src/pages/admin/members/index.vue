<template>
  <div class="space-y-4 p-4 min-h-0">
    <div class="flex items-center gap-2">
      <Input v-model="kw" placeholder="搜索成员：账号/姓名/手机号" class="w-80" />
      <Button @click="load">查询</Button>
      <div class="flex-1"></div>
      <Button @click="createInvite">生成邀请码</Button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left border-b">
            <th class="py-2">账号</th>
            <th class="py-2">姓名</th>
            <th class="py-2">手机号</th>
            <th class="py-2">状态</th>
            <th class="py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in list" :key="u.user_id" class="border-b">
            <td class="py-2">{{ u.username }}</td>
            <td class="py-2">{{ u.name }}</td>
            <td class="py-2">{{ u.phone }}</td>
            <td class="py-2">{{ u.status }}</td>
            <td class="py-2 space-x-2">
              <Button size="sm" @click="resetPwd(u)">重置密码</Button>
              <Button size="sm" variant="outline" @click="toggleStatus(u)">{{ u.status === 'Y' ? '停用' : '启用' }}</Button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="text-sm text-muted-foreground mt-2">共 {{ total }} 人</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';
import { useUserStore } from '@/store';
import { adminListUsers, adminCreateInvite, adminResetPassword, adminSetStatus } from '@/service/api.admin';

const userStore = useUserStore();
const kw = ref('');
const list = ref([]);
const total = ref(0);

const load = async () => {
  const res = await adminListUsers({ kw: kw.value });
  if (res.code === 200) {
    list.value = res.data?.list || [];
    total.value = res.data?.total || 0;
  }
};

const createInvite = async () => {
  const res = await adminCreateInvite({ expire_hours: 24 });
  if (res.code === 200) {
    const code = res.data?.invite_code;
    await ElMessageBox.alert(`邀请码：${code}\n24小时内有效`, '创建成功', { confirmButtonText: '复制' });
    navigator.clipboard?.writeText(code);
  }
};

const resetPwd = async (u) => {
  const { value } = await ElMessageBox.prompt('输入新密码', '重置密码', { inputType: 'password' });
  if (!value) return;
  const res = await adminResetPassword({ user_id: u.user_id, new_password: value });
  if (res.code === 200) ElMessage.success('已重置');
};

const toggleStatus = async (u) => {
  const next = u.status === 'Y' ? 'N' : 'Y';
  const res = await adminSetStatus({ user_id: u.user_id, status: next });
  if (res.code === 200) { ElMessage.success('已更新'); load(); }
};

onMounted(load);
</script>

<style scoped>
</style>
