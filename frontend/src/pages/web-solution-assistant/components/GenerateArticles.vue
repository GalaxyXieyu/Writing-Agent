<!--生成文章组件-->
<template>

  <div>
    <div style="height: 50px">
      <!--        下载按钮-->
      <el-tooltip
          v-if="!isEditable"
          effect="dark"
          content="下载"
          placement="bottom"
      >
        <el-button class="article-download" type="primary" plain size="small" style="width: 25px" @click="wordEport" :disabled="isCreate">
          <el-icon size="large"><Download /></el-icon>
        </el-button>
      </el-tooltip>
      <el-tooltip
          v-if="!isEditable"
          effect="dark"
          content="点击编辑"
          placement="bottom"
      >
        <el-button class="article-editor" type="primary" plain size="small" @click="clickEdit" style="width: 25px" :disabled="isCreate">
          <el-icon size="large"><Edit /></el-icon>
        </el-button>
      </el-tooltip>
      <el-tooltip
          v-if="isEditable"
          effect="dark"
          content="完成编辑"
          placement="bottom"
      >
        <el-button class="article-button" type="primary" size="small" @click="isEditable=false">
          完成编辑
        </el-button>
      </el-tooltip>
    </div>
    <WangEditor v-show="isEditable" ref="wangEditorRef" @update:htmlContent="handleHtmlContent"></WangEditor>
    <div id="container" ref="articleDivRef" v-show="!isEditable" style="padding: 50px;overflow-y: auto;height: 100%" v-html="markdownContentHtml" v-loading="loading" element-loading-text="Loading..."></div>

  </div>


</template>
<script setup>
import {Download,Edit} from '@element-plus/icons-vue'
import {ref,nextTick,watch,onUnmounted} from 'vue';
import WangEditor from './WangEditor.vue';
import { asBlob } from 'html-docx-js-typescript';
import { saveAs } from 'file-saver';
import { EventStreamContentType, fetchEventSource } from '@microsoft/fetch-event-source';
import { marked } from 'marked';
import { ElMessageBox } from 'element-plus'

const allTitleData = ref([{titleId:Date.now().toString(36),children:[]}]);//一级标题
const maxTitle = ref();//文章标题
const isEditable = ref(false);
const isPause = ref(false);
const articleDivRef = ref(null);
const wangEditorRef = ref(null);
const htmlContent = ref('');// 存储富文本内容
const markdownContent = ref('');
const markdownContentHtml = ref('');
const isCreate = ref(false); //生成文章过程中禁用编辑和下载按钮
const loading = ref(false) //生成文章过程中显示loading
const isShowTips = ref(true) //tips显示

const clickEdit = () => {
    if(isShowTips){
        isShowTips.value = false
        // var div1 = document.getElementById('tips');
        // div1.style.display = "none";
    }
  isEditable.value = true;
  const editHtml = articleDivRef.value.innerHTML;
  // console.log("editHtml.value=",editHtml)
  wangEditorRef.value.toEditValueHtml(editHtml)

};
const handleHtmlContent = (newHtml) => {
  //完成编辑
  htmlContent.value=newHtml;
  articleDivRef.value.innerHTML = newHtml
};

var that =this;
const wordEport = async () => {
    ElMessageBox.confirm('是否确认下载文件?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(async () => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        let contentHtml = articleDivRef.value.innerHTML;
        const converted = await asBlob(contentHtml, {orientation: 'portrait'});
        saveAs(converted, `导出文档_${year}${month}${day}${hours}${minutes}${seconds}.docx`)
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    });
};
// const ctrl = new AbortController();
let isFetching = false;
const createArticle = (templateTitleParam1) => {
    if(isFetching) return
    isFetching = true
    if(isCreate.value) return
  loading.value = true
  isCreate.value = true
  // let generateUrl = "http://localhost:18765/fangan/articleCreate";
  let generateUrl = "https://www.tianshu.chat:29847/api/v2/solution/generate-article";
  const chatPayload = {
    method: 'POST',
    body: JSON.stringify(templateTitleParam1),
    headers: {
      'Content-Type': 'application/json',
    },
  };
    let aiContent1 = "";
    let preventDuplication = false
  fetchEventSource(generateUrl, {
      openWhenHidden: true,
      signal: ctrl.signal,
    ...chatPayload,
    async onopen(res){
        if(preventDuplication) return
        preventDuplication = true
      console.log('onopen', res)
    },
      onmessage(event) {
          if(isPause.value){
              ctrl.abort();
              return;
          }
          loading.value = false
          if(JSON.parse(event.data).is_end === true) {
              isFetching = false
              return
          }
          let eventData  = JSON.parse(event.data).data;
          aiContent1 += eventData ;
          console.log('onmessage', aiContent1)
          markdownContentHtml.value = marked(aiContent1)
      },
    onclose() {
        loading.value = false
      isCreate.value = false
      console.log('onclose')
        preventDuplication = false
    },
    onerror(err) {
        preventDuplication = false
        loading.value = false
        isCreate.value = false
        isFetching = false
      console.log('onerror', err)
    },
  })

}
onUnmounted(()=>{
    ctrl.abort();
})
defineExpose({
  createArticle,isPause
});
</script>

<style scoped>
.maxTitle{
  padding-left: 20px;
  padding-bottom: 20px;

}
.firstTitle{
  padding-left: 20px;
}
.secondTitle{
  padding-left: 20px;
}
.context{
  padding: 10px;

}
.article-editor{
  position: absolute;
  top: 6%;
  right: 7%;
  float: right;
  padding: 10px;
}
.article-download{
  position: absolute;
  top: 6%;
  right: 4%;
  float: right;
  padding: 10px;
}
.article-button{
  float: right;
  margin-right: 10px;
  margin-top: 20px;
}

</style>
