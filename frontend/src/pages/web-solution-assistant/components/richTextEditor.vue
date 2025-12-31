<template>
    <div class="editor-container h-full flex flex-col relative">
        <div class="flex-1 relative h-full w-full" ref="editorContainerRef" v-loading="loading" element-loading-text="生成中..."></div>
        
        <Dialog v-model="dialogVisible" :closeOnOverlay="true" className="w-[40vw] max-w-[760px] p-0" :style="dialogStyle">
          <DialogHeader class="px-4 py-3">
            <DialogTitle>AI 智能助手</DialogTitle>
          </DialogHeader>
          <div class="px-4 pb-3">
            <div ref="contentRef" class="dialog-content" v-html="aiContentHtml"></div>
            <div class="flex items-center gap-2 mt-3">
              <Input v-model="aiInputContent" placeholder="请输入优化建议" />
              <Button size="sm" @click="handleAiInputClick">发送</Button>
            </div>
          </div>
          <DialogFooter class="px-4 py-3 border-t">
            <div class="flex items-center justify-between w-full">
              <span v-show="isCreateText" class="text-sm text-muted-foreground">创作中...</span>
              <div class="flex gap-2">
                <Button variant="outline" @click="handleWritingClick">重新写作</Button>
                <Button variant="outline" @click="handleInsertClick">插入后方</Button>
                <Button @click="handleReplaceClick">替换所选</Button>
              </div>
            </div>
          </DialogFooter>
        </Dialog>
    </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount, watch, nextTick} from 'vue';
import {AiEditor} from "aieditor";
import "aieditor/dist/style.css";
import {marked} from 'marked';
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {ElMessage, ElMessageBox} from 'element-plus'
import {getKnowToWriteUrl, createArticleUrl} from '@/service/api.solution'
import { getAiEditorConfig } from '@/lib/aieditor-provider'
import {useModelConfigStore} from '@/store/modules/modelConfig'
import {asBlob} from 'html-docx-js-typescript';
import {saveAs} from 'file-saver';
import interact from 'interactjs'
import Dialog from '@/components/ui/Dialog.vue'
import DialogHeader from '@/components/ui/DialogHeader.vue'
import DialogTitle from '@/components/ui/DialogTitle.vue'
import DialogFooter from '@/components/ui/DialogFooter.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

const props = defineProps({
    // 页面标题，仅用于导出命名
    templateTitle: String,
    // 初始 HTML 内容（例如历史详情页回显）
    initialHtml: {
        type: String,
        default: ''
    }
});

const editorContainerRef = ref(null);
let aiEditor = null;
const content = ref('');
const selectedText = ref('');
const dialogVisible = ref(false);
const dialogStyle = ref('');
const aiInputContent = ref('');
const aiContent = ref('');
const aiContentHtml = ref('');
const isCreateText = ref(false);
const isPause = ref(false);
const isCreate = ref(false);
// 生成时自动跟随滚动到底部
const autoFollowScroll = ref(true);
const loading = ref(false);
let ctrl;
let isCooldown = false;
let lastType = 1;
// 流式渲染节流，避免高频刷新导致卡顿
let renderTimer = null;
let renderScheduled = false;
let fullMarkdown = '';
let lastScrollTop = 0;
let isUserScrolling = false;
let scrollTimeout = null;

const scheduleRender = (immediate = false) => {
    const doRender = () => {
        try {
            const htmlContent = marked(fullMarkdown);
            content.value = htmlContent;
            if (aiEditor) {
                // 记录当前滚动位置
                const scrollContainer = editorContainerRef.value?.querySelector('.aieditor-content') 
                    || editorContainerRef.value?.querySelector('.ProseMirror')
                    || editorContainerRef.value?.querySelector('.ai-editor');
                const prevScrollTop = scrollContainer?.scrollTop || 0;
                const prevScrollHeight = scrollContainer?.scrollHeight || 0;
                
                if (aiEditor.setHtml) {
                    aiEditor.setHtml(htmlContent);
                } else if (aiEditor.setContent) {
                    aiEditor.setContent(htmlContent);
                }
                
                // 流式输出时平滑滚动到底部（仅当用户没有手动滚动时）
                if (autoFollowScroll.value && !isUserScrolling && scrollContainer) {
                    requestAnimationFrame(() => {
                        try {
                            // 使用平滑滚动，避免闪烁
                            scrollContainer.scrollTo({
                                top: scrollContainer.scrollHeight,
                                behavior: 'auto' // 流式输出时用 auto 避免滞后
                            });
                        } catch {}
                    });
                }
            }
        } catch (e) {
            console.error('流式渲染失败:', e);
        } finally {
            renderScheduled = false;
            renderTimer = null;
        }
    };
    if (immediate) {
        if (renderTimer) { clearTimeout(renderTimer); renderTimer = null; }
        doRender();
    } else if (!renderScheduled) {
        renderScheduled = true;
        // 增加节流时间到 200ms，减少渲染频率
        renderTimer = setTimeout(doRender, 200);
    }
};

// 检测用户滚动行为
const handleUserScroll = () => {
    isUserScrolling = true;
    if (scrollTimeout) clearTimeout(scrollTimeout);
    // 用户停止滚动 2 秒后恢复自动跟随
    scrollTimeout = setTimeout(() => {
        isUserScrolling = false;
    }, 2000);
};

const emit = defineEmits(['requestComplete', 'requestError']);

// 动态获取 AiEditor 的 AI 配置；失败则关闭 ai
const getAiConfig = async () => {
    try {
        const cfg = await getAiEditorConfig()
        const ai = cfg?.ai
        if (!ai) return false
        const hasModels = Array.isArray(ai.models)
            ? ai.models.length > 0
            : (ai.models && typeof ai.models === 'object' && Object.keys(ai.models).length > 0)
        if (!hasModels) return false
        return ai
    } catch {
        return false
    }
}

onMounted(async () => {
    nextTick(async () => {
        if (editorContainerRef.value) {
            // 直接使用 aieditor-provider 返回的原生配置（符合官方文档）
            let aiConfig = await getAiConfig();
            const aiToInject = aiConfig || false;

            aiEditor = new AiEditor({
                element: editorContainerRef.value,
                placeholder: "点击输入内容...",
                content: '',
                onChange: (editor) => {
                    if (editor && editor.getHtml) {
                        content.value = editor.getHtml();
                    }
                },
                ai: aiToInject
            });
            try { console.log('[aieditor] editor inited with ai:', aiConfig !== false, aiConfig) } catch {}
            // 若传入了初始 HTML，编辑器准备好后立即写入
            try {
                if (props.initialHtml) {
                    if (aiEditor.setHtml) {
                        aiEditor.setHtml(props.initialHtml || '');
                    } else if (aiEditor.setContent) {
                        aiEditor.setContent(props.initialHtml || '');
                    }
                }
            } catch {}
            
            if (editorContainerRef.value) {
                const editorElement = editorContainerRef.value.querySelector('.ai-editor');
                if (editorElement) {
                    editorElement.addEventListener('mouseup', () => {
                        const selection = window.getSelection();
                        if (selection && selection.toString().trim()) {
                            selectedText.value = selection.toString();
                            const coords = getSelectionCoords();
                            if (coords) {
                                calculateDialogPosition(coords);
                            }
                        }
                    });
                    // 监听滚动，检测用户手动滚动行为
                    const scrollTarget = editorElement.querySelector('.aieditor-content') 
                        || editorElement.querySelector('.ProseMirror')
                        || editorElement;
                    if (scrollTarget) {
                        scrollTarget.addEventListener('scroll', handleUserScroll, { passive: true });
                    }
                }
            }
        }
    });

    // 去除基于 .el-dialog 的拖拽逻辑；如需拖拽可后续为 Dialog 增加 handle
});

const getSelectionCoords = () => {
    if (!editorContainerRef.value) return null;
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return null;
    
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    const containerRect = editorContainerRef.value.getBoundingClientRect();
    
    return {
        start: {
            x: rect.left - containerRect.left,
            y: rect.top - containerRect.top,
            height: rect.height
        },
        end: {
            x: rect.right - containerRect.left,
            y: rect.top - containerRect.top,
            height: rect.height
        },
        width: rect.width,
        height: rect.height
    };
};

const calculateDialogPosition = (coords) => {
    const viewportHeight = window.innerHeight;
    const dialogHeight = 250;
    const padding = 10;
    
    const spaceBelow = viewportHeight - (coords.end.y + coords.height);
    const spaceAbove = coords.start.y;
    
    if (spaceBelow >= dialogHeight + padding || spaceAbove >= dialogHeight + padding) {
        if (spaceBelow >= spaceAbove) {
            dialogStyle.value = {
                position: 'fixed',
                top: `${coords.start.y + coords.height + padding}px`,
                left: `50%`,
                margin: 0,
                height: spaceBelow >= dialogHeight + padding ? `${dialogHeight}px` : `${spaceBelow - padding}px`
            };
        } else {
            dialogStyle.value = {
                position: 'fixed',
                bottom: `${viewportHeight - coords.start.y + padding}px`,
                left: `50%`,
                margin: 0,
                height: spaceAbove >= dialogHeight + padding ? `${dialogHeight}px` : `${spaceAbove - padding}px`
            };
        }
    } else {
        dialogStyle.value = {
            position: 'fixed',
            top: '50%',
            left: '70%',
            margin: 0,
            transform: 'translate(-50%, -50%)',
            height: `${dialogHeight}px`
        };
    }
};

const handleClickOutside1 = (event) => {
    const dialog = document.getElementById('ai-dialog');
    if (dialog && !dialog.contains(event.target) && dialogVisible.value) {
        dialogVisible.value = false;
        aiInputContent.value = "";
        aiContent.value = "";
        document.removeEventListener('click', handleClickOutside1);
    }
};

const getArticleType = (type) => {
    switch (type) {
        case 1:
            aiInputContent.value = '';
            return '扩写';
        case 2:
            aiInputContent.value = '';
            return '润色';
        case 3:
            aiInputContent.value = '';
            return '续写';
        case 4:
            aiInputContent.value = '';
            return '转化风格';
        default:
            return '';
    }
};

const getKnowToWrite = (selectTxt, type) => {
    const ctrl = new AbortController();
    isCreateText.value = true;
    aiContentHtml.value = '';
    dialogVisible.value = true;
    document.addEventListener('click', handleClickOutside1, true);
    lastType = type;
    aiContent.value = '';
    const requestPayload = {
        "original_text": selectedText.value,
        "article_type": getArticleType(type),
        "user_requirements": aiInputContent.value,
        "model_id": useModelConfigStore().currentOrFirst
    };
    const chatPayload = {
        method: "POST",
        body: JSON.stringify(requestPayload),
        headers: {
            "Content-Type": "application/json",
        },
    };
    fetchEventSource(getKnowToWriteUrl, {
        openWhenHidden: true,
        ...chatPayload,
        signal: ctrl.signal,
        async onopen(res) {
            console.log('onopen', res);
        },
        onmessage(msg) {
            if (JSON.parse(msg.data).is_end === true) {
                isCreateText.value = false;
                return;
            }
            aiContent.value += JSON.parse(msg.data).data;
            aiContentHtml.value = marked(aiContent.value);
        },
        onclose() {
            console.log("生成结束,onclose");
            ElMessage({
                message: '创作完成.',
                type: 'success',
            });
        },
        onerror(e) {
            ctrl.abort();
            console.log("生成失败,onerror", e);
        },
    });
};

const handleWritingClick = () => {
    if (isCooldown) return;
    isCooldown = true;
    setTimeout(() => {
        isCooldown = false;
    }, 1500);
    getKnowToWrite(selectedText.value, lastType);
};

const handleInsertClick = () => {
    if (aiEditor && aiContent.value) {
        try {
            const currentContent = aiEditor.getHtml ? aiEditor.getHtml() : '';
            if (aiEditor.setHtml) {
                aiEditor.setHtml(currentContent + aiContent.value);
            } else if (aiEditor.setContent) {
                aiEditor.setContent(currentContent + aiContent.value);
            }
            dialogVisible.value = false;
            aiContent.value = '';
        } catch (e) {
            console.error('插入内容失败:', e);
        }
    }
};

const handleReplaceClick = () => {
    if (aiEditor && aiContent.value) {
        try {
            const selection = window.getSelection();
            if (selection && selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                range.deleteContents();
                const textNode = document.createTextNode(aiContent.value);
                range.insertNode(textNode);
                selection.removeAllRanges();
            } else {
                if (aiEditor.setHtml) {
                    aiEditor.setHtml(aiContent.value);
                } else if (aiEditor.setContent) {
                    aiEditor.setContent(aiContent.value);
                }
            }
            dialogVisible.value = false;
            aiContent.value = '';
        } catch (e) {
            console.error('替换内容失败:', e);
        }
    }
};

const handleAiInputClick = () => {
    if (isCooldown) return;
    isCooldown = true;
    setTimeout(() => {
        isCooldown = false;
    }, 1500);
    getKnowToWrite(selectedText.value, 5);
    aiContent.value = '';
};

const onClickByType = (type) => {
    getKnowToWrite(selectedText.value, type);
};

const createArticle = (templateTitleParam1) => {
    if (isPause.value && ctrl) {
        ctrl.abort();
    }
    if (isCreate.value) return;
    ctrl = new AbortController();
    isPause.value = false;
    if (aiEditor) {
        try {
            if (aiEditor.setHtml) {
                aiEditor.setHtml('');
            } else if (aiEditor.setContent) {
                aiEditor.setContent('');
            }
        } catch (e) {
            console.error('清空编辑器内容失败:', e);
        }
    }
    content.value = '';
    fullMarkdown = '';
    if (renderTimer) { clearTimeout(renderTimer); renderTimer = null; }
    renderScheduled = false;
    loading.value = true;
    isCreate.value = true;
    
    // 优先使用参数中的 modelId
    const modelId = templateTitleParam1.modelId || useModelConfigStore().currentOrFirst;
    
    const chatPayload = {
        method: 'POST',
        body: JSON.stringify({...templateTitleParam1, modelId}),
        headers: {
            'Content-Type': 'application/json',
        },
    };
    // 攒批渲染：将增量写入 fullMarkdown，由 scheduleRender 合并更新
    fetchEventSource(createArticleUrl, {
        openWhenHidden: true,
        signal: ctrl.signal,
        ...chatPayload,
        async onopen(res) {
            console.log('onopen', res);
        },
        onmessage(event) {
            if (isPause.value) {
                isCreate.value = false;
                ctrl.abort();
                return;
            }
            loading.value = false;
            const parsed = JSON.parse(event.data);
            if (parsed.is_end === true) {
                // 流结束，立即做一次最终渲染
                scheduleRender(true);
                return;
            }
            const eventData = parsed.data || '';
            fullMarkdown += eventData;
            scheduleRender(false);
        },
        onclose() {
            loading.value = false;
            isCreate.value = false;
            ElMessage({
                message: '创作完成.',
                type: 'success',
            });
            emit('requestComplete', { html: content.value, markdown: fullMarkdown });
        },
        onerror(err) {
            loading.value = false;
            isCreate.value = false;
            if (renderTimer) { clearTimeout(renderTimer); renderTimer = null; }
            renderScheduled = false;
            
            // 友好的错误提示
            let errorMsg = '生成失败，请重试';
            const errStr = String(err);
            if (errStr.includes('504') || errStr.includes('Gateway Timeout')) {
                errorMsg = 'AI服务响应超时，请稍后重试或选择其他模型';
            } else if (errStr.includes('502') || errStr.includes('Bad Gateway')) {
                errorMsg = 'AI服务暂时不可用，请稍后重试';
            } else if (errStr.includes('500')) {
                errorMsg = '服务器内部错误，请稍后重试';
            } else if (errStr.includes('abort') || errStr.includes('AbortError')) {
                errorMsg = '生成已取消';
            } else if (errStr.includes('network') || errStr.includes('Network')) {
                errorMsg = '网络连接失败，请检查网络后重试';
            }
            
            ElMessage({
                message: errorMsg,
                type: 'error',
                duration: 5000,
            });
            
            emit('requestError', err);
            throw err;
        },
    });
};

const wordEport = async () => {
    ElMessageBox.confirm('是否确认下载文件?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(async () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        let contentHtml = '';
        if (aiEditor) {
            try {
                if (aiEditor.getHtml) {
                    contentHtml = aiEditor.getHtml();
                } else if (aiEditor.getContent) {
                    contentHtml = aiEditor.getContent();
                }
            } catch (e) {
                console.error('获取编辑器内容失败:', e);
            }
        }
        if (!contentHtml) {
            contentHtml = content.value ? await marked(content.value) : '';
        }
        const converted = await asBlob(contentHtml, {orientation: 'portrait'});
        saveAs(converted, `${props.templateTitle || '解决方案'}.docx`);
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    });
};

const contentRef = ref(null);

const updateContentHeight = () => {
    const dialog = document.querySelector('.ai-dialog');
    const content = contentRef.value;
    if (dialog && content) {
        const dialogHeight = dialog.clientHeight;
        content.style.height = `${dialogHeight * 0.32}px`;
    }
};

watch(dialogVisible, (newVal) => {
    if (newVal) {
        nextTick(() => {
            updateContentHeight();
        });
    }
});

onMounted(() => {
    window.addEventListener('resize', updateContentHeight);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', updateContentHeight);
    if (aiEditor) {
        aiEditor.destroy();
    }
    if (ctrl) {
        ctrl.abort();
    }
});

// 监听外部传入的初始 HTML 变化，随时同步到编辑器
watch(() => props.initialHtml, (val) => {
    try {
        if (aiEditor && typeof aiEditor.setHtml === 'function') {
            aiEditor.setHtml(val || '');
        } else if (aiEditor && typeof aiEditor.setContent === 'function') {
            aiEditor.setContent(val || '');
        } else if (editorContainerRef.value) {
            const el = editorContainerRef.value.querySelector('.ai-editor');
            if (el) el.innerHTML = val || '';
        }
    } catch (e) {
        console.error('同步 initialHtml 失败:', e);
    }
});

// 暂停生成方法
const pauseGeneration = () => {
    isPause.value = true;
    isCreate.value = false;
    if (ctrl) {
        try {
            ctrl.abort();
        } catch (e) {
            console.error('中止请求失败:', e);
        }
    }
};

defineExpose({
    createArticle,
    pauseGeneration,
    isPause,
    isCreate,
    // 手动设置 HTML，供详情页直接注入内容
    setHtml: (html) => {
        try {
            if (aiEditor && aiEditor.setHtml) {
                aiEditor.setHtml(html || '');
            } else if (aiEditor && aiEditor.setContent) {
                aiEditor.setContent(html || '');
            } else if (editorContainerRef.value) {
                const editorElement = editorContainerRef.value.querySelector('.ai-editor');
                if (editorElement) editorElement.innerHTML = html || '';
            }
        } catch (e) {
            console.error('setHtml 调用失败:', e);
        }
    },
    // 允许外部打开/关闭自动跟随
    setAutoFollow: (val) => { autoFollowScroll.value = !!val; }
});
</script>

<style scoped>
.editor-container {
    height: 100%;
    width: 100%;
}

.dialog-content {
    overflow-y: auto;
    word-break: break-word;
    line-height: 1.5;
}

:deep(.ai-editor) {
    height: 100% !important;
    width: 100%;
}

:deep(#aiEditor) {
    height: 100%;
    width: 100%;
}
</style>