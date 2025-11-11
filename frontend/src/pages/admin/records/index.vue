<template>
  <div class="space-y-4 p-4 min-h-0">
    <div class="flex items-center gap-2">
      <Input v-model="kw" placeholder="标题关键字" class="w-64" />
      <select v-model="type" class="border rounded px-2 py-1 text-sm">
        <option value="">全部类型</option>
        <option value="solution">文章方案</option>
        <option value="file">文件</option>
      </select>
      <Button @click="load">查询</Button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left border-b">
            <th class="py-2">类型</th>
            <th class="py-2">标题/文件名</th>
            <th class="py-2">成员手机号</th>
            <th class="py-2">成员姓名</th>
            <th class="py-2">时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in list" :key="r.type + '-' + r.id" class="border-b">
            <td class="py-2">{{ r.type }}</td>
            <td class="py-2">{{ r.title }}</td>
            <td class="py-2">{{ r.owner_phone }}</td>
            <td class="py-2">{{ r.owner_name }}</td>
            <td class="py-2">{{ r.created_at }}</td>
          </tr>
        </tbody>
      </table>
      <div class="text-sm text-muted-foreground mt-2">共 {{ total }} 条</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Input from '@/components/ui/Input.vue';
import Button from '@/components/ui/Button.vue';
import { useUserStore } from '@/store';
import { adminListRecords } from '@/service/api.admin';

const userStore = useUserStore();
const kw = ref('');
const type = ref('');
const list = ref([]);
const total = ref(0);

const load = async () => {
  const res = await adminListRecords({ kw: kw.value, type: type.value });
  if (res.code === 200) {
    list.value = res.data?.list || [];
    total.value = res.data?.total || 0;
  }
};

onMounted(load);
</script>

<style scoped>
</style>
