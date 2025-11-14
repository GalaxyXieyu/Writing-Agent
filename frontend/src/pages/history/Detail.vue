<template>
  <div class="p-4 space-y-3 h-full flex flex-col">
    <div class="flex items-center justify-between">
      <div>
        <div class="text-lg font-semibold">{{ title }}</div>
        <div class="text-sm text-muted-foreground">生成时间：{{ createTime }}</div>
      </div>
      <div class="space-x-2">
        <button class="px-3 py-1 border rounded text-sm" @click="exportWord">导出 Word</button>
        <button class="px-3 py-1 border rounded text-sm" @click="exportPdf">导出 PDF</button>
      </div>
    </div>
    <div class="flex-1 min-h-0">
      <RichTextEditor ref="editorRef" :templateTitle="title" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import RichTextEditor from '@/pages/web-solution-assistant/components/richTextEditor.vue';
import { getSolution } from '@/service/api.solution';
import { asBlob } from 'html-docx-js-typescript';
import { saveAs } from 'file-saver';

const route = useRoute();
const editorRef = ref(null);
const title = ref('');
const createTime = ref('');
let htmlCache = '';

onMounted(async () => {
  const id = route.query.id;
  if (!id) return;
  const res = await getSolution({ solution_id: String(id) });
  if (res.code === 200 && res.data) {
    title.value = res.data.solution_title || '历史文章';
    createTime.value = res.data.create_date || '';
    // 将 markdown 渲染到编辑器
    const html = res.data.solution_content || '';
    htmlCache = html;
    // 调用组件暴露的 setHtml 方法，确保完整内容写入
    requestAnimationFrame(() => {
      try {
        editorRef.value?.setHtml?.(html);
      } catch {}
    });
  } else {
    ElMessage.error(res.message || '加载失败');
  }
});

const exportWord = async () => {
  const converted = await asBlob(htmlCache || document.querySelector('.ai-editor')?.innerHTML || '', {orientation: 'portrait'});
  saveAs(converted, `${title.value || '解决方案'}.docx`);
};

const exportPdf = async () => {
  const el = document.querySelector('.ai-editor');
  if (!el) return;
  const mod = await import('html2pdf.js');
  const html2pdf = mod.default || mod;
  html2pdf().from(el).set({ filename: `${title.value || '解决方案'}.pdf` }).save();
};
</script>

<style scoped>
.text-muted-foreground{ color: #6b7280; }
</style>
