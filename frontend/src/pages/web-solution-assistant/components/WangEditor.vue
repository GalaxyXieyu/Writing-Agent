<template>
  <div style="border: 1px solid #ccc">
    <Toolbar
        style="border-bottom: 1px solid #ccc"
        :editor="editorRef"
        :defaultConfig="toolbarConfig1"
    />
    <Editor
        style="height: 600px; overflow-y: auto;"
        :defaultConfig="editorConfig"
        @onCreated="handleCreated"
        @onChange="handleChange"

    />
    <div id="AiText" class="AiText">

      <div id="sseContent" class="aitext" v-html="aiContentHtml"></div><br>
      <div class="editor-button">
          <p id="status" class="inline-elements"></p>
        <el-button id="rexie">重新写作</el-button>
        <el-button id="charu">插入后方</el-button>
        <el-button id="tihuan" type="primary">替换所选</el-button>
      </div>
         <el-divider style="position: absolute;margin-top: -6px;margin-left: -2%"/>
        <div class="aiInput">
            <el-input
                v-model="aiInputContent"
                placeholder="请输入优化建议"
                type="text"
                style="height: 36px"
            >
                <template #suffix>
                    <el-button id="aiInputClick" type="primary" size="small"  circle><el-icon><Top /></el-icon></el-button>
                </template>
            </el-input>
        </div>
    </div>
  </div>
</template>
<script setup>
// import '@wangeditor/editor/dist/css/style.css' // 引入 css
import {onBeforeUnmount, ref, shallowRef, onMounted, reactive, nextTick} from 'vue'
import {Editor, Toolbar} from '@wangeditor/editor-for-vue'
import {DomEditor, Boot} from '@wangeditor/editor'
import {EventStreamContentType, fetchEventSource} from "@microsoft/fetch-event-source";
import {marked} from "marked";
import {Top} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

// 内容 HTML
const valueHtml = ref('')
const aiInputContent = ref('')
const aiContentHtml = ref('')

// const markdownContentHtml = ref('')
// const markdownContent = ref('')

const emit = defineEmits(['update:htmlContent']); // 定义一个事件来传递HTML内容

const toolbarConfig1 = {
  toolbarKeys: [
    "headerSelect",
    'bold', // 加粗
    'italic', // 斜体
    'through', // 删除线
    'underline', // 下划线
    'bulletedList', // 无序列表
    'numberedList', // 有序列表
    'color', // 文字颜色
    'bgColor', // 背景颜色
    "fontFamily", // 字体
    'fontSize', // 字体大小
    'lineHeight', // 行高
    'delIndent', // 缩进
    'indent', // 增进
    'justifyCenter', // 居中对齐
    'justifyJustify', // 两端对齐
    'justifyLeft', // 左对齐
    'justifyRight', // 右对齐
    'undo', // 撤销
    'redo', // 重做
    'clearStyle', // 清除格式
    'fullScreen' // 全屏

  ],
}

const editorConfig = {
  placeholder: '请输入内容...',
  // 其他配置...
  hoverbarKeys: {
    text: {
      //扩写、润色、续写、改写
      //expand, polish, continue, rewrite
      menuKeys: ['custom-expand', 'custom-polish', 'custom-continue', 'custom-rewrite'] // 文本元素的悬浮工具栏菜单项
    },
    //暂时没有图片和表格，只针对文字悬浮工具
    // image: {
    //   menuKeys: ['imageWidth30', 'imageWidth50', 'imageWidth100', 'deleteImage'] // 图片元素的悬浮工具栏菜单项
    // },
    // table: {
    //   menuKeys: [
    //     'enter', 'tableHeader', 'tableFullWidth',
    //     'insertTableRow', 'deleteTableRow',
    //     'insertTableCol', 'deleteTableCol', 'deleteTable'
    //   ] // 表格元素的悬浮工具栏菜单项
    // }
  }
};

// const editorConfig = { placeholder: '请输入内容...' }

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

const handleCreated = (editor) => {
  editorRef.value = editor // 记录 editor 实例，重要！

  const expandMenuConf = {
    key: 'custom-expand',//定义 menu key ：要保证唯一、不重复（重要）
    factory() {
      return new expandButtonMenu()//替换为你菜单的class
    },
  }
  const polishMenuConf = {
    key: 'custom-polish',//定义 menu key ：要保证唯一、不重复（重要）
    factory() {
      return new polishButtonMenu()//替换为你菜单的class
    },
  }
  const continueMenuConf = {
    key: 'custom-continue',//定义 menu key ：要保证唯一、不重复（重要）
    factory() {
      return new continueButtonMenu()//替换为你菜单的class
    },
  }
  const rewriteMenuConf = {
    key: 'custom-rewrite',//定义 menu key ：要保证唯一、不重复（重要）
    factory() {
      return new rewriteButtonMenu()//替换为你菜单的class
    },
  }
  //注册菜单
  if (!editor.getAllMenuKeys()?.includes("custom-expand")) {
    Boot.registerMenu(expandMenuConf)
  }
  if (!editor.getAllMenuKeys()?.includes("custom-polish")) {
    Boot.registerMenu(polishMenuConf)
  }
  if (!editor.getAllMenuKeys()?.includes("custom-continue")) {
    Boot.registerMenu(continueMenuConf)
  }
  if (!editor.getAllMenuKeys()?.includes("custom-rewrite")) {
    Boot.registerMenu(rewriteMenuConf)
  }

}

//扩写按
class expandButtonMenu {
  constructor() {
    this.title = '扩 写'
    // this.iconSvg = '<svg >...</svg>'
    this.tag = 'button'
  }
  // 获取菜单执行时的 value ，用不到则返回空 字符串或 false
  getValue(editor) {
    const selectText = editor.getSelectionText();//仅提取文本
    console.log("提取选中文本=", selectText)
    return selectText
  }
  // 菜单是否需要激活（如选中加粗文本，“加粗”菜单会激活），用不到则返回 false
  isActive(editor) {
    return false // or true
  }
  // 菜单是否需要禁用（如选中 H1 ，“引用”菜单被禁用），用不到则返回 false
  isDisabled(editor) {
    return false // or true
  }
  // 点击菜单时触发的函数
  exec(editor, value) {
    // editor.insertText(value) // value 即 this.getValue(editor) 的返回值
    getKnowToWrite(value, 1, editor)
      aiInputContent.value = ""
      // toggleAiTextDisplay(true)
  }
}
//润色按钮
class polishButtonMenu {
  constructor() {
    this.title = '润 色'
    // this.iconSvg = '<svg >...</svg>'
    this.tag = 'button'
  }
  getValue(editor) {
    return editor.getSelectionText()
  }
  isActive(editor) {
    return false // or true
  }
  isDisabled(editor) {
    return false // or true
  }
  exec(editor, value) {
    // editor.insertText(value) // value 即 this.getValue(editor) 的返回值
    getKnowToWrite(value, 2, editor)
      aiInputContent.value = ""
  }
}
//续写按钮
class continueButtonMenu {
  constructor() {
    this.title = '续 写'
    // this.iconSvg = '<svg >...</svg>'
    this.tag = 'button'
  }
  getValue(editor) {
    return editor.getSelectionText()
  }
  isActive(editor) {
    return false // or true
  }
  isDisabled(editor) {
    return false // or true
  }
  exec(editor, value) {
    // editor.insertText(value) // value 即 this.getValue(editor) 的返回值
    getKnowToWrite(value, 3, editor)
      aiInputContent.value = ""
  }
}
//改写按钮
class rewriteButtonMenu {
  constructor() {
    this.title = '改 写'
    // this.iconSvg = '<svg >...</svg>'
    this.tag = 'button'
  }
  getValue(editor) {
    return editor.getSelectionText()
  }
  isActive(editor) {
    return false // or true
  }
  isDisabled(editor) {
    return false // or true
  }
  exec(editor, value) {
    // editor.insertText(value) // value 即 this.getValue(editor) 的返回值
    getKnowToWrite(value, 4, editor)
      aiInputContent.value = ""
  }
}


const handleChange = (editor) => {
  // 将新HTML内容传递给父组件
  const newHtml = editor.getHtml()
  emit('update:htmlContent', newHtml);
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
/**
 * 调用大模型生成文章---扩写、润色、续写、改写 选中文本
 */
const getKnowToWrite = (selectTxt, type, editor,aiCreateText) => {
  toggleAiTextDisplay(true)
    toggleStatus(true)
    localStorage.setItem('myEditorItem', JSON.stringify(editor.selection));
  document.getElementById('sseContent').innerText = ''
  let AiText = '';
  let isCooldown = false;
    // let generateUrl = "http://localhost:18765/fangan/txtAbility";
    // let generateUrl = "https://www.tianshu.chat:18766/fangan/txtAbility";
    let generateUrl = "https://www.tianshu.chat:29847/api/v2/solution/optimize-content";
    const requestPayload = {
        "original_text": selectTxt,
        "article_type": getArticleType(type),
        "user_requirements":aiInputContent.value
    };
  const chatPayload = {
    method: "POST",
    body: JSON.stringify(requestPayload),
    headers: {
      "Content-Type": "application/json",
    },
  };
  fetchEventSource(generateUrl, {
      openWhenHidden: true,
      ...chatPayload,
    async onopen(res) {
      console.log('onopen', res)
    },
      onmessage(msg) {
          console.log('onmessage', msg)
          if (JSON.parse(msg.data).is_end === true) {
              return
          }
          let eventData = JSON.parse(msg.data).data;
          AiText += eventData;
          // document.getElementById('sseContent').innerText = AiText;
          const sseContent = document.getElementById('sseContent');
          // sseContent.innerText = marked(AiText);
          aiContentHtml.value = marked(AiText);
          sseContent.scrollTop = sseContent.scrollHeight;
      },
    onclose() {
      console.log("生成结束,onclose")
        toggleStatus(false)
        ElMessage({
            message: '创作完成.',
            type: 'success',
        })
    },
    onerror(e) {
      console.log("生成失败,onerror", e)
    },
  });
  addGlobalClickListener();
  document.getElementById('rexie').addEventListener('click', handleWritingClick);
  document.getElementById('charu').addEventListener('click', handleInsertClick);
  document.getElementById('tihuan').addEventListener('click', handleReplaceClick);
  document.getElementById('aiInputClick').addEventListener('click', handleAiInputClick);
  function handleWritingClick() {
    if (isCooldown) return;
    // 处理点击事件
    isCooldown = true;
    setTimeout(() => {
      isCooldown = false;
    }, 3000); // 冷却时间，例如3000毫秒（3秒）
      removeEventListener();
    getKnowToWrite(selectTxt, type, editor,AiText);
      AiText = '';
  }
    function handleAiInputClick() {
        if (isCooldown) return;
        // 处理点击事件
        isCooldown = true;
        setTimeout(() => {
            isCooldown = false;
        }, 3000); // 冷却时间，例如3000毫秒（3秒）
        editor.select(JSON.parse(localStorage.getItem('myEditorItem')))
        removeEventListener();
        getKnowToWrite(selectTxt, 5, editor,AiText);
        AiText = '';

    }

  function handleInsertClick() {
    const insertContext = selectTxt + AiText;
    console.log('insertContext:', editor);
    // editor.insertText(insertContext, editor.getSelectionPosition());
    editor.dangerouslyInsertHtml(marked(insertContext), editor.getSelectionPosition());
    AiText = '';
    toggleAiTextDisplay(false);
    removeEventListener();
  }

  function handleReplaceClick() {
    // editor.insertText(AiText, editor.getSelectionPosition());
      editor.dangerouslyInsertHtml(marked(AiText), editor.getSelectionPosition());
    AiText = '';
    toggleAiTextDisplay(false);
    removeEventListener();
  }
  function removeEventListener() { //销毁绑定的点击事件
    document.getElementById('rexie').removeEventListener('click', handleWritingClick);
    document.getElementById('charu').removeEventListener('click', handleInsertClick);
    document.getElementById('tihuan').removeEventListener('click', handleReplaceClick);
    document.getElementById('aiInputClick').removeEventListener('click', handleAiInputClick);
  }

};
function toggleStatus(show) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = show ? '创作中...' : '';
}
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
    // 移除点击监听器，避免重复添加
    document.removeEventListener('click', handleClickOutside, true);
  }
}
const toEditValueHtml = (editHtml) => {
  const editor = editorRef.value
  if (editor == null) return
  valueHtml.value = editHtml
  // 需要对editor进行焦点选中,才能插入HTML生效
  if (editor.isDisabled()) editor.enable()
  if (!editor.isFocused()) editor.focus()
  editor.clear()
  editor.dangerouslyInsertHtml(editHtml)

  // const toolbar = DomEditor.getToolbar(editor)
  // const curToolbarConfig = toolbar.getConfig()
  // console.log( curToolbarConfig.toolbarKeys ) // 当前菜单排序和分组
}

defineExpose({
  toEditValueHtml,

});
</script>
<style scoped>
::-webkit-scrollbar {  width: 0 !important;}
::-webkit-scrollbar {  width: 0 !important;height: 0;}
.AiText {
  display: none;
  position: absolute;
  top: 40%;
  background: white;
  /*padding: 20px;*/
    padding: 20px;
    padding-bottom: 40px;
  margin-left: 3%;
  width: 60%;
    /*height: 60px;*/
  border: 1px solid rgb(13, 124, 255);
  border-radius: 3px;
  max-height: 21vh;
  overflow-y: hidden;
  /*margin-bottom: 25px;*/

}
#sseContent {
    /*border: 1px solid red;*/
  max-height: calc(20vh - 50px); /* 15vh 减去上面padding 20px 以及 editor-button 高度20px 及其margin-top 5px*/
  overflow-y: auto;
  padding-bottom: 30px; /* 防止内容被按钮覆盖 */
}
.editor-button{
  position: absolute;
  bottom: 12px; /* 距离底部保持一定距离 */
  left: 0;
  right: 0;
  margin-top: 20px;
  margin-right: 24px;
  margin-bottom: 40px;
  background: white;
  text-align: right;
}
.aiInput{
    position: absolute;
    width: 94%;
    /*margin-top: -1px;*/
    margin-left: 1%;

}
.inline-elements{
    display:inline-block;
    margin-top: 3px;
    float: left;
    margin-left: 2%;
    font-size: 18px;

}
</style>
