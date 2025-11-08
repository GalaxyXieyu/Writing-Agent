<template>
    <div class="editor-container h-full flex flex-col relative">
        <div class="flex-1 relative h-full w-full" ref="editorContainerRef" v-loading="loading" element-loading-text="生成中..."></div>
        
        <el-dialog
            id="ai-dialog"
            v-model="dialogVisible"
            :close-on-click-modal="false"
            :modal="false"
            :style="dialogStyle"
            class="ai-dialog"
            title="Ai智能助手"
            width="40%"
        >
            <div ref="contentRef" class="dialog-content" v-html="aiContentHtml"></div>
            <template #footer>
                <div class="dialog-footer">
                    <span v-show="isCreateText" style="float: left">创作中...</span>
                    <el-button @click="handleWritingClick">重新写作</el-button>
                    <el-button @click="handleInsertClick">插入后方</el-button>
                    <el-button type="primary" @click="handleReplaceClick">
                        替换所选
                    </el-button>
                </div>
                <el-divider style="margin: 10px 0"/>
                <div class="input-area">
                    <el-input
                        v-model="aiInputContent"
                        placeholder="请输入优化建议"
                        style="height: 36px"
                        type="text"
                    >
                        <template #suffix>
                            <el-button circle size="small" type="primary" @click="handleAiInputClick">
                                <el-icon>
                                    <Top/>
                                </el-icon>
                            </el-button>
                        </template>
                    </el-input>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount, watch, nextTick} from 'vue';
import {AiEditor} from "aieditor";
import "aieditor/dist/style.css";
import {marked} from 'marked';
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {ElMessage, ElMessageBox} from 'element-plus'
import {Top} from '@element-plus/icons-vue'
import {getKnowToWriteUrl, createArticleUrl} from '@/service/api.solution'
import {useModelConfigStore} from '@/store/modules/modelConfig'
import {asBlob} from 'html-docx-js-typescript';
import {saveAs} from 'file-saver';
import interact from 'interactjs'

const props = defineProps({
    templateTitle: String
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
const loading = ref(false);
let ctrl;
let isCooldown = false;
let lastType = 1;

const emit = defineEmits(['requestComplete', 'requestError']);

const getAiEditorConfig = () => {
    const env = import.meta.env;
    const aiConfig = {};
    
    if (env.VITE_AI_EDITOR_ENABLED === 'true') {
        const models = {};
        
        if (env.VITE_AI_OPENAI_API_KEY) {
            models.openai = {
                apiKey: env.VITE_AI_OPENAI_API_KEY,
                model: env.VITE_AI_OPENAI_MODEL || 'gpt-4o-mini',
                baseURL: env.VITE_AI_OPENAI_BASE_URL || undefined
            };
        }
        
        if (env.VITE_AI_SPARK_APP_ID && env.VITE_AI_SPARK_API_KEY && env.VITE_AI_SPARK_API_SECRET) {
            models.spark = {
                appId: env.VITE_AI_SPARK_APP_ID,
                apiKey: env.VITE_AI_SPARK_API_KEY,
                apiSecret: env.VITE_AI_SPARK_API_SECRET,
                version: env.VITE_AI_SPARK_VERSION || 'v3.5'
            };
        }
        
        if (Object.keys(models).length > 0) {
            aiConfig.models = models;
        }
    }
    
    return Object.keys(aiConfig).length > 0 ? aiConfig : null;
};

onMounted(() => {
    nextTick(() => {
        if (editorContainerRef.value) {
            const aiConfig = getAiEditorConfig();
            aiEditor = new AiEditor({
                element: editorContainerRef.value,
                placeholder: "点击输入内容...",
                content: '',
                onChange: (editor) => {
                    if (editor && editor.getHtml) {
                        content.value = editor.getHtml();
                    }
                },
                ...(aiConfig ? { ai: aiConfig } : {})
            });
            
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
                }
            }
        }
    });

    interact('.el-dialog')
        .draggable({
            allowFrom: '.el-dialog__header',
            modifiers: [
                interact.modifiers.restrictRect({
                    restriction: 'parent'
                })
            ],
            listeners: {
                move(event) {
                    const target = event.target
                    const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx
                    const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy
                    target.style.transform = `translate(${x}px, ${y}px)`
                    target.setAttribute('data-x', x)
                    target.setAttribute('data-y', y)
                }
            }
        })
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
    loading.value = true;
    isCreate.value = true;
    const chatPayload = {
        method: 'POST',
        body: JSON.stringify({...templateTitleParam1, modelId: useModelConfigStore().currentOrFirst}),
        headers: {
            'Content-Type': 'application/json',
        },
    };
    let aiContent1 = "";
    let aiValue = "";
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
            if (JSON.parse(event.data).is_end === true) {
                console.log('Stream ended');
                return;
            }
            let eventData = JSON.parse(event.data).data;
            if (eventData === '\n') {
                aiContent1 += aiValue + '\n';
            }
            aiValue = eventData;
            aiContent1 += eventData;
            const htmlContent = marked(aiContent1);
            content.value = htmlContent;
            if (aiEditor) {
                try {
                    if (aiEditor.setHtml) {
                        aiEditor.setHtml(htmlContent);
                    } else if (aiEditor.setContent) {
                        aiEditor.setContent(htmlContent);
                    }
                } catch (e) {
                    console.error('更新编辑器内容失败:', e);
                }
            }
        },
        onclose() {
            loading.value = false;
            isCreate.value = false;
            ElMessage({
                message: '创作完成.',
                type: 'success',
            });
            emit('requestComplete', true);
        },
        onerror(err) {
            loading.value = false;
            isCreate.value = false;
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

defineExpose({
    createArticle,
    isPause,
    isCreate
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