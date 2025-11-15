<template>
  <div class="p-4 space-y-3 h-full flex flex-col">
    <div class="flex items-center justify-between">
      <div>
        <div class="text-lg font-semibold">{{ title }}</div>
        <div class="text-sm text-muted-foreground">生成时间：{{ createTime }}</div>
      </div>
      <div class="space-x-2">
        <button class="px-3 py-1 border rounded text-sm" @click="exportWord">导出 Word</button>
        <button class="px-3 py-1 border rounded text-sm" @click="exportMarkdown">导出 Markdown</button>
      </div>
    </div>
    <div class="flex-1 min-h-0">
      <RichTextEditor ref="editorRef" :templateTitle="title" :initialHtml="htmlCache" />
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
const htmlCache = ref('');

onMounted(async () => {
  const id = route.query.id;
  if (!id) return;
  const res = await getSolution({ solution_id: String(id) });
  if (res.code === 200 && res.data) {
    title.value = res.data.solution_title || '历史文章';
    createTime.value = res.data.create_date || '';
    // 将 markdown 渲染到编辑器
    const html = res.data.solution_content || '';
    htmlCache.value = html;
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
  const converted = await asBlob(htmlCache.value || document.querySelector('.ai-editor')?.innerHTML || '', {orientation: 'portrait'});
  saveAs(converted, `${title.value || '解决方案'}.docx`);
};

// 运行时按需从 CDN 加载 Turndown（HTML -> Markdown）
async function ensureTurndown() {
  if (window.TurndownService) return window.TurndownService;
  const url = 'https://cdn.jsdelivr.net/npm/turndown/dist/turndown.js';
  await new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = url;
    s.async = true;
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });
  return window.TurndownService;
}

const exportMarkdown = async () => {
  const html = htmlCache.value || document.querySelector('.ai-editor')?.innerHTML || '';
  const TurndownService = await ensureTurndown();
  const service = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced' });
  const md = service.turndown(html || '');
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
  saveAs(blob, `${title.value || '解决方案'}.md`);
};
</script>

<style scoped>
.text-muted-foreground{ color: #6b7280; }
</style>
