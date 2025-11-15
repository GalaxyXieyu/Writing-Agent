<template>
  <div class="space-y-4">
    <div
      v-for="(item, index) in titleData"
      :key="index"
      :id="`first-${item.titleId ?? index}`"
      class="group rounded-lg border border-border bg-card shadow-sm transition-all hover:shadow-md"
    >
      <!-- 标题头部 -->
      <div class="flex items-center justify-between border-b border-border bg-muted/50 px-5 py-3.5">
        <div class="flex items-center gap-3">
          <Button 
            variant="ghost" 
            size="icon-sm" 
            @click="item.isFirstTitleClose = !item.isFirstTitleClose" 
            class="h-7 w-7 rounded-md hover:bg-background"
          >
            <svg v-if="!item.isFirstTitleClose" class="h-4 w-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
            </svg>
            <svg v-else class="h-4 w-4 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </Button>
          <Badge variant="secondary" class="bg-primary/10 text-primary font-medium px-2.5 py-0.5">一级标题</Badge>
        </div>
        <div class="flex items-center gap-1">
          <Button 
            variant="ghost" 
            size="icon-sm" 
            @click="addSecondLevelTitle(item)" 
            class="h-7 w-7 rounded-md hover:bg-background"
            title="添加二级标题"
          >
            <img src="../iconPng/添加.png" alt="添加" class="h-4 w-4" />
          </Button>
          <Button 
            variant="ghost" 
            size="icon-sm" 
            @click="deleteFirstLevelTitle(item)" 
            class="h-7 w-7 rounded-md hover:bg-destructive/10 hover:text-destructive"
            title="删除一级标题"
          >
            <img src="../iconPng/删除.png" alt="删除" class="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <!-- 内容区域 -->
      <div v-show="!item.isFirstTitleClose" class="p-5 space-y-5">
        <!-- 一级标题输入：压缩 textarea 高度，适配 1920×1080 单屏展示 -->
        <div class="space-y-2.5">
          <Label class="text-responsive-sm font-medium text-foreground">标题名称</Label>
          <Textarea
            v-model="item.titleName"
            placeholder="输入一级标题"
            :maxlength="100"
            class="min-h-[70px] resize-none w-full"
          />
          <p class="text-right text-responsive-xs text-muted-foreground">{{ item.titleName?.length || 0 }}/100</p>
        </div>
        
        <!-- 写作要求输入 -->
        <div class="space-y-2.5">
          <Label class="text-responsive-sm font-medium text-foreground">写作要求</Label>
          <Textarea
            v-model="item.writingRequirement"
            placeholder="输入写作要求"
            :maxlength="300"
            class="min-h-[90px] resize-none w-full"
          />
          <p class="text-right text-responsive-xs text-muted-foreground">{{ item.writingRequirement?.length || 0 }}/300</p>
        </div>

        <!-- 参考输出（可选） -->
        <div class="space-y-2.5">
          <Label class="text-responsive-sm font-medium text-foreground">参考输出（可选）</Label>
          <Textarea
            v-model="item.referenceOutput"
            placeholder="可粘贴本章期望的示例输出，便于参考"
            :maxlength="5000"
            class="min-h-[90px] resize-none w-full"
          />
          <p class="text-right text-responsive-xs text-muted-foreground">{{ item.referenceOutput?.length || 0 }}/5000</p>
        </div>
        
        <!-- 二级标题列表 -->
        <div v-if="item.children && item.children.length > 0" class="mt-5 space-y-4">
          <div 
            v-for="(childrenItem, childrenIndex) in item.children" 
            :key="childrenIndex" 
            :id="`second-${childrenItem.titleId ?? childrenIndex}`"
            class="rounded-md border border-border bg-muted/30 p-4"
          >
            <div class="mb-4 flex items-center justify-between">
              <Badge variant="secondary" class="bg-secondary text-secondary-foreground font-medium px-2.5 py-0.5 text-responsive-sm">二级标题</Badge>
              <div class="flex items-center gap-1">
                <Button 
                  variant="ghost" 
                  size="icon-sm" 
                  @click="addThirdLevelTitle(item, childrenItem)" 
                  class="h-6 w-6 rounded-md hover:bg-background"
                  title="添加三级标题"
                >
                  <img src="../iconPng/添加.png" alt="添加" class="h-3.5 w-3.5" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="icon-sm" 
                  @click="deleteSecondLevelTitle(item, childrenItem)" 
                  class="h-6 w-6 rounded-md hover:bg-destructive/10 hover:text-destructive"
                  title="删除二级标题"
                >
                  <img src="../iconPng/删除.png" alt="删除" class="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
            <div class="space-y-4">
              <div class="space-y-2.5">
                <Label class="text-responsive-xs font-medium text-foreground">标题名称</Label>
                <Textarea
                  v-model="childrenItem.titleName"
                  placeholder="输入二级标题"
                  :maxlength="100"
                  class="min-h-[60px] resize-none w-full"
                />
                <p class="text-right text-responsive-xs text-muted-foreground">{{ childrenItem.titleName?.length || 0 }}/100</p>
              </div>
              <div class="space-y-2.5">
                <Label class="text-responsive-xs font-medium text-foreground">写作要求</Label>
                <Textarea
                  v-model="childrenItem.writingRequirement"
                  placeholder="输入写作要求"
                  :maxlength="300"
                  class="min-h-[80px] resize-none w-full"
                />
                <p class="text-right text-responsive-xs text-muted-foreground">{{ childrenItem.writingRequirement?.length || 0 }}/300</p>
              </div>

              <!-- 参考输出（可选） -->
              <div class="space-y-2.5">
                <Label class="text-responsive-xs font-medium text-foreground">参考输出（可选）</Label>
                <Textarea
                  v-model="childrenItem.referenceOutput"
                  placeholder="可粘贴本节期望的示例输出，便于参考"
                  :maxlength="5000"
                  class="min-h-[80px] resize-none w-full"
                />
                <p class="text-right text-responsive-xs text-muted-foreground">{{ childrenItem.referenceOutput?.length || 0 }}/5000</p>
              </div>
            </div>
            
            <!-- 三级标题列表 -->
            <div v-if="childrenItem.children && childrenItem.children.length > 0" class="mt-4 space-y-3">
              <div 
                v-for="(thirdLevelItem, thirdLevelIndex) in childrenItem.children" 
                :key="thirdLevelIndex" 
                :id="`third-${thirdLevelItem.titleId ?? thirdLevelIndex}`"
                class="rounded-md border border-border bg-background p-4"
              >
                <div class="mb-3 flex items-center justify-between">
                  <Badge variant="outline" class="font-medium px-2 py-0.5 text-responsive-xs">三级标题</Badge>
                  <Button 
                    variant="ghost" 
                    size="icon-sm" 
                    @click="deleteThirdLevelTitle(item, childrenItem, thirdLevelItem)" 
                    class="h-6 w-6 rounded-md hover:bg-destructive/10 hover:text-destructive"
                    title="删除三级标题"
                  >
                    <img src="../iconPng/删除.png" alt="删除" class="h-3 w-3" />
                  </Button>
                </div>
                <div class="space-y-3">
                  <div class="space-y-2">
                    <Label class="text-responsive-xs font-medium text-foreground">标题名称</Label>
                    <Textarea
                      v-model="thirdLevelItem.titleName"
                      placeholder="输入三级标题"
                      :maxlength="100"
                      class="min-h-[50px] resize-none w-full text-responsive-sm"
                    />
                    <p class="text-right text-responsive-xs text-muted-foreground">{{ thirdLevelItem.titleName?.length || 0 }}/100</p>
                  </div>
                  <div class="space-y-2">
                    <Label class="text-responsive-xs font-medium text-foreground">写作要求</Label>
                    <Textarea
                      v-model="thirdLevelItem.writingRequirement"
                      placeholder="输入写作要求"
                      :maxlength="300"
                      class="min-h-[60px] resize-none w-full text-responsive-sm"
                    />
                    <p class="text-right text-responsive-xs text-muted-foreground">{{ thirdLevelItem.writingRequirement?.length || 0 }}/300</p>
                  </div>

                  <!-- 参考输出（可选） -->
                  <div class="space-y-2">
                    <Label class="text-responsive-xs font-medium text-foreground">参考输出（可选）</Label>
                    <Textarea
                      v-model="thirdLevelItem.referenceOutput"
                      placeholder="可粘贴该小节期望的示例输出，便于参考"
                      :maxlength="5000"
                      class="min-h-[60px] resize-none w-full text-responsive-sm"
                    />
                    <p class="text-right text-responsive-xs text-muted-foreground">{{ thirdLevelItem.referenceOutput?.length || 0 }}/5000</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加按钮 -->
    <div class="rounded-lg border-2 border-dashed border-border bg-muted/30 p-5 text-center transition-colors hover:border-primary/50 hover:bg-muted/50">
      <Button variant="ghost" @click="addFirstLevelTitle" class="font-semibold text-responsive-base text-foreground">
        <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加一级标题
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Button from '@/components/ui/Button.vue';
import Textarea from '@/components/ui/Textarea.vue';
import Badge from '@/components/ui/Badge.vue';
import Label from '@/components/ui/Label.vue';
// 使用ref创建响应式状态，默认为false，表示按钮默认不显示
const isDeleteButtonFocus = ref(true);
const props = defineProps({
  titleData:{
    type: Array,
    default: () => {
      return [{
          titleId: '',
          templateId: '',
          parentId: '',
          titleName: '',
          showOrder: 1,
          writingRequirement: '',
          referenceOutput: '',
          statusCd: "Y",
          isFirstTitleClose:true,
          children: [],
      }]
    },
  },
});
//新增一级标题
let globalIdCounter = 1;
const addFirstLevelTitle = () => {
    const firstTitleId = ++globalIdCounter;
    console.log("一级标题的 children 数组已初始化",firstTitleId);
  props.titleData.push({
    titleId:firstTitleId,
    titleName: '',
    writingRequirement: '',
    referenceOutput: '',
    children:[]
  });
};
//删除一级标题
const deleteFirstLevelTitle = (item) => {
  for (let i = 0; i < props.titleData.length; i++) {
    if (props.titleData[i].titleId === item.titleId) {
      props.titleData.splice(i, 1);
    }
  }

};
//增加二级标题
const addSecondLevelTitle = (item) => {
    const secondTitleId = ++globalIdCounter;
    console.log("二级标题的 children 数组已初始化",secondTitleId);
  for (let i = 0; i < props.titleData.length; i++) {
    if (props.titleData[i].titleId === item.titleId) {
      props.titleData[i].children.push({
        titleId:secondTitleId,
        titleName: '',
        writingRequirement: '',
        referenceOutput: '',
        children: []
      });
    }
  }
};

//删二级标题
const deleteSecondLevelTitle = (item, childrenItem) => {
    console.log(item, childrenItem)
    for (let i = 0; i < props.titleData.length; i++) {
        if (props.titleData[i].titleId === item.titleId) {
            for (let j = 0; j < props.titleData[i].children.length; j++) {
                if (props.titleData[i].children[j].titleId === childrenItem.titleId) {
                    props.titleData[i].children.splice(j, 1);
                }
            }
        }
    }

};

//增加三级标题
const addThirdLevelTitle = (item, secondLevelItem) => {
    // const thirdTitleId = Date.now().toString(36);
    const thirdTitleId = ++globalIdCounter;
    for (let i = 0; i < props.titleData.length; i++) {
        if (props.titleData[i].titleId === item.titleId) {
            for (let j = 0; j < props.titleData[i].children.length; j++) {
                if (props.titleData[i].children[j].titleId === secondLevelItem.titleId) {
                    // 确保二级标题的 children 数组已经初始化
                    if (!props.titleData[i].children[j].children) {
                        props.titleData[i].children[j].children = [];
                    }
                    props.titleData[i].children[j].children.push({ 
                      titleId: thirdTitleId,
                      titleName: '',
                      writingRequirement: '',
                      referenceOutput: ''
                    });
                    console.log("三级标题已添加",props.titleData);
                }
            }
        }
    }
};
//删三级标题
const deleteThirdLevelTitle = (item, childrenItem, subChildrenItem) => {
    console.log(item, childrenItem, subChildrenItem);
    for (let i = 0; i < props.titleData.length; i++) {
        if (props.titleData[i].titleId === item.titleId) {
            for (let j = 0; j < props.titleData[i].children.length; j++) {
                if (props.titleData[i].children[j].titleId === childrenItem.titleId) {
                    for (let k = 0; k < props.titleData[i].children[j].children.length; k++) {
                        if (props.titleData[i].children[j].children[k].titleId === subChildrenItem.titleId) {
                            props.titleData[i].children[j].children.splice(k, 1);
                            console.log("三级标题已删除");
                        }
                    }
                }
            }
        }
    }
};
</script>

<style scoped>
/* 使用 Tailwind CSS，大部分样式已迁移到类名中 */
</style>
