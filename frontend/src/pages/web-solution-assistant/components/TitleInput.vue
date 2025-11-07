<template>
  <div>
    <el-form>
      <div v-for="(item, index) in titleData" :key="index" style="margin-bottom: 1vh;background-color: #F5F5F5;border-radius: 10px;padding-bottom: 1vh;">
        <el-row>
          <el-col :span="17" class="first-tag">
            <el-button v-if="!item.isFirstTitleClose" type="text" style="color: black;width: 5%;border: none" size="small" plain @click="item.isFirstTitleClose = true">
              <el-icon size="12"><ArrowUp /></el-icon>
            </el-button>
            <el-button v-else type="text" style="color: black;width: 5%;border: none" size="small" plain @click="item.isFirstTitleClose = false">
              <el-icon size="12"><ArrowDown /></el-icon>
            </el-button>
            <el-tag type="text" style="border-radius: 6px;background-color: #E5E7F6;color: #555">一级标题</el-tag>
          </el-col>
          <el-col :span="6">
            <el-button type="text" class="first-button" size="small" plain @click="addSecondLevelTitle(item)">
<!--              <el-icon size="18" color="#555"><Plus/></el-icon>-->
              <img src="../iconPng/添加.png" alt="PNG Icon" class="file-icon" />
            </el-button>
            <el-button type="text" class="first-button" size="small" plain @click="deleteFirstLevelTitle(item)">
<!--              <el-icon size="18" color="#555"><DeleteFilled /></el-icon>-->
              <img src="../iconPng/删除.png" alt="PNG Icon" class="file-icon" />
            </el-button>
          </el-col>
        </el-row>
        <div class="first-dash-left-border" v-show="!item.isFirstTitleClose">
          <el-row>
            <el-col :span="24">
              <el-input class="first-input" maxlength="100"
                        type="textarea"
                        autosize
                        resize="none"
                        v-model="item.titleName" placeholder="输入一级标题" show-word-limit/>
<!--              <p class="text-length-p">{{ item.titleName?item.titleName.length:0 }}/100</p>-->
            </el-col>
            <el-col :span="24">
              <el-input class="first-input"
                        type="textarea"
                        autosize
                        resize="none"
                        :border="false" maxlength="300" v-model="item.writingRequirement" placeholder="输入写作要求" show-word-limit/>
<!--              <p class="text-length-p">{{ item.writingRequirement?item.writingRequirement.length:0 }}/300</p>-->
            </el-col>
          </el-row>
          <div v-for="(childrenItem, childrenIndex) in item.children" :key="childrenIndex">
            <div class="second-dash-left-border">
              <el-row>
                <el-col :span="17">
                  <el-tag class="second-tag" type="text" style="border-radius: 6px;background-color: #E5E7F6;color: #555">二级标题</el-tag>
                </el-col>
                <el-col :span="6">
                    <el-button type="text" class="second-button-add" size="small" plain @click="addThirdLevelTitle(item, childrenItem)">
<!--                        <el-icon size="18" color="#555"><Plus /></el-icon>-->
                      <img src="../iconPng/添加.png" alt="PNG Icon" class="file-icon" />
                    </el-button>
                  <el-button type="text" class="second-button" size="small" plain
                             @click="deleteSecondLevelTitle(item,childrenItem)">
<!--                    <el-icon size="18" color="#555"><DeleteFilled /></el-icon>-->
                    <img src="../iconPng/删除.png" alt="PNG Icon" class="file-icon" />
                  </el-button>
                </el-col>
              </el-row>
              <el-row>
                <el-col :span="24">
                  <el-input class="second-input"
                            type="textarea"
                            autosize
                            resize="none"
                            maxlength="100" v-model="childrenItem.titleName" placeholder="输入二级标题" show-word-limit/>
<!--                  <p class="text-length-p">{{ childrenItem.titleName?childrenItem.titleName.length:0 }}/100</p>-->
                </el-col>
                <el-col :span="24">
                  <el-input class="second-input"
                            type="textarea"
                            autosize
                            resize="none"
                            maxlength="300" v-model="childrenItem.writingRequirement" placeholder="输入写作要求" show-word-limit/>
<!--                  <p class="text-length-p">{{ childrenItem.writingRequirement?childrenItem.writingRequirement.length:0 }}/300</p>-->
                </el-col>
              </el-row>
                <div v-for="(thirdLevelItem, thirdLevelIndex) in childrenItem.children" :key="thirdLevelIndex">
                    <div class="third-dash-left-border">
                        <el-row>
                            <el-col :span="17">
                                <el-tag class="third-tag" type="text" style="border-radius: 6px;background-color: #E5E7F6;color: #555">三级标题</el-tag>
                            </el-col>
                            <el-col :span="6">
                                <el-button type="text" class="third-button" size="small" plain @click="deleteThirdLevelTitle(item, childrenItem, thirdLevelItem)">
<!--                                    <el-icon size="18" color="#555"><DeleteFilled /></el-icon>-->
                                  <img src="../iconPng/删除.png" alt="PNG Icon" class="file-icon" />
                                </el-button>
                            </el-col>
                        </el-row>
                        <el-row>
                            <el-col :span="24">
                                <el-input class="third-input"
                                          type="textarea"
                                          autosize
                                          resize="none"
                                          maxlength="100" v-model="thirdLevelItem.titleName" placeholder="输入三级标题" show-word-limit/>
<!--                                <p class="text-length-p">{{ thirdLevelItem.titleName?thirdLevelItem.titleName.length:0 }}/100</p>-->
                            </el-col>
                            <el-col :span="24">
                                <el-input class="third-input"
                                          maxlength="300" type="textarea" autosize
                                          resize="none"
                                          v-model="thirdLevelItem.writingRequirement" placeholder="输入写作要求" show-word-limit/>
<!--                                <p class="text-length-p">{{ thirdLevelItem.writingRequirement?thirdLevelItem.writingRequirement.length:0 }}/300</p>-->
                            </el-col>
                        </el-row>
                    </div>
                </div>
            </div>
          </div>
        </div>
      </div>
      <div class="firstLevelTitleAdd">
        <el-button type="text" size="small" plain @click="addFirstLevelTitle"
                   style="font-weight: bold;color: #504c4c;font-size: 0.96rem">
          <el-icon size="18" style="margin-right:5px;" color="#555"><Plus /></el-icon>添加一级标题</el-button>
      </div>


    </el-form>
  </div>
</template>

<script setup>


import {DeleteFilled,Plus,ArrowUp,ArrowDown } from '@element-plus/icons-vue'
import { ref } from 'vue';
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
  props.titleData.push({titleId:firstTitleId,children:[]});
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
      props.titleData[i].children.push({titleId:secondTitleId});
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
                    props.titleData[i].children[j].children.push({ titleId: thirdTitleId });
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

/* 一级标题tag样式 */
.first-tag{
  margin-left: 3%;
  margin-top: 1vh

}
/* 一级标题input样式 */
.first-input{
  width: 94%;
  margin-left: 3%;
  margin-top: 5px;
}
.first-button{
  width: 20px;
  margin-top: 1vh;
  margin-right: 5px;
  text-align: right;
  float: right;
  /*border: 1px solid red;*/
}
/* 二级标题tag样式 */
.second-tag{
  margin-left: 3%;
}
/* 二级标题input样式 */
.second-input{
  width: 94%;
  margin-left: 3%;
  margin-top: 5px
}
/* 三级标题tag样式 */
.third-tag{
    margin-left: 3%;
}
/* 三级标题input样式 */
.third-input{
    width: 94%;
    margin-left: 3%;
    margin-top: 5px
}
.second-button{
  width: 20px;
  margin-right: 5px;
  text-align: right;
  float: right;
}
.second-button-add{
    width: 20px;
    margin-right: -5%;
  /*border: 1px solid red;*/
    text-align: right;
    float: right;

}
.third-button{
    width: 20px;
    margin-right: 5px;
    text-align: right;
    float: right;

}
.firstLevelTitleAdd{
  width: 100%;
  /*margin-left: 5%;*/
  margin-top: 1vh;
  background-color: #F5F5F5;
  text-align: center;
  /*height: 3vh;*/
  margin-bottom: 1vh;
  /*border: 1px solid red;*/
}
.text-length-p{
  margin-right: 10px;
  text-align: right;
  font-size: 12px;
  opacity: 0.5
}
.first-dash-left-border {
  border-left: 1px dashed #ccc; /* 左边框为灰色虚线 */
  margin-left: 6%;
}
.second-dash-left-border {
  border-left: 1px dashed #ccc; /* 左边框为灰色虚线 */
  margin-left: 3%;
  margin-top: 8px; /* 短边框后面有10px的内边距 */

}
.third-dash-left-border{
    border-left: 1px dashed #ccc; /* 左边框为灰色虚线 */
    margin-left: 3%;
    margin-top: 5px; /* 短边框后面有10px的内边距 */

}
.file-icon{
  width: 18px;
}
</style>
