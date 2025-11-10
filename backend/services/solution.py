import sys
import os
import logging  # 导入 logging 模块

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.agents.paragraph_writer import build_paragraph_chain
from ai.agents.content_optimizer import build_optimize_chain
from ai.llm.llm_factory import LLMFactory
from typing import List, Dict, Any, AsyncGenerator, Optional, Union
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from utils.logger import mylog
from models.templates import TemplateChild as OutlineItem  # 从templates.py导入OutlineItem

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 状态记录
class ChapterGenerationState:
    def __init__(self, outline: OutlineItem):
        self.outline = outline
        self.current_chapter_index = 0
        self.generated_contents = []  # 使用列表保存每一章节的内容

    def next_chapter(self) -> Optional[OutlineItem]:
        if self.current_chapter_index < len(self.outline.children):
            chapter = self.outline.children[self.current_chapter_index]
            self.current_chapter_index += 1
            return chapter
        return None

# 生成写作要求的递归函数
def generate_writing_requirements(chapter: OutlineItem) -> str:
    requirements = []
    
    def recurse(chapter, prefix=""):
        if chapter.writingRequirement:
            requirements.append(f"{prefix}{chapter.titleName}: {chapter.writingRequirement}")
        else:
            requirements.append(f"{prefix}{chapter.titleName}")
        
        for child in chapter.children:
            recurse(child, prefix + "  ")
    
    recurse(chapter)
    return "\n".join(requirements)



# 完整章节生成
async def generate_article(state: ChapterGenerationState, llm, db=None) -> AsyncGenerator[str, None]:
    complete_content = ""  # 用于存储完整的返回内容
    # 提取最高级别的标题
    highest_level_title = state.outline.titleName
    mylog.info(f"最高级别的标题: {highest_level_title}")
    
    while True:
        chapter = state.next_chapter()
        if not chapter:
            break
        
        # 获取上一章节的内容
        if state.generated_contents:
            last_para_content = state.generated_contents[-1]
            # 统计 token 数量
            token_count = len(last_para_content)
            # 如果超过 2000 个 token，则截断最后 2000 个 token
            if token_count > 2000:
                last_para_content = last_para_content[-2000:]
        else:
            last_para_content = ""
        
        # 打印调试信息，确保每章的标题和要求被正确传入
        print(f"生成章节: {chapter.titleName}")
        print(f"章节要求: {chapter.writingRequirement}")
        yield "# "+chapter.titleName+"\n"
        # 处理每个二级章节
        if not chapter.children:
            async for token in generate_chapter(chapter, last_para_content, highest_level_title, llm, db=db):
                complete_content += token  # 累加到完整内容中
                yield token
        else:
            for subchapter in chapter.children:
                subchapter_content = ""
                async for token in generate_chapter(subchapter, last_para_content, highest_level_title, llm, db=db):
                    subchapter_content += token
                    complete_content += token  # 累加到完整内容中
                    yield token
                
                # 每个二级章节之间返回一个换行符
                yield "\n\n"
                
                # 更新 last_para_content 为当前子章节的内容
                last_para_content = subchapter_content
        
        # 将当前章节的内容添加到 generated_contents 列表中
        state.generated_contents.append(complete_content)
    
    mylog.info("完整的返回内容: %s", complete_content)  # 记录信息日志


# 单个章节生成
async def generate_chapter(chapter: OutlineItem, last_para_content: str, highest_level_title: str, llm, db=None) -> AsyncGenerator[str, None]:
    writing_requirements = generate_writing_requirements(chapter)
    structure = f"Writing Requirement: {writing_requirements}"
    complete_template = f"{structure}"

    try:
        # 打印调试信息，确保传入的参数正确
        mylog.debug(f"入参 - last_para_content: {last_para_content}")
        mylog.debug(f"入参 - highest_level_title: {highest_level_title}")
        mylog.debug(f"入参 - 本章内容: {chapter.titleName}")
        mylog.debug(f"入参 - 本章的要求: {writing_requirements}")
        
        # 使用异步函数构建 chain，支持从数据库读取提示词
        from ai.agents.paragraph_writer import build_paragraph_chain_async
        chain = await build_paragraph_chain_async(llm, db=db)
        async for token in chain.astream({
            "complete_title": highest_level_title,
            "last_para_content": last_para_content,
            "titleNames": chapter.titleName,
            "requirements": writing_requirements
        }):
            yield token.content
    except Exception as e:
        mylog.error(f"Error generating chapter: {e}")  # 记录错误日志
    yield "\n"  # 在章节结束后添加一个换行

# 优化内容
async def optimize_content(original_text: str, article_type: str, user_requirements: str, llm) -> AsyncGenerator[str, None]:
    try:
        chain = build_optimize_chain(llm)
        async for token in chain.astream({
            "original_text": original_text,
            "article_type": article_type,
            "user_requirements": user_requirements
        }):
            yield token.content
    except Exception as e:
        mylog.error(f"Error optimizing content: {e}")  # 记录错误日志
        yield original_text

# 测试函数
async def test_generate_article():
    outline = OutlineItem(
        titleId=1,
        templateId=1,
        parentId=0,
        titleName="企业数据化转型的重要性",
        showOrder=1,
        writingRequirement="",
        statusCd="Y",
        children=[
            OutlineItem(
                titleId=2,
                templateId=1,
                parentId=1,
                titleName="第一章",
                showOrder=1,
                writingRequirement="介绍企业数据化转型的背景",
                statusCd="Y",
                children=[
                    OutlineItem(
                        titleId=4,
                        templateId=1,
                        parentId=2,
                        titleName="1.1 数据化转型的定义",
                        showOrder=1,
                        writingRequirement="定义什么是数据化转型",
                        statusCd="Y",
                        children=[
                            OutlineItem(
                                titleId=7,
                                templateId=1,
                                parentId=4,
                                titleName="1.1.1 数据化转型的历史",
                                showOrder=1,
                                writingRequirement="介绍数据化转型的历史背景",
                                statusCd="Y",
                                children=[]
                            )
                        ]
                    ),
                    OutlineItem(
                        titleId=5,
                        templateId=1,
                        parentId=2,
                        titleName="1.2 数据化转型的重要性",
                        showOrder=2,
                        writingRequirement="解释为什么数据化转型对企业很重要",
                        statusCd="Y",
                        children=[]
                    )
                ]
            ),
            OutlineItem(
                titleId=3,
                templateId=1,
                parentId=1,
                titleName="第二章",
                showOrder=2,
                writingRequirement="描述企业数据化转型的不同方法",
                statusCd="Y",
                children=[
                    OutlineItem(
                        titleId=6,
                        templateId=1,
                        parentId=3,
                        titleName="2.1 数据收集与分析",
                        showOrder=1,
                        writingRequirement="介绍数据收集与分析的方法和工具",
                        statusCd="Y",
                        children=[]
                    ),
                    OutlineItem(
                        titleId=8,
                        templateId=1,
                        parentId=3,
                        titleName="2.2 数据驱动决策",
                        showOrder=2,
                        writingRequirement="描述如何通过数据驱动决策",
                        statusCd="Y",
                        children=[
                            OutlineItem(
                                titleId=9,
                                templateId=1,
                                parentId=8,
                                titleName="2.2.1 数据驱动决策的挑战",
                                showOrder=1,
                                writingRequirement="讨论数据驱动决策中可能遇到的挑战",
                                statusCd="Y",
                                children=[]
                            )
                        ]
                    )
                ]
            )
        ]
    )

    state = ChapterGenerationState(outline)
    
    mylog.info("开始生成文章...")  # 记录信息日志
    async for content in generate_article(state):
        print(content, end='', flush=True)
    mylog.info("文章生成完成。")  # 记录信息日志

if __name__ == "__main__":
    asyncio.run(test_generate_article())