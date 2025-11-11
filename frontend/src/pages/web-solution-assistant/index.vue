<template>

    <div class="flex h-full min-h-0 gap-responsive bg-background p-responsive">
      <!-- 左侧表单区域 -->
      <div class="flex w-full h-full min-h-0 min-w-0 flex-col gap-responsive md:w-2/5 lg:w-2/5 xl:w-1/3 min-w-[280px] sm:min-w-[320px] md:min-w-[360px] lg:min-w-[380px]">
        <!-- 模板选择区域 -->
        <Card class="flex flex-col flex-1 min-h-0">
          <CardHeader class="flex flex-row items-center justify-between pb-3 px-responsive pt-responsive">
            <CardTitle class="text-responsive-base font-semibold">写作模板</CardTitle>
            <Button variant="ghost" size="sm" @click="lookTemplateDialog" class="h-auto p-0 text-primary text-responsive-sm">
              查看全部模板
              <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </Button>
          </CardHeader>
          <CardContent class="flex flex-1 min-h-0 flex-col gap-4 px-responsive pb-responsive">
            <div class="flex items-center gap-2">
              <Input v-model="search" placeholder="搜索模板" class="flex-1" />
              <el-select v-model="leftFilterType" size="small" style="width: 140px">
                <el-option label="全部" value="all" />
                <el-option label="写作模板" value="1" />
                <el-option label="文件模板" value="2" />
                <el-option label="AI生成" value="3" />
              </el-select>
            </div>
            <div class="flex-1 min-h-0 overflow-y-auto border-y">
              <el-table 
                ref="tableRef" 
                :key="tableKey" 
                :data="filteredLeftList"  
                highlight-current-row
                @current-change="chooseTemplateFun"
                :row-key="getRowKey"
                :show-header="false"
                class="no-horizontal-border"
                scrollbar-always-on>
                <el-table-column>
                  <template #default="scope">
                    {{ scope.row.template_name }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <Button variant="outline" @click="openBuilder" class="w-full">
              生成自定义模板
            </Button>
          </CardContent>
        </Card>

        <!-- 表单输入区域 -->
        <Card class="flex flex-1 flex-col overflow-hidden min-h-0">
          <CardContent class="flex flex-1 flex-col gap-responsive overflow-y-auto p-responsive min-h-0 pb-24">
            <!-- 顶部：模型选择 + 全屏大纲入口 -->
            <div class="flex items-center justify-between flex-shrink-0 mt-1 pt-2 pb-2 border-b border-border">
              <div class="flex items-center gap-4">
                <Label class="text-responsive-sm font-medium text-foreground/90 whitespace-nowrap flex-shrink-0 min-w-[80px]">模型选择</Label>
                <ModelSelector v-model="currentModelId" @manage="openModelManage" />
              </div>
              <Button variant="outline" size="sm" @click="showOutlineFullscreen = true" class="gap-1">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 9V5h4M20 9V5h-4M4 15v4h4M20 15v4h-4"/>
                </svg>
                编辑大纲
              </Button>
            </div>

            <!-- 文章标题 -->
            <div v-if="!showOutlineFullscreen" class="space-y-2 flex-shrink-0 mt-4">
              <div class="flex items-center justify-between">
                <Label for="template-title" class="text-responsive-sm font-medium">文章标题</Label>
                <Button variant="ghost" size="sm" @click="saveTemplateDialog" class="h-auto p-0 text-primary text-responsive-xs">
                  保存模板
                </Button>
              </div>
              <Textarea
                id="template-title"
                v-model="templateTitle"
                placeholder="输入文章标题"
                :maxlength="100"
                class="min-h-responsive"
              />
              <p class="text-right text-responsive-xs text-muted-foreground">{{ templateTitle.length }}/100</p>
            </div>

            <!-- 文章要求 -->
            <div v-if="!showOutlineFullscreen" class="space-y-2 flex-shrink-0 mt-4">
              <Label for="article-requirement" class="text-responsive-sm font-medium">文章要求</Label>
              <Textarea
                id="article-requirement"
                v-model="articleRequirement"
                placeholder="请输入文章要求"
                :maxlength="100"
                class="min-h-responsive"
              />
              <p class="text-right text-responsive-xs text-muted-foreground">{{ articleRequirement.length }}/100</p>
            </div>

            <!-- 大纲列表 + 编辑区（与标题/要求同层级，统一滚动） -->
            <div class="mt-4" v-loading="loading" element-loading-text="Loading...">
              <!-- 大纲目录（仅内容决定高度，不设内部滚动） -->
              <div class="border rounded-lg p-2">
                <div class="flex items-center justify-between mb-2">
                  <Label class="text-responsive-sm font-medium">大纲列表</Label>
                  <div class="w-52">
                    <Input v-model="outlineSearch" placeholder="搜索标题/要求" />
                  </div>
                </div>
                <ul class="space-y-1 text-sm">
                  <li v-for="(n1, i1) in filteredOutline" :key="`mini-tree-1-${i1}`">
                    <div class="px-2 py-1 rounded hover:bg-accent cursor-pointer" @click="scrollToId(`first-${n1.id}`)">
                      {{ n1.name || `一级标题 ${i1+1}` }}
                    </div>
                    <ul v-if="n1.children?.length" class="ml-3 mt-1 space-y-1">
                      <li v-for="(n2, i2) in n1.children" :key="`mini-tree-2-${i1}-${i2}`">
                        <div class="px-2 py-1 rounded hover:bg-accent cursor-pointer" @click="scrollToId(`second-${n2.id}`)">
                          {{ n2.name || `二级标题 ${i1+1}.${i2+1}` }}
                        </div>
                        <ul v-if="n2.children?.length" class="ml-3 mt-1 space-y-1">
                          <li v-for="(n3, i3) in n2.children" :key="`mini-tree-3-${i1}-${i2}-${i3}`">
                            <div class="px-2 py-1 rounded hover:bg-accent cursor-pointer" @click="scrollToId(`third-${n3.id}`)">
                              {{ n3.name || `三级标题 ${i1+1}.${i2+1}.${i3+1}` }}
                            </div>
                          </li>
                        </ul>
                      </li>
                    </ul>
                  </li>
                </ul>
              </div>
              <!-- 编辑区（不设置overflow，与外层同一滚动） -->
              <div class="mt-3">
                <title-input :title-data="titleData"></title-input>
              </div>
            </div>
          </CardContent>

          <!-- 底部操作栏 -->
          <div class="border-t bg-background p-responsive flex-shrink-0 sticky bottom-0 z-10">
            <Button 
              v-if="!isCreate" 
              @click="createArticle"
              class="w-full"
            >
              生成文章
            </Button>
            <Button 
              v-else 
              variant="destructive"
              @click="pauseCreate"
              class="w-full"
            >
              暂停生成
            </Button>
          </div>
        </Card>
      </div>

      <!-- 右侧内容区域 -->
      <div class="flex-1 min-w-0 min-h-0 overflow-auto rounded-lg bg-background">
        <rich-text-editor 
          ref="richTextEditorRefs"
          :templateTitle="templateTitle"
          @requestComplete="handleRequestComplete"
          @requestError="handleRequestError"
        />
      </div>
    </div>

    <!-- 大纲编辑弹窗（居中，限制高度，内容区滚动，底部固定） -->
    <Dialog v-model="showOutlineFullscreen" :closeOnOverlay="true" className="w-[80vw] max-w-[1100px] max-h-[85vh] p-0 overflow-hidden">
      <div class="grid grid-rows-[auto,1fr,auto] h-full overflow-hidden">
        <DialogHeader class="px-4 py-3">
          <DialogTitle>编辑大纲</DialogTitle>
        </DialogHeader>
        <!-- 内容区：统一由该容器滚动，避免多层滚动冲突，并为底部操作条预留空间 -->
        <div class="flex min-h-0 overflow-y-auto pb-24">
          <!-- 左侧目录树 -->
          <div class="hidden md:flex md:w-64 lg:w-72 border-r border-border flex-col min-h-0">
            <div class="p-3 border-b">
              <Input v-model="outlineSearch" placeholder="搜索标题/要求" />
            </div>
            <div class="flex-1 p-2">
              <ul class="space-y-1 text-sm">
                <li v-for="(n1, i1) in filteredOutline" :key="`tree-1-${i1}`">
                  <button class="w-full text-left px-2 py-1 rounded hover:bg-accent" @click="scrollToId(`first-${n1.id}`)">{{ n1.name || `一级标题 ${i1+1}` }}</button>
                  <ul v-if="n1.children?.length" class="ml-3 mt-1 space-y-1">
                    <li v-for="(n2, i2) in n1.children" :key="`tree-2-${i1}-${i2}`">
                      <button class="w-full text-left px-2 py-1 rounded hover:bg-accent" @click="scrollToId(`second-${n2.id}`)">{{ n2.name || `二级标题 ${i1+1}.${i2+1}` }}</button>
                      <ul v-if="n2.children?.length" class="ml-3 mt-1 space-y-1">
                        <li v-for="(n3, i3) in n2.children" :key="`tree-3-${i1}-${i2}-${i3}`">
                          <button class="w-full text-left px-2 py-1 rounded hover:bg-accent" @click="scrollToId(`third-${n3.id}`)">{{ n3.name || `三级标题 ${i1+1}.${i2+1}.${i3+1}` }}</button>
                        </li>
                      </ul>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
          <!-- 右侧编辑区 -->
          <div class="flex-1 p-4">
            <div class="max-w-5xl mx-auto space-y-4">
              <div class="space-y-2">
                <Label class="text-sm font-medium">文章标题</Label>
                <Input v-model="templateTitle" placeholder="输入文章标题" />
              </div>
              <div class="space-y-2">
                <Label class="text-sm font-medium">文章要求</Label>
                <Textarea v-model="articleRequirement" placeholder="请输入文章要求" class="min-h-[100px]" />
              </div>
              <TitleInput :title-data="titleData" />
            </div>
          </div>
        </div>
        <!-- 底部操作条固定在弹窗底部上方，不遮挡内容 -->
        <DialogFooter class="px-4 py-3 border-t bg-background sticky bottom-0 z-20">
          <Button variant="outline" @click="showOutlineFullscreen = false">关闭</Button>
          <Button variant="outline" @click="saveTemplateDialog">保存大纲</Button>
          <Button @click="confirmOutlineFromFullscreen">应用并关闭</Button>
        </DialogFooter>
      </div>
    </Dialog>


    <Dialog v-model="showSaveTemplateDialog" className="max-w-md">
      <DialogHeader>
        <DialogTitle>请输入自定义模板名称</DialogTitle>
      </DialogHeader>
      <div class="space-y-4 py-4">
        <div v-if="showSaveTemplate" class="space-y-2">
          <Label>如何保存该自定义模板：</Label>
          <div class="flex gap-2">
            <Button 
              :variant="isAdd === '1000' ? 'default' : 'outline'"
              @click="isAdd = '1000'"
              class="flex-1"
            >
              保存为新模板
            </Button>
            <Button 
              :variant="isAdd === '1001' ? 'default' : 'outline'"
              @click="isAdd = '1001'"
              class="flex-1"
            >
              覆盖原有模板
            </Button>
          </div>
        </div>
        <div class="space-y-2">
          <Label for="template-name">模板名称：</Label>
          <Textarea
            id="template-name"
            v-model="templateName"
            placeholder="请输入模板名称"
            :maxlength="50"
            class="min-h-[60px]"
          />
          <p class="text-right text-xs text-muted-foreground">{{ templateName.length }}/50</p>
        </div>
      </div>
      <DialogFooter>
        <Button variant="outline" @click="cancelSave()">取消</Button>
        <Button @click="saveTemplate()">确认</Button>
      </DialogFooter>
    </Dialog>
  <el-dialog
      v-model="showTemplateDialog"
      @close="showTemplateDialog = false"
      title="全部模板"
      append-to-body
      width="80%"
      class="template-dialog"
  >
      <div class="mb-4 flex items-center gap-4">
        <Input
            v-model="searchTemplateName"
            placeholder="输入关键字查询"
            class="flex-1 max-w-md"
        />
        <div class="flex gap-2">
          <Button variant="outline" @click="resetForm">重置</Button>
          <Button @click="queryAllTemplate()">查询</Button>
        </div>
      </div>
      <el-table
          :data="allTemplateData"
          class="scrollable-table"
          :row-class-name="tableRowClassName"
          :header-cell-style="{backgroundColor: '#ECF4FF'}"
      >
        <el-table-column align="right" width="30px">
          <template #default="scope">
            <el-radio v-model.trim="selectRadio" :label="scope.row.INDEX" @change="handleRadioChange(scope)"></el-radio>
          </template>
        </el-table-column>
        <el-table-column property="template_name" label="模板名称" width="" align="center" />
        <el-table-column property="create_time" label="创建时间" width="" align="center" />
        <el-table-column fixed="right" label="操作" min-width="" align="center">
          <template v-slot:default="{row}">
            <el-button link type="primary" size="default" style="color: #5571FF" @click="reNameHandleClick(row)">重命名</el-button>
            <el-button link type="primary" size="default" style="color: #5571FF" @click="deleteAllHandleClick(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
          style="margin-top: 20px;justify-content: end"
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 25, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
      />
      <template #footer>
        <div class="flex justify-end gap-2">
          <Button variant="outline" @click="canclAllTemplate">取 消</Button>
          <Button @click="selectOneTemplate">选 定</Button>
        </div>
      </template>
  </el-dialog>

  <!-- 新版生成自定义模板对话框（shadcn 风格） -->
  <TemplateBuilderDialog
    v-model:visible="builderVisible"
    :model-id="createTemplateModelId"
    @applied="handleAppliedTemplate"
    @openLibrary="openLibraryFromResult"
    @manageModel="openModelManage"
  />
  <Dialog v-model="reNameVisible" className="max-w-md">
    <DialogHeader>
      <DialogTitle>重命名</DialogTitle>
    </DialogHeader>
    <div class="space-y-4 py-4">
      <div class="space-y-2">
        <Label for="rename-input" class="text-sm">
          <span class="text-destructive">*</span> 新名称：
        </Label>
        <Input
          id="rename-input"
          v-model="newName"
          placeholder="请输入新名称"
        />
      </div>
    </div>
    <DialogFooter>
      <Button variant="outline" @click="reNameVisible = false">取 消</Button>
      <Button @click="reNameMethod">确 定</Button>
    </DialogFooter>
  </Dialog>


  <el-dialog v-model="dialogTableVisible" title="生成自定义模板" width="36%">
    <div>
      <el-button-group v-model="isAdd" class="button-container">
        <el-button id="generate-template-btn" label="1000" @click="handleGenerateClick()" class="button-container-button" style="width: 50%;text-align: center;">快速生成模板</el-button>
        <el-button id="upload-template-btn" label="1001" @click="handleUploadClick()" class="button-container-button" style="width: 50%;text-align: center;">上传模板文件</el-button>
      </el-button-group>
    </div>
    <div v-if="isFastCreate">
      <el-form v-model="createTemplateFrom">
        <el-form-item style="margin-left: 8%">
          <template #label>
            <span style="color:transparent;">*</span> 模型选择：
          </template>
          <div style="width: 72%">
            <ModelSelector v-model="createTemplateModelId" @manage="openModelManage" />
          </div>
        </el-form-item>
        <el-form-item style="margin-top: 2%;margin-left: 8%">
          <template #label>
            <span style="color:red;">*</span> 文章标题：
          </template>
          <el-input v-model="createTemplateFrom.createTitle" placeholder="请输入文章标题" style="width: 72%" maxlength="20" show-word-limit/>
        </el-form-item>
        <el-form-item style="margin-left: 8%">
          <template #label>
            <span style="color: transparent;">*</span> 模板要求：
          </template>
          <el-input v-model="createTemplateFrom.createNeed" placeholder="请输入模板要求" style="width: 72%"
                    type="textarea"
                    resize="none"
                    :autosize="{ minRows: 3, maxRows: 4 }"
                    maxlength="100" show-word-limit/>
        </el-form-item>
        <el-form-item style="margin-left: 8%">
          <template #label>
            <span style="color:red;">*</span> 模板名称：
          </template>
          <el-input v-model="createTemplateFrom.templateName" placeholder="请输入模板名称" style="width: 72%" maxlength="20" show-word-limit/>
        </el-form-item>
        <el-alert
          v-if="creatingFastTemplate"
          title="模板生成中，请稍候..."
          type="info"
          show-icon
          style="margin: 0 8% 8px 8%; width: 84%"
        />
        <div style="margin-left: 8%; color: #909399; font-size: 12px; width: 84%">
          提交后：系统会生成模板并自动填入左侧“文章标题/大纲”，同时可在“查看全部模板”中查看。
        </div>
      </el-form>
    </div>
    <div v-if="!isFastCreate">
      <el-form-item label="附件：" style="margin-left: 8%" class="upload-container">
        <el-upload
            style="margin-top: 2%;width: 80%;"
            :show-file-list="false"
            drag
            :auto-upload="true"
            :http-request="uploadSolutionFile"
            :before-upload="handleBeforeUpload"
            accept=".pdf,.docx,.txt,.md"
            class="custom-upload-box"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            点击上传，或<em>拖动文档到这里</em>
          </div>
          <template #tip>
            <div style="font-size: 14px;margin-top: 1vh">
              <el-icon style="margin-bottom: 3px;" size="large"><Warning /></el-icon>
              支持 PDF、DOCX、TXT、MD 格式，单个文件尽量不超过 50MB
            </div>
            <div class="demo-progress" v-if="percentage !== 0" style="margin-top: 1vh">
              <img
                  v-if="fileShowName.includes('docx') || fileShowName.includes('doc')"
                  src="./iconPng/file_word.png" alt="PNG Icon" class="file-icon" />
              <img
                  v-if="fileShowName.includes('pdf') || fileShowName.includes('txt') || fileShowName.includes('md')"
                  src="./iconPng/file_pdf.png" alt="PNG Icon" class="file-icon" />
              {{fileShowName}}
              <el-progress  :percentage="percentage" :status="exception"/>
            </div>
          </template>
        </el-upload>
      </el-form-item>

    </div>
    <template #footer>
      <el-button @click="cancelDialog" :disabled="creatingFastTemplate">关 闭</el-button>
      <el-button type="primary" color="#5571FF" v-if="isFastCreate" @click="submit" :loading="creatingFastTemplate" :disabled="!canFastCreateSubmit">提 交 </el-button>
    </template>
  </el-dialog>
  <Dialog v-model="centerDialogVisible" className="max-w-md">
    <DialogHeader>
      <DialogTitle>重命名文件</DialogTitle>
    </DialogHeader>
    <div class="space-y-4 py-4">
      <div class="space-y-2">
        <Label for="new-filename" class="text-sm">
          <span class="text-destructive">*</span> 文件名称：
        </Label>
        <Input
          id="new-filename"
          v-model="newFilename"
          placeholder="请输入文件名称"
          :maxlength="256"
        />
        <p class="text-right text-xs text-muted-foreground">{{ newFilename.length }}/256</p>
      </div>
    </div>
    <DialogFooter>
      <Button variant="outline" @click="centerDialogVisible = false">取 消</Button>
      <Button @click="reFilename">确 定</Button>
    </DialogFooter>
  </Dialog>

  <Dialog v-model="deleteDialogVisible" className="max-w-md">
    <DialogHeader>
      <DialogTitle>是否删除该文件？</DialogTitle>
    </DialogHeader>
    <div class="py-4">
      <p class="text-sm text-muted-foreground">点击删除后文件将彻底删除，不能找回。</p>
    </div>
    <DialogFooter>
      <Button variant="outline" @click="deleteDialogVisible = false">取 消</Button>
      <Button variant="destructive" @click="deleteFile">删 除</Button>
    </DialogFooter>
  </Dialog>
  <Dialog v-model="createTemplateVisible" className="max-w-md">
    <DialogHeader>
      <DialogTitle>模板名称重命名</DialogTitle>
    </DialogHeader>
    <div class="space-y-4 py-4">
      <div class="space-y-2">
        <Label for="template-filename" class="text-sm">
          <span class="text-destructive">*</span> 模板名称：
        </Label>
        <Input
          id="template-filename"
          v-model="newFilename"
          placeholder="请输入模板名称"
        />
      </div>
    </div>
    <DialogFooter>
      <Button variant="outline" @click="createTemplateVisible = false">取 消</Button>
      <Button @click="reFilename">确 定</Button>
    </DialogFooter>
  </Dialog>
</template>
<!--13502707728-->
<script setup>
import {ArrowRightBold,Plus,Refresh,MagicStick, UploadFilled,DocumentAdd,Document,Close,Search,Warning} from '@element-plus/icons-vue'
import TitleInput from '@/pages/web-solution-assistant/components/TitleInput.vue';
import GenerateArticles from '@/pages/web-solution-assistant/components/GenerateArticles.vue';
import RichTextEditor from '@/pages/web-solution-assistant/components/richTextEditor.vue';
import {ref, computed, onMounted,nextTick,onBeforeUnmount,watch, h} from 'vue';
import { ElMessage,ElMessageBox,ElSwitch } from 'element-plus'
import { useUserStore } from '@/store';
import ModelSelector from '@/components/ModelSelector.vue'
import { useModelConfigStore } from '@/store/modules/modelConfig'
import Card from '@/components/ui/Card.vue';
import CardHeader from '@/components/ui/CardHeader.vue';
import CardTitle from '@/components/ui/CardTitle.vue';
import CardContent from '@/components/ui/CardContent.vue';
import Button from '@/components/ui/Button.vue';
import Textarea from '@/components/ui/Textarea.vue';
import Label from '@/components/ui/Label.vue';
import Dialog from '@/components/ui/Dialog.vue';
import DialogHeader from '@/components/ui/DialogHeader.vue';
import DialogTitle from '@/components/ui/DialogTitle.vue';
import DialogFooter from '@/components/ui/DialogFooter.vue';
import Input from '@/components/ui/Input.vue';
import TemplateBuilderDialog from '@/pages/web-solution-assistant/components/TemplateBuilderDialog.vue'
import {
    deleteFileInfo, queryTemplateTitle, getFileList,
    selectWritingTemplateList,
    updateFileName,
    uploadBusiFile, selectTemplateTitle,
    templateRefresh12, createTemplate, templateSave, templateDelete, templateUpdate, createTemplateSelect,
    templateCreate,createTemplateReName,deleteCreateTemplate,usuallyTemplateQuery,allTemplateQuery,templateReName
} from '@/service/api.solution';
// Vue3 组件数据
const instances = ref([{
  firstLevelTitle: '',
  secondLevelTitle: '',
  firstWritingRequirement: '',
  secondWritingRequirement: ''
}]);
const pagination = ref({
    currentPage: 1,
    pageSize: 10,
    total: 0
});
// 创建一个计算属性来处理数组的切片
const slicedData = computed(() => {
    return gridData.value.slice(
        (pagination.value.currentPage - 1) * pagination.value.pageSize,
        pagination.value.currentPage * pagination.value.pageSize
    );
});
const templatePpagination = ref({
    currentPage: 1,
    pageSize: 10,
    total: 0
});
// 创建一个计算属性来处理数组的切片
const templateData = computed(() => {
    return createTemplateData.value.slice(
        (templatePpagination.value.currentPage - 1) * templatePpagination.value.pageSize,
        templatePpagination.value.currentPage * templatePpagination.value.pageSize
    );
});
const templateTitle = ref('');//写作模板标题
const titleData = ref([{titleId:1,children:[]}]);//标题数据集
const dialogTableVisible = ref(false);
const gridData = ref([]);
const multipleSelection = ref([]);//选中的参考文件
const options = ref([]);
const chooseTemplateId = ref('');
const centerDialogVisible = ref(false);
const createTemplateVisible = ref(false);
const deleteDialogVisible = ref(false);
const newFilename = ref('');
const updateFileId = ref('')
const createTemplateId = ref('')
const deleteFileId = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalFileList = ref([])
const selectFiles = ref([])
const generateArticlesRef = ref(null)
const richTextEditorRefs = ref(null)
const uploadFileTableRef = ref(null)
const articleRequirement = ref('') //文章要求
const loading = ref(false)  //生成模板显示loading
const reLoading = ref(false) //刷新模板显示loading
const isCreate = ref(false) //刷新模板显示loading
const isFastCreate = ref(true) //初始选择快速生成
const fastCreateDialogVisible = ref('1000') //初始选择快速生成
const createTitle = ref('')
const createNeed = ref('')
const templateName = ref('')
const showCreateTemplateDialog = ref(false);
const builderVisible = ref(false)
const usuallyTemplateData = ref([])
const tableRef = ref(null);
const tableKey = ref(1);
const createTemplateFrom = ref({
  createTitle: '',
  createNeed: '',
  templateName: ''
});
const creatingFastTemplate = ref(false) // 快速生成模板-提交中状态
const canFastCreateSubmit = computed(() => {
  return !!createTemplateFrom.value.createTitle && !!createTemplateFrom.value.templateName && !creatingFastTemplate.value
})
// 生成模板所选的模型ID
const createTemplateModelId = ref(null)
const open = (res) => {
  const messageBox = ElMessageBox.confirm(
      '模板生成成功',
      {
        confirmButtonText: '立即使用',
        cancelButtonText: '取消',
        type: 'success',
        center: true,
        showClose: false,
        customClass: 'custom-message-box',
        confirmButtonClass: 'custom-confirm-button'
      }
  )
      .then(() => {
        // uploadFiles()
        titleData.value = res.children
        templateTitle.value = res.titleName
        articleRequirement.value = res.writingRequirement
        cancelDialog()
        canclAllTemplate()
        clearInterval(countdownInterval);
      })

  // 倒计时 3 秒
  let countdown = 3;
  const countdownInterval = setInterval(() => {
    if (countdown > 0) {
      // 更新取消按钮文本
        const cancelButton = document.querySelector('.custom-message-box').querySelector('.el-message-box__btns').querySelector('.el-button');
      console.log(cancelButton)
      if (cancelButton) {
        cancelButton.textContent = `返回(${countdown})`; // 显示倒计时
      }
      countdown--;
    } else {
      // 清除倒计时
      clearInterval(countdownInterval);
      // 关闭消息框
      ElMessageBox.close();
    }
  }, 1000);
}
const isRowSelectable = (row) => {
  if (row.status_cd == '1') {
    return true
  }else{
    return false
  }
}
const handleSizeChange = (val) => {
    if(isFastCreate.value){
        templatePpagination.value.pageSize = val;
        templatePpagination.value.currentPage = 1;
    }else {
        pagination.value.pageSize = val;
        pagination.value.currentPage = 1;
    }

}
const handleCurrentChange = (val) => {
    if(isFastCreate.value){
        templatePpagination.value.currentPage = val;
    }else {
        pagination.value.currentPage = val;
    }

}

onMounted(() => {
    selectTemplateList();
    loadLeftTemplates()
    // 可选：预取模型列表与默认模型
    const modelStore = useModelConfigStore();
    modelStore.fetchList();
    // 初始化生成模板用的模型选择为当前或默认
    if (!createTemplateModelId.value && modelStore.currentOrFirst) {
      createTemplateModelId.value = modelStore.currentOrFirst
    }
});
// 当模型列表或当前选择变化时，同步到生成模板对话框
watch(() => useModelConfigStore().currentOrFirst, (val) => {
  if (!createTemplateModelId.value && val) {
    createTemplateModelId.value = val
  }
})
const selectTemplateList = () => {
    const userStore = useUserStore();
    const parma ={
        "userId": userStore.profile.mobile,
    }
    selectWritingTemplateList(parma).then(res => {
        options.value = res.data
    }).catch(error => {
        ElMessage.error('请求失败:'+error);
    })
};
const tableRowClassName = ({ row, rowIndex }) => {//给每行数据添加索引，防止在一些row没有INDEX字段时多选出现问题
  row.INDEX = rowIndex;
};
const handleRadioChange = (val) => {//单选
  selectRowData.value = val
};
const handleSelectionChange = (val) => {//多选
  if(val.length>1){
    uploadFileTableRef.value.toggleRowSelection(val[0], false);
  }
  multipleSelection.value = val.slice(-1);
};

const statusCds = (row, column, cellValue) => {
  if (cellValue === '0') {
    return '正在解析'
  } else if (cellValue === '1') {
    return '解析完成'
  }else{
    return '解析失败'
  }
};
const createTemplateData = ref('')
const queryCreateTemplate = () => {
    const selectParam = {
        "userId": userStore.profile.mobile,
        "pageNum": 1,
        "pageSize": 10000
    }
    createTemplateSelect(selectParam).then(res => {
        console.log("查询模板成功：",res)
        createTemplateData.value = res.data.data.templateList
        templatePpagination.value.total = res.data.data.templateCount
    }).catch(error => {
        ElMessage.error('查询模板失败:'+error);
    }).finally(() => {

    })
}
// 定义获取行唯一键的方法
const getRowKey = (row) => row.template_id;
const search = ref('')
const leftFilterType = ref('all')
const filteredLeftList = computed(() => {
    let data = Array.isArray(usuallyTemplateData.value) ? [...usuallyTemplateData.value] : []
    if (leftFilterType.value !== 'all') {
        data = data.filter(item => String(item.type || 1) === leftFilterType.value)
    }
    const q = (search.value || '').toLowerCase()
    if (q) {
        data = data.filter(item => (item.template_name || '').toLowerCase().includes(q))
    }
    return data
})
const loadLeftTemplates = () => {
    const parmas = {
        userId: userStore.profile.mobile,
        templateTitle: ''
    }
    allTemplateQuery(parmas).then(res => {
        tableKey.value += 1
        usuallyTemplateData.value = res.data.data || []
    }).catch(error => {
        ElMessage.error('查询模板失败:'+ error);
    })
}
const createSolutionTemplate = () => {
  const modelStore = useModelConfigStore();
  if (!createTemplateModelId.value && !modelStore.currentOrFirst) {
    ElMessage.error('请先在模型配置中添加或选择一个模型');
    return;
  }
  if(templateName.value ==''){
      ElMessage.error('请输入模板名称')
      return
  }
  showCreateTemplateDialog.value = false
    ElMessage({
        message: '正在生成模板，请稍后...',
        type: 'success',
    })
    const param = {
        "titleName": createTitle.value,
        "writingRequirement": createNeed.value,
        "userId": userStore.profile.mobile,
        "templateName": templateName.value,
        "modelId": createTemplateModelId.value || modelStore.currentOrFirst
    }
    templateCreate(param).then(res => {
        createTitle.value = ''
        createNeed.value = ''
        templateName.value = ''
        ElMessage({
            message: '模板生成成功.',
            type: 'success',
        })
        queryCreateTemplate()
    }).catch(error => {
        console.log("重命名失败：" + error)
        queryCreateTemplate()
    })
}
const createTemplateHandle = () => {
    if(createTitle.value == ''){
        ElMessage.error('请输入模板名称')
        return
    }
    showCreateTemplateDialog.value = true
}
const cancelCreate = () => {
    showCreateTemplateDialog.value = false
    templateName.value = ''
}
// 监听 dialogTableVisible 变化
watch(dialogTableVisible, (newValue) => {
  if (!newValue) {
    cancelDialog();
    clearInterval(intervalId.value);
  }
});
const cancelDialog = () => {
    dialogTableVisible.value = false
  createTemplateFrom.value = {
      createTitle: '',
      createNeed: '',
      templateName: ''
  }
  percentage.value = 0
  fileShowName.value = ''
  handleGenerateClick()
}
watch(dialogTableVisible, (newValue, oldValue) => {
    if (newValue === false) {
        if (timerID.value) {
            clearInterval(timerID.value);
            timerID.value = null;
        }
    }
});
const selectTemplate = () => { //选定按钮
    if(!isFastCreate.value){
        selectFiles.value = multipleSelection.value
        reLoading.value = true
        const selectParam = {
            "file_id": selectFiles.value[0].file_id,
        }
        selectTemplateTitle(selectParam).then(res => {
            console.log("查询模板成功：",JSON.parse(res.data.data[0].title_data))
            if(JSON.parse(res.data.data[0].title_data).data){
                titleData.value = JSON.parse(res.data.data[0].title_data).data.children
                templateTitle.value = JSON.parse(res.data.data[0].title_data).data.titleName
                articleRequirement.value = JSON.parse(res.data.data[0].title_data).data.writingRequirement

            }else{
                titleData.value = JSON.parse(res.data.data[0].title_data).children
                templateTitle.value = JSON.parse(res.data.data[0].title_data).titleName
                articleRequirement.value = JSON.parse(res.data.data[0].title_data).writingRequirement
            }
        }).catch(error => {
            ElMessage.error('查询模板失败:'+error);
        }).finally(() => {
            reLoading.value = false
        })
    }else {
        reLoading.value = true
        createTitle.value = ''
        createNeed.value = ''
        console.log('selectTemplateData',multipleSelection.value)
        templateTitle.value = JSON.parse(multipleSelection.value[0].create_template).titleName
        articleRequirement.value = JSON.parse(multipleSelection.value[0].create_template).writingRequirement
        titleData.value = JSON.parse(multipleSelection.value[0].create_template).children
        reLoading.value = false
    }
    dialogTableVisible.value = false
    selectTemplateInfo.value = ''
    tableRef.value?.setCurrentRow(null);
};

const deleteSelectedFile = (index) => {
  selectFiles.value.splice(index,1)

};

const uploadFiles = () => {
  dialogTableVisible.value = true
    templateName.value =''
  setTimeout(()=>{
    document.getElementById('generate-template-btn').style.backgroundColor = '#FFFFFF';
    document.getElementById('generate-template-btn').style.color = '#5D78FF';
    document.getElementById('generate-template-btn').style.fontWeight = 'bold';
  },100)

};
const openBuilder = () => { builderVisible.value = true }
let messageShown = false;
const selectFileList = (file_id) => {//查询文件列表
  const userStore = useUserStore();
  const selectParam = {
    "busiId": userStore.profile.mobile,
    "pageNum": 1,
    "pageSize": 10000
  }
  getFileList(selectParam).then(res => {
    for(let i=0 ; i<res.data.fileList.length; i++){
      if(res.data.fileList[i].file_id === file_id){
        console.log("已找到匹配文件：",res.data.fileList[i])
          if(res.data.fileList[i].status_cd === '1'){
            ElMessage.success('文件解析成功')
            clearInterval(timerID.value);
            open(JSON.parse(res.data.fileList[i].title_data))
            return
          }else if(res.data.fileList[i].status_cd === '2'){
            ElMessage.error('文件解析失败')
            clearInterval(timerID.value);
            return
          }
      }
    }
    // gridData.value = res.data.fileList
    // pagination.value.total = res.data.fileCount
    // let string = selectFiles.value.map(item => item.file_id);
    // nextTick(() => {
    //   gridData.value.forEach(item=>{
    //       if(file_id && !messageShown){
    //           if(item.file_id === file_id){
    //               if(item.status_cd === '1'){
    //                   ElMessage.success('文件解析成功')
    //                   messageShown = true;
    //               }else if(item.status_cd === '2'){
    //                   ElMessage.error('文件解析失败')
    //                   messageShown = true;
    //               }
    //           }
    //       }
    //     uploadFileTableRef.value && uploadFileTableRef.value.toggleRowSelection(item,false);
    //     if(string.includes(item.file_id)){
    //       uploadFileTableRef.value && uploadFileTableRef.value.toggleRowSelection(item,true);
    //     }
    //   })
    // })
  }).catch(error => {
   ElMessage.error('请求失败:'+error);
  })
};
const submit = () => {
  if(isFastCreate.value){

    ElMessageBox.confirm('是否确认提交?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success',
      confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(() => {
      const modelStore = useModelConfigStore();
      if (!createTemplateModelId.value && !modelStore.currentOrFirst) {
        ElMessage.error('请先在模型配置中添加或选择一个模型');
        return;
      }
      creatingFastTemplate.value = true
      ElMessage({
        message: '模板正在生成，请稍后...',
        type: 'success',
      })
      console.log('selectTemplateData',createTemplateFrom.value)
      console.log('selectTemplateData',createTemplateFrom.value.createTitle)
      const param = {
        "titleName": createTemplateFrom.value.createTitle,
        "writingRequirement": createTemplateFrom.value.createNeed,
        "userId": userStore.profile.mobile,
        "templateName": createTemplateFrom.value.templateName,
        "modelId": createTemplateModelId.value || modelStore.currentOrFirst
      }
      templateCreate(param).then(res => {
        open(res.data.data)
      })
      .finally(() => {
        creatingFastTemplate.value = false
        cancelDialog()
      })

    }).catch(() => {
      ElMessage({
        type: 'info',
        message: '取消成功'
      });
    })

  }else {

  }
  // dialogTableVisible.value = false

}
const handleGenerateClick = () => {
  isFastCreate.value = true
  document.getElementById('generate-template-btn').style.backgroundColor = '#FFFFFF';
  document.getElementById('generate-template-btn').style.color = '#5D78FF';
  document.getElementById('generate-template-btn').style.fontWeight = 'bold';
  document.getElementById('upload-template-btn').style.backgroundColor = '#f5f5f5';
  document.getElementById('upload-template-btn').style.color = '#333333';
  document.getElementById('upload-template-btn').style.fontWeight = '';

}
const handleUploadClick = () => {
  isFastCreate.value = false
  document.getElementById('generate-template-btn').style.backgroundColor = '#f5f5f5';
  document.getElementById('generate-template-btn').style.color = '#333333';
  document.getElementById('generate-template-btn').style.fontWeight = '';
  document.getElementById('upload-template-btn').style.backgroundColor = '#FFFFFF';
  document.getElementById('upload-template-btn').style.color = '#5D78FF';
  document.getElementById('upload-template-btn').style.fontWeight = 'bold';
}
const selectOneTemplate = () => {
  if(!selectRowData.value){
    ElMessage.error('请选择模板')
    return
  }
  console.log('selectOneTemplateData',selectRowData.value)
  // type 1:内置模板及自定义模板 2:文件模板 3:ai生成模板
  if (selectRowData.value.row.type === 1){
    reLoading.value = true
    const selectParam = {
      "templateId": selectRowData.value.row.template_id
    }
    queryTemplateTitle(selectParam).then(res => {
      console.log("查询模板返回结果：",res.data)
      titleData.value = res.data
      if (res.data.length>0 && res.data[0].children){
        titleData.value = res.data[0].children
        articleRequirement.value = res.data[0].writingRequirement
        templateTitle.value = res.data[0].titleName
      }
    }).catch(error => {
      ElMessage.error('请求失败:'+error);
    }).finally(() => {
      reLoading.value = false
    })
  }else if (selectRowData.value.row.type === 2){
    if(selectRowData.value.row.status_cd === '0'){
      ElMessage.error('该文件正在解析中，请稍后...')
      return
    }
    if(selectRowData.value.row.status_cd === '2'){
      ElMessage.error('该文件解析失败，请重新上传解析')
      return
    }
    reLoading.value = true
    if(JSON.parse(selectRowData.value.row.title_data).data){
      titleData.value = JSON.parse(selectRowData.value.row.title_data).data.children
      templateTitle.value = JSON.parse(selectRowData.value.row.title_data).data.titleName
      articleRequirement.value = JSON.parse(selectRowData.value.row.title_data).data.writingRequirement

    }else{
      titleData.value = JSON.parse(selectRowData.value.row.title_data).children
      templateTitle.value = JSON.parse(selectRowData.value.row.title_data).titleName
      articleRequirement.value = JSON.parse(selectRowData.value.row.title_data).writingRequirement
    }
    reLoading.value = false
  }else if (selectRowData.value.row.type === 3){
    reLoading.value = true
    templateTitle.value = JSON.parse(selectRowData.value.row.create_template).titleName
    articleRequirement.value = JSON.parse(selectRowData.value.row.create_template).writingRequirement
    titleData.value = JSON.parse(selectRowData.value.row.create_template).children
    reLoading.value = false
  }
  // 选定后关闭模板库，同时确保其他来源的弹窗一并关闭
  showTemplateDialog.value = false
  closeAllTransientModals()
}
const canclAllTemplate = () => {
  showTemplateDialog.value = false
  searchTemplateName.value = ''
}
const reNameMethod = () => {
  // type 1:内置模板及自定义模板 2:文件模板 3:ai生成模板
  if(selectRowData.value.type === 1){
    const param = {
      "id": selectRowData.value.template_id,
      "template_name": newName.value
    }
    templateReName(param).then(res => {
      ElMessage({
        message: '模板重命名成功.',
        type: 'success',
      })
    })
  }else if(selectRowData.value.type === 2){
    const param = {
      "file_id": selectRowData.value.file_id,
      "file_name": newName.value
    }
    updateFileName(param).then(res => {
      ElMessage({
        message: '文件重命名成功.',
        type: 'success',
      })
    })
  }else if(selectRowData.value.type === 3){
    const param = {
      "id": selectRowData.value.id,
      "template_name": newName.value
    }
    createTemplateReName(param).then(res => {
      ElMessage({
        message: '模板重命名成功.',
        type: 'success',
      })
    })
  }
  queryAllTemplate()
  newName.value = ''
  selectRowData.value = ''
  reNameVisible.value = false
}
const selectRowData = ref('')
const reNameVisible = ref(false)
const newName = ref('')
const reNameHandleClick = (row) => {
  if (row.template_id >= 1 && row.template_id <= 10) {
    ElMessage.warning('禁止重命名公用模板')
    return
  }
  // 改为使用 Prompt，避免多层弹窗无反应
  ElMessageBox.prompt('请输入新名称', '重命名', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: row.template_name,
  }).then(({ value }) => {
    const newVal = (value || '').trim()
    if (!newVal) { ElMessage.error('名称不能为空'); return }
    if (row.type === 1 || row.type === undefined) {
      templateReName({ id: row.template_id, template_name: newVal }).then(() => {
        ElMessage.success('模板重命名成功')
        queryAllTemplate(); loadLeftTemplates()
      })
    } else if (row.type === 2) {
      updateFileName({ file_id: row.file_id, file_name: newVal }).then(() => {
        ElMessage.success('文件重命名成功')
        queryAllTemplate(); loadLeftTemplates()
      })
    } else if (row.type === 3) {
      createTemplateReName({ id: row.id, template_name: newVal }).then(() => {
        ElMessage.success('模板重命名成功')
        queryAllTemplate(); loadLeftTemplates()
      })
    }
  }).catch(() => {})
};
const deleteAllHandleClick = (row) => {
  console.log('row',row)
  if (row.template_id >= 1 && row.template_id <= 10) {
    ElMessage.warning('禁止删除公用模板')
    return
  }
  // type 1:内置模板及自定义模板 2:文件模板 3:ai生成模板
  ElMessageBox.confirm('是否确认删除该模板?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    confirmButtonClass: 'my-confirmButtonClass-class',
  }).then(() => {
    if(row.type === 1){
      const parmas ={
        "userId": userStore.profile.mobile,
        "templateId": row.template_id.toString(),
      }
      templateDelete(parmas).then(res => {
        ElMessage.success('删除模板成功');
      }).catch(error => {
        ElMessage.error('请求失败:'+error);
      }).finally(()=>{
        queryAllTemplate()
      });
    }else if(row.type === 2){
      const param = {
        "file_id": row.file_id
      }
      deleteFileInfo(param).then(res => {
        ElMessage({
          message: '删除成功.',
          type: 'success',
        })
      }).catch(error => {
        ElMessage.error('请求失败:'+error);
      }).finally(()=>{
        queryAllTemplate()
      });
    }else if(row.type === 3){
      const param = {
        "id": row.id
      }
      deleteCreateTemplate(param).then(res => {
        ElMessage({
          message: '删除成功.',
          type: 'success',
        })
      }).catch(error => {
        ElMessage.error('请求失败:'+error);
      }).finally(()=>{
        queryAllTemplate()
      });
    }
  }).catch(() => {
    ElMessage({
      type: 'info',
      message: '取消成功'
    });
  })

};
const reFilenameHandleClick = (row) => {
    newFilename.value=''
    if(isFastCreate.value){
        createTemplateVisible.value = true
        createTemplateId.value = row.id
    }else {
        centerDialogVisible.value = true
        updateFileId.value = row.file_id

    }

};

const reFilename = () => {//文件重命名
  if (newFilename.value !== '') {
      if(isFastCreate.value){
          const param = {
              "id": createTemplateId.value,
              "template_name": newFilename.value
          }
          createTemplateReName(param).then(res => {
              createTemplateId.value = ''
              createTemplateVisible.value = false
              ElMessage({
                  message: '模板重命名成功.',
                  type: 'success',
              })
              queryCreateTemplate()
          }).catch(error => {
              console.log("重命名失败：" + error)
              queryCreateTemplate()
          })

      }else {
          const param = {
              "file_id": updateFileId.value,
              "file_name": newFilename.value
          }
          updateFileName(param).then(res => {
              updateFileId.value = ''
              centerDialogVisible.value = false
              ElMessage({
                  message: '文件重命名成功.',
                  type: 'success',
              })
              selectFileList()
          }).catch(error => {
              console.log("重命名失败：" + error)
              selectFileList()
          })

      }
  } else ElMessage.error('错误，文件名不能为空.')
};

const deleteHandleClick = (row) => {
    if(isFastCreate.value){
        ElMessageBox.confirm('是否确认删除模板?', '确认提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          confirmButtonClass: 'my-confirmButtonClass-class',
        }).then(() => {
            const param = {
                "id": row.id
            }
            deleteCreateTemplate(param).then(res => {
                console.log("删除成功：",res)
                ElMessage({
                    message: '删除成功.',
                    type: 'success',
                })
            }).catch(error => {
                console.log("删除失败：" + error)
            }).finally(() => {
                queryCreateTemplate()
            })

        })

    }else {
        deleteDialogVisible.value = true
        deleteFileId.value = row.file_id
    }


};

const deleteFile = () => {//删除文件
        const param = {
            "file_id": deleteFileId.value
        }
        deleteFileInfo(param).then(res => {
            deleteFileId.value=''
            deleteDialogVisible.value = false
            ElMessage({
                message: '删除成功.',
                type: 'success',
            })
            selectFileList()
        }).catch(error => {
            ElMessage.error('请求失败:'+error);
            selectFileList()
        })

};
const pauseCreate = () => {
    ElMessageBox.confirm('是否确认暂停?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(() => {
      // 子组件通过 defineExpose 暴露了 isCreate/isPause（ref），此处需访问其 .value
      if (richTextEditorRefs.value) {
        if (richTextEditorRefs.value.isCreate) richTextEditorRefs.value.isCreate.value = false
        if (richTextEditorRefs.value.isPause) richTextEditorRefs.value.isPause.value = true
      }
        isCreate.value=!isCreate.value
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    });

}
const createArticle = () => {  //调用生成文章接口
  const modelStore = useModelConfigStore();
  if (!modelStore.currentOrFirst) {
    ElMessage.error('请先在模型配置中添加或选择一个模型');
    return;
  }
  if(templateTitle.value === ""){
    ElMessage.error('请先输入文章标题');
    return
  }
  console.log("模板大纲数据：",titleData.value)
  if(titleData.value.length === 0){
    ElMessage.error('请至少输入一个一级标题');
    return
  }
    let hasTitleName = false; // 用于标记是否至少有一个 titleName 存在
    for (let i = 0; i < titleData.value.length; i++) {
        // 假设 titleData.value[i] 有一个属性 titleName
        if (titleData.value[i].titleName) {
            hasTitleName = true; // 如果找到一个 titleName，将标记设置为 true
            break; // 并退出循环
        }
    }
    if (!hasTitleName) {
        ElMessage.error('请至少输入一个一级标题');
        return;
    }
    ElMessageBox.confirm('是否确认生成文章?', '确认提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(() => {
        isCreate.value=!isCreate.value
        // var div1 = document.getElementById('tips');
        // div1.style.display = "none";
        const parameter = {
                "titleId": 0,
                "templateId": 0,
                "parentId": 0,
            "titleName": templateTitle.value,
            "showOrder": 0,
            "writingRequirement": articleRequirement.value,
            "statusCd": "Y",
            "children": titleData.value

        }
        // 兼容不同来源的模板：
        // - 自定义/内置模板: template_id
        // - AI 生成模板: id
        // - 文件模板: 无模板 id，仅传 null
        const rawTplId = selectTemplateInfo.value?.template_id ?? selectTemplateInfo.value?.id ?? null
        const templateTitleParam1 = {
            "outline": parameter,
            "templateId": rawTplId != null ? String(rawTplId) : null,
            "userId": userStore.profile.mobile
        }
        // generateArticlesRef.value.createArticle(templateTitleParam1)
        richTextEditorRefs.value.createArticle(templateTitleParam1)
    })

};

const currentModelId = ref(null)
const openModelManage = () => {
  // 预留：可跳转到模型管理页，当前项目未配置导航体系，这里先提示
  ElMessage.info('请前往模型配置管理页添加模型（待接入导航）')
}
const handleRequestComplete = (content) => {
    console.log('请求完成，内容：', content);
    isCreate.value = false
    // 处理完成逻辑
};

const handleRequestError = (error) => {
    console.log('请求出错：', error);
    isCreate.value = false
    // 处理错误逻辑
};
const handleClear = () => {
    articleRequirement.value = ''
};

// 新版对话框回填与跳转
const handleAppliedTemplate = (tpl) => {
  templateTitle.value = tpl.titleName || ''
  articleRequirement.value = tpl.writingRequirement || ''
  titleData.value = tpl.children || []
  // 打开全屏大纲编辑弹窗，复用编辑体验
  showOutlineFullscreen.value = true
}
// 统一关闭其他弹窗，避免库弹窗叠在生成弹窗之上
const closeAllTransientModals = () => {
  builderVisible.value = false
  dialogTableVisible.value = false
  showCreateTemplateDialog.value = false
  showSaveTemplateDialog.value = false
  reNameVisible.value = false
  centerDialogVisible.value = false
  createTemplateVisible.value = false
  deleteDialogVisible.value = false
}
const openLibraryFromResult = () => {
  closeAllTransientModals()
  lookTemplateDialog()
}

// 监听 search 值的变化
watch(search, () => {
    // 在搜索时保持当前选中行的状态
    if (selectTemplateInfo.value) {
        nextTick(() => {
            tableRef.value?.setCurrentRow(selectTemplateInfo.value);
        });
    }
});
const selectTemplateInfo = ref('')
const chooseTemplateFun = (row) => { // 左侧选择模板，按 type 分流
    if (!row) return
    titleData.value = ''
    selectTemplateInfo.value = row
    reLoading.value = true
    const type = row.type
    if (type === 1 || type === undefined) {
      const selectParam = { "templateId": row.template_id }
      queryTemplateTitle(selectParam).then(res => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          const first = res.data[0]
          titleData.value = first.children || []
          articleRequirement.value = first.writingRequirement || ''
          templateTitle.value = first.titleName || ''
        }
      }).catch(error => {
        ElMessage.error('请求失败:'+error)
      }).finally(() => { reLoading.value = false })
    } else if (type === 2) {
      if (row.status_cd === '0') { ElMessage.error('该文件正在解析中，请稍后...'); reLoading.value = false; return }
      if (row.status_cd === '2') { ElMessage.error('该文件解析失败，请重新上传解析'); reLoading.value = false; return }
      try {
        const parsed = JSON.parse(row.title_data)
        const data = parsed.data || parsed
        titleData.value = data.children || []
        templateTitle.value = data.titleName || ''
        articleRequirement.value = data.writingRequirement || ''
      } catch (e) {
        ElMessage.error('文件模板数据异常')
      } finally { reLoading.value = false }
    } else if (type === 3) {
      try {
        const data = JSON.parse(row.create_template)
        titleData.value = data.children || []
        templateTitle.value = data.titleName || ''
        articleRequirement.value = data.writingRequirement || ''
      } catch (e) {
        ElMessage.error('AI模板数据异常')
      } finally { reLoading.value = false }
    } else {
      reLoading.value = false
    }
};
const transformData = (data) => {
    const result = {};

    const processItem = (item) => {
        // 初始化当前级别的结果对象
        const currentResult = {};
        if (item.children && item.children.length > 0) {
            // 如果存在子标题，递归处理每个子标题
            item.children.forEach(child => {
                const childResult = processItem(child); // 递归调用处理子标题
                if (childResult) {
                    currentResult[child.titleName] = childResult;
                }
            });
        } else {
            // 如果没有子标题，直接设置写作要求
            currentResult[item.titleName] = item.writingRequirement || '';
        }
        return currentResult;
    };

    data.forEach(item => {
        const itemResult = processItem(item);
        if (Object.keys(itemResult).length > 0) {
            result[item.titleName] = itemResult;
        }
    });

    return result;
};
// 获取定时器的ID，以便之后可以清除它

const timerID = ref(null);
const intervalId = ref(null);
const exception = ref('');
const uploadSolutionFile = (content) => {//上传文件
    messageShown = false
  percentage.value = 0
  const userStore = useUserStore();
  const formData = new FormData()
  exception.value = ''
  formData.append('file', content.file);
  formData.append('createNo', userStore.profile.mobile);
  formData.append('createName', userStore.profile.name);
    // 在设置新的定时器之前，清除之前的定时器
    if (timerID.value) {
        clearInterval(timerID.value);
    }
  intervalId.value = setInterval(() => {
    if (percentage.value < 99) {
      percentage.value = (percentage.value % 100) + 1;
    } else {
      // 当percentage达到100时，停止定时器
      clearInterval(intervalId.value);
    }
    if(percentage.value == 100){
      exception.value = 'success'
    }
  }, 10);
  uploadBusiFile(formData).then(res => {
    percentage.value = 100
      timerID.value = setInterval(() => {
          selectFileList(res.data.data.file_id);
      }, 2000)
      if(res.data.code == 400){
          ElMessage.warning(res.data.message);
      }else ElMessage.success('上传文件成功,文件正在解析，请稍后');
  }).catch(error => {
    clearInterval(intervalId.value)
    exception.value = 'exception'
    console.log('上传文件失败:' + error)
      if (error.response) {
          switch (error.response.status) {
              case 413:
                  ElMessage.error('文件过大，请上传小于限制的文件')
                  break
              case 415:
                  ElMessage.error('不支持的文件类型')
                  break
              default:
                  ElMessage.error(`上传失败: ${error.response.data?.message || '请重试'}`)
          }
      } else if (error.code === 'ERR_NETWORK') {
          ElMessage.error('网络异常或后端未响应，请稍后重试')
      } else {
          ElMessage.error('上传出错，请重试')
      }
  })
};
const format = (percentage) => {
  return percentage === 100 ? '上传成功' : `${percentage}%`;
};
const uploadPercentage = ref(0);
const fileList = ref([]);
const fileShowName = ref('');
const percentage = ref(0);
const handleBeforeUpload = (file) => {
  if (file.size === 0){
    ElMessage.error("不能上传空文件");
    return false;

  }
  const maxSize = 50 * 1024 * 1024; // 50MB（前端放宽，后端按字符截断）
  if (file.size > maxSize) {
    ElMessage.error(`文件太大，不能超过 ${maxSize / 1024 / 1024}MB.`);
    return false;
  }

  // 检查文件的扩展名
  const fileName = file.name;
  fileShowName.value = fileName;
  const fileType = fileName.substring(fileName.lastIndexOf('.') + 1);
  const allowedTypes = ['pdf', 'docx', 'txt', 'md'];

  if (!allowedTypes.includes(fileType.toLowerCase())) {
    ElMessage.error('只能上传 PDF、DOCX、TXT 或 MD 文件!');
    return false;
  }
  // 如果文件类型检查通过，可以继续上传
  return true;
};
const userStore = useUserStore();
const templateRefresh = () => {
    if(templateTitle.value === ""){
        ElMessage.error('请先输入文章标题');
        return
    }
    ElMessageBox.confirm('是否确认刷新模板?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(() => {
        reLoading.value = true
        const parameter = [{
            "titleName": templateTitle.value,
            "writingRequirement": articleRequirement.value,
            "children": titleData.value
        }]
        const templateRefreshParam1 = {
            "titleName": templateTitle.value,
            "writingRequirement": articleRequirement.value,
            "originalTemplate": parameter
        }
        console.log("刷新模板参数：",templateRefreshParam1)
        titleData.value = ''
        templateRefresh12(templateRefreshParam1).then(res => {
            console.log("刷新模板返回结果：",res.data.data.data)
            templateTitle.value = res.data.data.data.titleName
            articleRequirement.value = res.data.data.data.writingRequirement
            titleData.value = res.data.data.data.children
            ElMessage({
                message: '刷新写作模板成功.',
                type: 'success',
            })
        }).catch(error => {
            ElMessage.error('模板刷新失败:'+error);
        }).finally(() => {
            reLoading.value = false
        });
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    });
}

const createTemplateClick = () => {
    if(templateTitle.value === ""){
        ElMessage.error('请先输入文章标题');
        return
    }
    ElMessageBox.confirm('是否确认根据标题和要求生成模板?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(() => {
        loading.value = true
        titleData.value = ''
        const createTemplateParam = {
            "titleName": templateTitle.value,
            "writingRequirement": articleRequirement.value
        }
        console.log("生成模板按钮所需传递参数：",createTemplateParam)
        createTemplate(createTemplateParam).then(res => {
            titleData.value = res.data.data.data.children
            ElMessage({
                message: '生成写作模板成功.',
                type: 'success',
            })
        }).catch(error => {
            ElMessage.error('请求失败:'+error);
        }).finally(() => {
            loading.value = false
        });
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    })


}
const deleteTemplate = (row) => {
    ElMessageBox.confirm('是否确认删除该模板?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      confirmButtonClass: 'my-confirmButtonClass-class',
    }).then(() => {
        const parmas ={
            "userId": userStore.profile.mobile,
            "templateId": row.template_id.toString(),
        }
        templateDelete(parmas).then(res => {
            ElMessage.success('删除模板成功');
            loadLeftTemplates()
        }).catch(error => {
            ElMessage.error('请求失败:'+error);
        })
    }).catch(() => {
        ElMessage({
            type: 'info',
            message: '取消成功'
        });
    });
}
const showSaveTemplateDialog = ref(false);
const showSaveTemplate = ref(false);

const isAdd = ref('');
const saveTemplateDialog=()=>{
    if(templateTitle.value === ""){
        ElMessage.error('请先输入文章标题');
        return
    }
    if(titleData.value.length === 0){
        ElMessage.error('请先输入一级标题');
        return
    }

    // 根据当前选中的模板类型决定交互
    const row = selectTemplateInfo.value
    const canOverride = row && (row.type === 1 || row.type === undefined) && row.user_id !== '0'
    showSaveTemplate.value = !!canOverride
    if (canOverride) {
      isAdd.value = '1001'
      templateName.value = row.template_name || templateTitle.value
    } else {
      isAdd.value = '1000'
      templateName.value = templateTitle.value + '（自定义）'
    }
    showSaveTemplateDialog.value = true
}
const showTemplateDialog = ref(false);
const selectRadio = ref('');
const lookTemplateDialog=()=>{
  closeAllTransientModals()
  queryAllTemplate()
  showTemplateDialog.value = true
}
const allTemplateList = ref('');
const searchTemplateName = ref('');
const queryAllTemplate = () => {
  const parmas = {
    "userId": userStore.profile.mobile,
    "templateTitle": searchTemplateName.value,
  }
  allTemplateQuery(parmas).then(res => {
    console.log("查询模板列表：",res)
    allTemplateList.value = res.data.data
    pagination.value.total = res.data.total_count
    }).catch(error => {
        ElMessage.error('请求失败:'+error);
    })
}
// 创建一个计算属性来处理数组的切片
const allTemplateData = computed(() => {
  return allTemplateList.value.slice(
      (pagination.value.currentPage - 1) * pagination.value.pageSize,
      pagination.value.currentPage * pagination.value.pageSize
  );
});
const resetForm = () => {
  searchTemplateName.value = '';
  queryAllTemplate()
}
const cancelSave = () => {
    showSaveTemplateDialog.value = false;
    isAdd.value =''
}
const saveTemplate=()=>{
    // 仅校验写作模板（type=1）的重名，避免与文件/AI模板混淆
    if ((usuallyTemplateData.value || []).some(it => (it.type === 1 || it.type === undefined) && it.template_name === templateName.value)) {
        ElMessage.error('该模板名称已存在，请重新输入');
        return
    }
    showSaveTemplateDialog.value = false
    if(isAdd.value === '1000'){
        const parameter = {
            "titleName": templateTitle.value,
            "writingRequirement": articleRequirement.value,
            "children": titleData.value
        }
        const saveTemplateParam = {
            "userId": userStore.profile.mobile,
            "titleName": templateName.value,
            "writingRequirement": articleRequirement.value,
            "originalTemplate": [parameter]
        }

        templateSave(saveTemplateParam).then(res => {
            ElMessage.success('模板保存成功');
            loadLeftTemplates()
        })
    }else if(isAdd.value === '1001'){
        const parameter = {
            "titleName": templateTitle.value,
            "writingRequirement": articleRequirement.value,
            "children": titleData.value
        }
        const saveTemplateParam = {
            "userId": userStore.profile.mobile,
            "templateId": selectTemplateInfo.value.template_id.toString(),
            "titleName": templateName.value,
            "writingRequirement": articleRequirement.value,
            "originalTemplate": [parameter]
        }

        templateUpdate(saveTemplateParam).then(res => {
            ElMessage.success('模板修改成功');
            showSaveTemplateDialog.value = false
            loadLeftTemplates()
        })
    }else {
        const parameter = {
            "titleName": templateTitle.value,
            "writingRequirement": articleRequirement.value,
            "children": titleData.value
        }
        const saveTemplateParam = {
            "userId": userStore.profile.mobile,
            "titleName": templateName.value,
            "writingRequirement": articleRequirement.value  ,
            "originalTemplate": [parameter]
        }
        console.log("saveTemplateParam",saveTemplateParam)
        templateSave(saveTemplateParam).then(res => {
            ElMessage.success('模板保存成功');
            loadLeftTemplates()
        })
    }



}
// Vue3 生命周期：组件卸载前执行清理
onBeforeUnmount(() => {
    console.log("页面卸载");
    isCreate.value=!isCreate.value
    if (richTextEditorRefs.value) {
        richTextEditorRefs.value.isPause = true
    }
});

// 全屏大纲编辑弹窗状态与确认
const showOutlineFullscreen = ref(false)
const confirmOutlineFromFullscreen = () => {
  // 直接复用同一个响应式对象，已与左侧表单联动
  showOutlineFullscreen.value = false
  ElMessage.success('已应用全屏编辑的大纲')
}

// 目录树与搜索
const outlineSearch = ref('')
const outlineToTree = (data) => {
  return (data || []).map((n1, i1) => ({
    id: n1.titleId ?? i1,
    name: n1.titleName,
    children: (n1.children || []).map((n2, i2) => ({
      id: n2.titleId ?? `${i1}-${i2}`,
      name: n2.titleName,
      children: (n2.children || []).map((n3, i3) => ({
        id: n3.titleId ?? `${i1}-${i2}-${i3}`,
        name: n3.titleName,
      })),
    })),
  }))
}
const filteredOutline = computed(() => {
  const q = outlineSearch.value?.trim().toLowerCase()
  const tree = outlineToTree(titleData.value)
  if (!q) return tree
  const match = (node) => (node.name || '').toLowerCase().includes(q)
  const dfs = (nodes) => nodes
    .map(n => {
      const kids = n.children ? dfs(n.children) : []
      if (match(n) || kids.length) return { ...n, children: kids }
      return null
    })
    .filter(Boolean)
  return dfs(tree)
})
const scrollToId = (id) => {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
/* 使用 Tailwind CSS，大部分样式已迁移到类名中 */
/* 保留必要的 Element Plus 样式覆盖 */
/* 为el-table设置固定高度和滚动条 */
.scrollable-table {
    height: 30vh; /* 根据需要调整，确保留出分页和按钮的空间 */
    overflow-y: auto;
    margin-top: 1%;
}
.active {
    background-color: #409EFF; /* 高亮颜色 */
    color: white;
}
.el-table__body-wrapper {
    overflow: auto !important;
}

:deep(.el-dialog) {
  border-radius: 20px;
  padding: 0 0 16px 0;
}

:deep(.el-dialog__header) {
  --el-text-color-primary: #1EFFFF;
  --el-text-color-regular: #fff;
  padding: 0 !important;
  margin: 0 !important;
  height: 50px;
  background-color: #F9F9F9;
  border-bottom: 1px solid #eaeaea;
  box-shadow: 0 1px 5px 0 rgba(0, 0, 0, 0.08);
  /*background-color: #c71717;*/
  border-top-left-radius: 15px;
  border-top-right-radius: 15px;
  box-sizing: border-box;
}
:deep(.el-dialog__title) {
  margin-left: 24px;
  line-height: 50px;
  color: black;
  font-weight: bold;
}

:deep(.el-dialog__body) {
  padding: 16px 16px 0 16px;
}

:deep(.el-dialog__footer) {
  padding: 16px 16px 0 16px;
}

.button-container {

  margin-left: 5%;
  width: 90%;
  padding: 5px;
  background-color: #f5f5f5;
  border-radius: 40px;
}

.button-container-button {
  flex: 1;
  /*padding: 10px;*/
  /*margin: 5px;*/
  /*border: 1px solid red;*/
  border: none;
  border-radius: 20px !important;
  background-color: #f5f5f5;
  color: #333;
  cursor: pointer;
  transition: background-color 0.3s;
}

.button-container-button:hover {
  background-color: #f5f5f5;
}


:deep(.custom-message-box) {
  width: 300px; /* 设置宽度 */
  height: 150px;
}

:deep(.custom-message-box .el-message-box__message) {
  margin-top: 8px;
  font-size: 20px; /* 调整消息内容的字体大小 */
}

:deep(.custom-message-box .el-message-box__btns button) {
  font-size: 20px; /* 调整按钮的字体大小 */
}
:deep(.custom-message-box .el-message-box__header .el-message-box__title .el-icon) {
  font-size: 32px;
}
:deep(.custom-confirm-button) {
  background-color: #5571FF;
  border: none;
}
:deep(.custom-upload-box .el-upload .el-upload-dragger .el-icon) {
  margin-left: 10%;
  margin-top: -20px;
  font-size: 40px;
}

:deep(.custom-upload-box .el-upload .el-upload-dragger) {
  display: flex;
  height: 50px;
}
:deep(.custom-upload-box .el-upload .el-upload-dragger .el-upload__text) {
  margin-top: -16px;
  font-size: 20px;
}
:deep(.el-table .el-table__body td) {
  font-size: 15px; /* 调整字体大小 */
  font-weight: normal; /* 加粗字体 */
  /*font-family:'Times New Roman', Times, serif;*/
}
:deep(.demo-progress .el-progress--line) {
  /*margin-bottom: 15px;*/
  height: 20px;
  width: 100%;
  /*margin-left: 100%;*/
}
.file-icon{
  width: 4.8%;
}
/* 修改当前页码按钮的背景色和文字颜色 */
:deep(.el-pagination .el-pager .number.is-active) {
  /*background-color: #5571FF; !* 当前页码按钮背景颜色 *!*/
  color: #5571FF; /* 当前页码按钮文字颜色 */

}
:deep(.el-pagination .el-pager .number:hover) {
  /*background-color: #5571FF; !* 当前页码按钮背景颜色 *!*/
  color: #5571FF; /* 当前页码按钮文字颜色 */

}
:deep(.no-horizontal-border .el-table__row>td) { border: none; }
:deep(.no-horizontal-border .el-table::before) { height: 0px; }

/* 增加文章标题输入框的上间距 */
:deep(textarea#template-title) {
  padding-top: 2rem !important;
}

/* 修复“全部模板”弹窗在选择后出现的边界溢出与位移问题 */
:deep(.template-dialog .el-dialog) {
  /* 去除全局为 .el-dialog 设置的额外内边距，避免宽度计算溢出 */
  padding: 0 !important;
  width: 80vw !important;
  max-width: 1100px;
  max-height: 80vh;
  overflow: hidden; /* 禁止外层产生水平/垂直溢出 */
}
:deep(.template-dialog .el-dialog__body) {
  /* 让内容区可滚动，避免撑破弹窗 */
  max-height: calc(80vh - 120px);
  overflow: auto;
  box-sizing: border-box;
}
:deep(.template-dialog .el-dialog__footer) {
  /* 保证底部操作区始终在可视范围内且不挤出边界 */
  padding: 12px 16px 16px 16px !important;
  background: var(--background, #fff);
}
</style>
