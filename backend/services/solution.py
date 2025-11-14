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

"""生成、优化流程的通用空值防御与日志增强"""

# 生成写作要求的递归函数（兼容 None 值）
def generate_writing_requirements(chapter: OutlineItem) -> str:
    requirements: list[str] = []

    def recurse(node, prefix: str = ""):
        title = getattr(node, "titleName", None) or ""
        req = getattr(node, "writingRequirement", None) or ""
        if req:
            requirements.append(f"{prefix}{title}: {req}")
        else:
            requirements.append(f"{prefix}{title}")

        children = getattr(node, "children", None) or []
        for child in children:
            recurse(child, prefix + "  ")

    recurse(chapter)
    return "\n".join(requirements)



# 完整章节生成
async def generate_article(state: ChapterGenerationState, llm, db=None) -> AsyncGenerator[str, None]:
    complete_content: str = ""  # 用于存储完整的返回内容
    # 提取最高级别的标题（防御 None）
    highest_level_title = getattr(state.outline, "titleName", None) or ""
    # 去除冗余日志输出
    
    while True:
        chapter = state.next_chapter()
        if not chapter:
            break
        
        # 获取上一章节的内容
        if state.generated_contents:
            last_para_content = state.generated_contents[-1] or ""
            # 统计 token 数量
            token_count = len(last_para_content)
            # 如果超过 2000 个 token，则截断最后 2000 个 token
            if token_count > 2000:
                last_para_content = last_para_content[-2000:]
        else:
            last_para_content = ""
        
        # 打印调试信息，确保每章的标题和要求被正确传入
        title_safe = getattr(chapter, "titleName", None) or ""
        req_safe = getattr(chapter, "writingRequirement", None) or ""
        # 标题输出防御 None
        yield "# " + title_safe + "\n"
        # 处理每个二级章节
        children = getattr(chapter, "children", None) or []
        if not children:
            async for token in generate_chapter(chapter, last_para_content, highest_level_title, llm, db=db):
                tok = token or ""
                complete_content += tok  # 累加到完整内容中
                yield tok
        else:
            for subchapter in children:
                subchapter_content: str = ""
                async for token in generate_chapter(subchapter, last_para_content, highest_level_title, llm, db=db):
                    tok = token or ""
                    subchapter_content += tok
                    complete_content += tok  # 累加到完整内容中
                    yield tok
                
                # 每个二级章节之间返回一个换行符
                yield "\n\n"
                
                # 更新 last_para_content 为当前子章节的内容
                last_para_content = subchapter_content
        
        # 将当前章节的内容添加到 generated_contents 列表中
        state.generated_contents.append(complete_content or "")
    
    # 去除冗余日志输出


# 单个章节生成
async def generate_chapter(chapter: OutlineItem, last_para_content: str, highest_level_title: str, llm, db=None) -> AsyncGenerator[str, None]:
    # 入参兼容与结构拼装
    writing_requirements = generate_writing_requirements(chapter)
    structure = f"Writing Requirement: {writing_requirements}"
    complete_template = f"{structure}"

    try:
        # 使用异步函数构建 chain，支持从数据库读取提示词
        from ai.agents.paragraph_writer import build_paragraph_chain_async
        llm_no_usage = llm.bind(stream_options={"include_usage": False})
        chain = await build_paragraph_chain_async(llm_no_usage, db=db)
        inputs = {
            "complete_title": highest_level_title or "",
            "last_para_content": last_para_content or "",
            "titleNames": getattr(chapter, "titleName", None) or "",
            "requirements": writing_requirements or ""
        }
        try:
            # 直接使用 astream 返回的增量结果（AIMessageChunk 或字符串）
            async for chunk in chain.astream(inputs):

                # 统一抽取文本内容
                text = getattr(chunk, "content", None)
                if text is None:
                    if isinstance(chunk, str):
                        text = chunk
                    else:
                        try:
                            text = str(chunk)
                        except Exception:
                            text = ""
                if text:
                    yield text
        except Exception as se:
            # 处理流式异常；若为已知的 AIMessageChunk usage 校验问题，则强制回退
            STREAM_ONLY = (os.getenv("AI_STREAM_ONLY", "").lower() in ("1", "true", "yes"))
            err_msg = str(se)
            force_fallback = ("AIMessageChunk" in err_msg) or ("usage_metadata" in err_msg)
            if STREAM_ONLY and not force_fallback:
                # 静默跳过（不回退）
                pass
            else:
                # 回退到非流式一次性生成
                try:
                    resp = await chain.ainvoke(inputs)
                    content_text = getattr(resp, "content", resp) or ""
                    if not isinstance(content_text, str):
                        try:
                            content_text = str(content_text)
                        except Exception:
                            content_text = ""
                    chunk_size = 500
                    for i in range(0, len(content_text), chunk_size):
                        yield content_text[i:i+chunk_size]
                except Exception:
                    # 静默失败
                    pass
    except Exception:
        # 静默失败
        pass
    yield "\n"  # 在章节结束后添加一个换行

# 优化内容
async def optimize_content(original_text: str, article_type: str, user_requirements: str, llm) -> AsyncGenerator[str, None]:
    try:
        # 禁用 usage 推送，避免上游返回 null 触发校验错误
        try:
            llm_no_usage = llm.bind(stream_options={"include_usage": False})
        except Exception:
            llm_no_usage = llm
        chain = build_optimize_chain(llm_no_usage)
        try:
            async for chunk in chain.astream({
                "original_text": original_text,
                "article_type": article_type,
                "user_requirements": user_requirements
            }):
                text = getattr(chunk, "content", None)
                if text is None:
                    if isinstance(chunk, str):
                        text = chunk
                    else:
                        try:
                            text = str(chunk)
                        except Exception:
                            text = ""
                if text:
                    yield text
        except Exception as se:
            # 与章节生成一致的回退策略
            STREAM_ONLY = (os.getenv("AI_STREAM_ONLY", "").lower() in ("1", "true", "yes"))
            err_msg = str(se)
            force_fallback = ("AIMessageChunk" in err_msg) or ("usage_metadata" in err_msg)
            if STREAM_ONLY and not force_fallback:
                pass
            else:
                try:
                    resp = await chain.ainvoke({
                        "original_text": original_text,
                        "article_type": article_type,
                        "user_requirements": user_requirements
                    })
                    content_text = getattr(resp, "content", resp) or ""
                    if not isinstance(content_text, str):
                        try:
                            content_text = str(content_text)
                        except Exception:
                            content_text = ""
                    chunk_size = 500
                    for i in range(0, len(content_text), chunk_size):
                        yield content_text[i:i+chunk_size]
                except Exception:
                    pass
    except Exception:
        # 静默降级
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
    
    # 去除冗余日志
    async for content in generate_article(state):
        print(content, end='', flush=True)
    # 去除冗余日志

if __name__ == "__main__":
    asyncio.run(test_generate_article())