<template>
    <div class="editor-container">
        <VApp id="app">
            <VContainer>
                <VuetifyTiptap ref="editorRef"
                               v-model="content" :extensions="extensions" :hideBubble="true"
                               :min-height="vhValue" :max-height="vhValue"
                               rounded
                               editorClass="gundongtiaoyanse"
                >
                </VuetifyTiptap>
                <VuetifyViewer :value="content" />

            </VContainer>
        </VApp>

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
import {ref, onMounted, onUnmounted, computed, reactive, defineProps, watch, nextTick} from 'vue';
import {VuetifyTiptap, VuetifyViewer, createVuetifyProTipTap} from 'vuetify-pro-tiptap';
import 'vuetify-pro-tiptap/style.css'
import {
    BaseKit, Bold, Italic, Underline, Strike, Color, Highlight, Heading,
    TextAlign, FontFamily, FontSize, SubAndSuperScript, BulletList, OrderedList,
    TaskList, Indent, Link, Image, Video, Table, Blockquote, HorizontalRule, Code, CodeBlock, Clear, Fullscreen, History
} from 'vuetify-pro-tiptap'
import {marked} from 'marked';
import {BubbleMenu} from '@tiptap/extension-bubble-menu';
import {fetchEventSource} from "@microsoft/fetch-event-source";
import {ElMessage, ElMessageBox} from 'element-plus'
import {Top, Download} from '@element-plus/icons-vue'
import {getKnowToWriteUrl, createArticleUrl} from '@/service/api.solution'
import { useModelConfigStore } from '@/store/modules/modelConfig'
import {asBlob} from 'html-docx-js-typescript';

const showBubble = ref(true);
const dialogVisible = ref(false);
import interact from 'interactjs'

const editorRef = ref(null);
const editor = ref('');
const selectedText = ref('');
// 定义 props
const props = defineProps({
    templateTitle: String
});
// 计算弹框位置
const dialogStyle = ref('')
const vhValue = ref(0);
// const customButtonClicked = () => {
//   console.log("下载文件按钮被点击")
// }
// 处理点击外部关闭
const handleClickOutside1 = (event) => {
    const dialog = document.getElementById('ai-dialog')
    if (!dialog.contains(event.target) && dialogVisible.value) {
        dialogVisible.value = false
        aiInputContent.value = ""
        aiContent.value = ""
        document.removeEventListener('click', handleClickOutside1)
    }
}
// 获取选中文本位置信息的函数
const getSelectionCoords = (editor) => {
    const {from, to} = editor.state.selection

    // 获取编辑器视图的坐标信息
    const view = editor.view
    const start = view.coordsAtPos(from)
    const end = view.coordsAtPos(to)

    return {
        start: {
            x: start.left,
            y: start.top,
            height: start.bottom - start.top
        },
        end: {
            x: end.right,
            y: end.top,
            height: end.bottom - end.top
        },
        width: end.right - start.left,
        // 选中文本的整体高度
        height: Math.max(end.bottom, start.bottom) - Math.min(end.top, start.top)
    }
}
// 计算对话框位置的函数
const calculateDialogPosition = (coords) => {
    const viewportHeight = window.innerHeight

    const dialogHeight = 250 // 默认对话框高度
    const padding = 10

    // 计算上方和下方的可用空间
    const spaceBelow = viewportHeight - (coords.end.y + coords.height) //选中文本下方到视窗底部的空间
    const spaceAbove = coords.start.y //选中文本上方到视窗顶部的空间
    // 判断哪边空间较大
    // 判断哪边空间较大
    if (spaceBelow >= dialogHeight + padding || spaceAbove >= dialogHeight + padding) {
        if (spaceBelow >= spaceAbove) {
            // 下方空间较大
            dialogStyle.value = {
                position: 'fixed',
                top: `${coords.start.y + coords.height + padding}px`,
                left: `50%`,
                margin: 0,
                height: spaceBelow >= dialogHeight + padding ? `${dialogHeight}px` : `${spaceBelow - padding}px`
            }
        } else {
            // 上方空间较大
            dialogStyle.value = {
                position: 'fixed',
                bottom: `${viewportHeight - coords.start.y + padding}px`,
                left: `50%`,
                margin: 0,
                height: spaceAbove >= dialogHeight + padding ? `${dialogHeight}px` : `${spaceAbove - padding}px`
            }
        }
    } else {
        dialogStyle.value = {
            position: 'fixed',
            top: '50%',
            left: '70%',
            margin: 0,
            transform: 'translate(-50%, -50%)',
            height: `${dialogHeight}px`
        }
    }
}

const addElButton = () => {
  const parentElement = editorRef.value.$el.querySelector('.text-overline').parentElement;
  parentElement.classList.add('custom-height');
  if (parentElement) {
    const button = document.createElement('el-button');
    button.textContent = '下载文件';
    button.type = 'primary'
    button.className = 'buttonPrimary'; // 设置按钮样式
    button.onclick = () => {
      console.log("下载文件按钮被点击")
      wordEport()
    };
    parentElement.appendChild(button); // 将按钮添加到父元素中
  }
  console.log('组件挂载',parentElement)
};
onMounted(() => {
  // 计算属性，用于动态计算按钮样式
  addElButton()
    //给弹框添加可拖动功能
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
    editor.value = editorRef.value.editor; // 获取编辑器实例
    editor.value.on('selectionUpdate', () => {
        const {from, to} = editor.value.state.selection;
        if (from !== to) {
            selectedText.value = editor.value.state.doc.textBetween(from, to, ' ');
            const coords = getSelectionCoords(editor.value)
            calculateDialogPosition(coords)
            bubbleMenuElement.style.display = 'block';
            // 可以用这些信息来定位对话框
        }
    });



    // 获取需要观察的元素
    const topElement = editorRef.value.$el.querySelector('.v-toolbar__content');
    const bottomElement = editorRef.value.$el.querySelector('.text-overline').parentElement;

    // 开始观察元素尺寸变化
    resizeObserver.observe(topElement);
    resizeObserver.observe(bottomElement);
    calculateHeight();
});
// 创建 ResizeObserver 实例
const resizeObserver = new ResizeObserver((entries) => {
    calculateHeight();
});
const calculateHeight = () => {
    const topHeight = editorRef.value.$el.querySelector('.v-toolbar__content').offsetHeight;
    const bottomHeight = editorRef.value.$el.querySelector('.text-overline').parentElement.offsetHeight;
    // 获取视口的高度
    const viewportHeight = window.innerHeight;
    // 计算91vh的像素值
    vhValue.value = (91 / 100) * viewportHeight - topHeight - bottomHeight;
};
// 定义响应式数据
const content = ref('');

const aiInputContent = ref('')
const aiContent = ref('')
const aiContentHtml = ref('')

function toggleAiTextDisplay(show) {
    const div = document.getElementById('AiText');
    div.style.display = show ? "block" : "none";
}

function addGlobalClickListener() {
    document.addEventListener('click', handleClickOutside, true);
}

function handleClickOutside(event) {
    const div1 = document.getElementById('AiText');

    if (!div1.contains(event.target)) {
        toggleAiTextDisplay(false);
        aiInputContent.value = ""
        aiContent.value = ""
        // 移除点击监听器，避免重复添加
        document.removeEventListener('click', handleClickOutside, true);
    }
}

const getArticleType = (type) => {
    switch (type) {
        case 1:
            aiInputContent.value = ''
            return '扩写';
        case 2:
            aiInputContent.value = ''
            return '润色';
        case 3:
            aiInputContent.value = ''
            return '续写';
        case 4:
            aiInputContent.value = ''
            return '转化风格';
        default:
            return '';
    }
};

function toggleStatus(show) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = show ? '创作中...' : '';
}

/**
 * 调用大模型生成文章---扩写、润色、续写、改写 选中文本
 */
const getKnowToWrite = (selectTxt, type, editor, aiCreateText) => {
    const ctrl = new AbortController();
    isCreateText.value = true
    aiContentHtml.value = ''
    dialogVisible.value = true
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
            console.log('onopen', res)
        },
        onmessage(msg) {
            if (JSON.parse(msg.data).is_end === true) {
                isCreateText.value = false
                return
            }
            aiContent.value = JSON.parse(msg.data).data;
            aiContentHtml.value = marked(aiContent.value);
        },
        onclose() {
            console.log("生成结束,onclose")
            // toggleStatus(false)
            ElMessage({
                message: '创作完成.',
                type: 'success',
            })
        },
        onerror(e) {
            ctrl.abort();
            console.log("生成失败,onerror", e)
        },
    });
};
const isCreateText = ref(false);
let isCooldown = false;
let lastType = 1;
const handleWritingClick = () => {//重新写作
    if (isCooldown) return;
    // 处理点击事件
    isCooldown = true;
    setTimeout(() => {
        isCooldown = false;
    }, 1500); // 冷却时间，例如3000毫秒（3秒）
    getKnowToWrite(selectedText.value, lastType, editor, aiContent.value);
}
const handleInsertClick = () => {//插入后方
    editor.value.commands.setTextSelection({
        from: editor.value.state.selection.from,
        to: editor.value.state.selection.to
    });
    const insertContext = selectedText.value + aiContent.value;
    editor.value.commands.insertContent(insertContext.trim());
    dialogVisible.value = false
    aiContent.value = '';
}
const handleReplaceClick = () => {//替换所选
    editor.value.commands.setTextSelection({
        from: editor.value.state.selection.from,
        to: editor.value.state.selection.to
    });
    editor.value.commands.insertContent(aiContent.value.trim());
    dialogVisible.value = false
    aiContent.value = '';
}
const handleAiInputClick = () => {//用户自定义重新写作
    if (isCooldown) return;
    // 处理点击事件
    isCooldown = true;
    setTimeout(() => {
        isCooldown = false;
    }, 1500); // 冷却时间，例如3000毫秒（3秒）
    getKnowToWrite(selectedText.value, 5, editor.value, aiContent.value);
    aiContent.value = '';

}

const onClickByType = (type) => {
    getKnowToWrite(selectedText.value, type, editor.value)
}
const bubbleMenuElement = document.createElement('div');
bubbleMenuElement.innerHTML = `
  <button
     style="background-color: #5571FF;color: white;border: none;padding: 5px 10px;margin: 2px;border-radius: 4px;cursor: pointer;transition: background-color 0.3s ease;"
    onmouseover="this.style.backgroundColor='#79bbff'"
    onmouseout="this.style.backgroundColor='#007bff'"
    data-type="1">扩 写</button>
  <button
     style="background-color: #5571FF;color: white;border: none;padding: 5px 10px;margin: 2px;border-radius: 4px;cursor: pointer;transition: background-color 0.3s ease;"
    onmouseover="this.style.backgroundColor='#79bbff'"
    onmouseout="this.style.backgroundColor='#007bff'"
    data-type="2">润 色</button>
  <button
     style="background-color: #5571FF;color: white;border: none;padding: 5px 10px;margin: 2px;border-radius: 4px;cursor: pointer;transition: background-color 0.3s ease;"
    onmouseover="this.style.backgroundColor='#79bbff'"
    onmouseout="this.style.backgroundColor='#007bff'"
    data-type="3">续 写</button>
  <button
     style="background-color: #5571FF;color: white;border: none;padding: 5px 10px;margin: 2px;border-radius: 4px;cursor: pointer;transition: background-color 0.3s ease;"
    onmouseover="this.style.backgroundColor='#79bbff'"
    onmouseout="this.style.backgroundColor='#007bff'"
    data-type="4">改 写</button>
`;
// 使用事件委托处理点击事件
bubbleMenuElement.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
        const type = e.target.dataset.type;
        bubbleMenuElement.style.display = 'none';
        onClickByType(Number(type));
    }
});
const bubbleMenuVisible = ref(true);

const extensions = [
    BaseKit.configure({placeholder: ['请输入一些文字']}),
    Bold, Italic,
    Underline, Strike, Color, Highlight, Heading.configure({levels: [1, 2, 3, 4, 5, 6]}),
    TextAlign.configure({alignments: ['left', 'center', 'right', 'justify']}),
    FontFamily.configure({fonts: ['Arial', 'Times New Roman', 'Courier New', 'Verdana']}),
    FontSize.configure({sizes: [12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 72]}),
    SubAndSuperScript,
    BulletList, OrderedList,
    TaskList,
    Indent,
    Link,
    Image,
    Video,
    Table,
    Blockquote,
    HorizontalRule,
    Code,
    CodeBlock,
    Clear,
    Fullscreen,
    History,
    BubbleMenu.configure({
        element: bubbleMenuElement,
        tippyOptions: {
            placement: 'top',
            appendTo: document.body, // 将菜单附加到body
        },
    })
]

const emit = defineEmits(['requestComplete', 'requestError']);
const isPause = ref(false); //是否暂停生成文章
const isRequesting = ref(false); //限制自动的重复请求
const isCreate = ref(false); //生成文章过程中禁用编辑和下载按钮
const loading = ref(false) //生成文章过程中显示loading
// 将 ctrl 声明在外部，但在函数内部赋值
let ctrl;
//生成文章内容
const createArticle = (templateTitleParam1) => {
  console.log('createArticle', "||" , isCreate.value)
    if (isPause.value) {
      ctrl.abort();
    }
    if (isCreate.value) return
    ctrl = new AbortController();
  isRequesting.value = false
    isPause.value = false
    content.value = ''
    loading.value = true
    isCreate.value = true
    const chatPayload = {
        method: 'POST',
        body: JSON.stringify({ ...templateTitleParam1, modelId: useModelConfigStore().currentOrFirst }),
        headers: {
            'Content-Type': 'application/json',
        },
    };
    let aiContent1 = "";
    let aiValue = "";
    console.log('Starting new request...'); // 调试日志
    fetchEventSource(createArticleUrl, {
        openWhenHidden: true,
        signal: ctrl.signal,
        ...chatPayload,
        async onopen(res) {
            console.log('onopen', res)
        },
        onmessage(event) {
            if (isPause.value) {
                isCreate.value = false
                ctrl.abort();
                return;
            }
            loading.value = false
            if (JSON.parse(event.data).is_end === true) {
                console.log('Stream ended'); // 调试日志
                return
            }
            let eventData = JSON.parse(event.data).data;
            if(eventData === '\n'){
              aiContent1 += aiValue + '\n'
              console.log('eventData等于了换行夫：', eventData)
            }
          aiValue = eventData
            // aiContent1 += eventData;
            // content.value = marked(aiContent1)
            content.value = marked(aiContent1 + eventData)
            // console.log('Content updated:', aiContent1); // 调试日志
        },
        onclose() {
            loading.value = false
            isCreate.value = false
            ElMessage({
                message: '创作完成.',
                type: 'success',
            })
            emit('requestComplete', true);
        },
        onerror(err) {
            loading.value = false
            isCreate.value = false
            emit('requestError', err);
            throw err
        },
    })

}
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
        let contentHtml = await marked(content.value); // 将 Markdown 转换为 HTML
        //let contentHtml = editorRef.value.innerHTML;
        const converted = await asBlob(contentHtml, {orientation: 'portrait'});
        saveAs(converted, `${props.templateTitle || '解决方案'}.docx`)
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    });
};
const contentRef = ref(null)
// 计算内容区域高度
const updateContentHeight = () => {
    const dialog = document.querySelector('.ai-dialog')
    const content = contentRef.value
    if (dialog && content) {
        const dialogHeight = dialog.clientHeight
        content.style.height = `${dialogHeight * 0.32}px`
    }
}
// 监听对话框显示状态
watch(dialogVisible, (newVal) => {
    if (newVal) {
        nextTick(() => {
            updateContentHeight()
        })
    }
})
// 监听窗口大小变化
onMounted(() => {
    window.addEventListener('resize', updateContentHeight)
})
onUnmounted(() => {
    window.removeEventListener('resize', updateContentHeight)
    resizeObserver.disconnect();
})
defineExpose({
    createArticle, isPause, isCreate
});
</script>

<style scoped>
.article-download {
    position: absolute;
    top: 5.3%;
    right: 2%;
    float: right;
    padding: 10px;
    z-index: 1;
}

/* 内容样式 */
.dialog-content {
    overflow-y: auto;
    word-break: break-word;
    line-height: 1.5;
}
/*::v-deep .vuetify-pro-tiptap .v-input .v-input__control .v-toolbar__content .text-overline{*/
/*  float: left !important;*/
/*  background-color: red;*/
/*}*/
:deep(.vuetify-pro-tiptap .v-input .v-input__control .v-toolbar__content .text-overline) {
  margin-bottom: 1%;
  order: -1;
}
:deep(.buttonPrimary){
  display: flex; /* 使用 Flexbox */
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  width: 11%;
  height: 60%;
  margin-bottom: 0.5%;
  background-color: #5571FF;
  color: #FFFFFF;
  border-radius: 5px;
  font-size: 1.05rem;
  letter-spacing: 2px;
  /*border: 1px solid red;*/
}
/* 在你的 CSS 文件中 */
:deep(.custom-height) {
  height: 6vh !important;
}
:deep(.vuetify-pro-tiptap-editor__content::-webkit-scrollbar-thumb) {
  background-color: #DDDEE0 !important; /* 滚动条颜色 */
}
</style>
