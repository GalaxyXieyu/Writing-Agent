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
        # 调试日志：确认传入的 outline 结构
        children = getattr(outline, 'children', None)
        mylog.info(f"[ChapterGenerationState] 初始化, titleName={getattr(outline, 'titleName', 'N/A')}, children_count={len(children) if children else 0}, children_type={type(children)}")

    def next_chapter(self) -> Optional[OutlineItem]:
        children = getattr(self.outline, 'children', None) or []
        mylog.info(f"[next_chapter] current_index={self.current_chapter_index}, children_count={len(children)}")
        if self.current_chapter_index < len(children):
            chapter = children[self.current_chapter_index]
            self.current_chapter_index += 1
            mylog.info(f"[next_chapter] 返回章节: {getattr(chapter, 'titleName', 'N/A')}")
            return chapter
        mylog.info("[next_chapter] 没有更多章节")
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



# 阿拉伯数字转中文数字
def to_chinese_numeral(num: int) -> str:
    """将阿拉伯数字转换为中文数字（1-99）"""
    chinese_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
    if num <= 10:
        return chinese_nums[num]
    elif num < 20:
        return f"十{chinese_nums[num - 10]}" if num > 10 else "十"
    elif num < 100:
        tens = num // 10
        ones = num % 10
        if ones == 0:
            return f"{chinese_nums[tens]}十"
        return f"{chinese_nums[tens]}十{chinese_nums[ones]}"
    return str(num)


# 生成 Markdown 标题（根据层级自动添加 # 数量和编号）
def generate_markdown_title(title: str, level: int, numbering: str) -> str:
    """
    生成 Markdown 格式的标题
    level: 1=一级(##), 2=二级(###), 3=三级(####)
    numbering: 如 "1"、"1.1"、"2.1.1"
    
    格式规范：
    - 一级标题：## 一、标题名
    - 二级标题：### 1.1 标题名
    - 三级标题：#### 1.1.1 标题名
    """
    hashes = "#" * (level + 1)  # level 1 -> ##, level 2 -> ###, level 3 -> ####
    
    if level == 1:
        # 一级标题：用中文数字，如 "一、"
        num = int(numbering) if numbering.isdigit() else 1
        chinese_num = to_chinese_numeral(num)
        return f"{hashes} {chinese_num}、{title}\n\n"
    else:
        # 二级及以下：用阿拉伯数字，如 "1.1"、"1.1.1"
        return f"{hashes} {numbering} {title}\n\n"


# 递归生成章节内容
async def generate_outline_recursive(
    node: OutlineItem, 
    llm, 
    db, 
    highest_level_title: str,
    last_para_content: str,
    level: int,
    numbering: str
) -> AsyncGenerator[str, None]:
    """
    递归遍历大纲，自动生成标题和内容
    - level: 当前层级 (1=一级章节, 2=二级, 3=三级)
    - numbering: 当前编号 (如 "1", "1.1", "1.1.1")
    """
    title = getattr(node, "titleName", None) or ""
    children = getattr(node, "children", None) or []
    
    # 1. 代码自动输出 Markdown 标题
    yield generate_markdown_title(title, level, numbering)
    
    # 2. 大模型生成该章节的内容（不含标题）
    async for token in generate_chapter_content(node, last_para_content, highest_level_title, llm, db=db):
        yield token or ""
    
    yield "\n\n"
    
    # 3. 递归处理子章节
    current_content = ""
    for idx, child in enumerate(children, start=1):
        child_numbering = f"{numbering}.{idx}" if numbering else str(idx)
        async for token in generate_outline_recursive(
            child, llm, db, highest_level_title, 
            current_content[-2000:] if len(current_content) > 2000 else current_content,
            level + 1, 
            child_numbering
        ):
            current_content += token or ""
            yield token


# 完整章节生成
async def generate_article(state: ChapterGenerationState, llm, db=None) -> AsyncGenerator[str, None]:
    """
    生成完整文章：
    1. 代码自动生成 Markdown 标题（## 1. xxx, ### 1.1 xxx）
    2. 大模型只生成内容
    """
    highest_level_title = getattr(state.outline, "titleName", None) or ""
    root_children = getattr(state.outline, 'children', None) or []
    
    # 输出文章总标题
    yield f"# {highest_level_title}\n\n"
    
    # 如果没有子章节，直接生成根节点内容
    if not root_children:
        async for token in generate_chapter_content(state.outline, "", highest_level_title, llm, db=db):
            yield token or ""
        return
    
    # 遍历一级章节
    last_content = ""
    for idx, chapter in enumerate(root_children, start=1):
        numbering = str(idx)
        async for token in generate_outline_recursive(
            chapter, llm, db, highest_level_title,
            last_content[-2000:] if len(last_content) > 2000 else last_content,
            level=1,
            numbering=numbering
        ):
            last_content += token or ""
            yield token


# 单个章节内容生成（只生成内容，不含标题）
async def generate_chapter_content(chapter: OutlineItem, last_para_content: str, highest_level_title: str, llm, db=None) -> AsyncGenerator[str, None]:
    # 入参兼容与结构拼装
    writing_requirements = generate_writing_requirements(chapter)
    structure = f"Writing Requirement: {writing_requirements}"
    complete_template = f"{structure}"
    children_titles = []
    try:
        children_titles = [getattr(c, "titleName", None) or "" for c in (getattr(chapter, "children", None) or [])]
    except Exception:
        children_titles = []
    expected_titles = "\n".join([f"- {t}" for t in children_titles if t])

    # 简化日志：只在首次生成时输出关键信息
    chapter_title = getattr(chapter, 'titleName', 'N/A')
    
    # 获取参考输出
    example_output = getattr(chapter, "exampleOutput", None)
    if not example_output:
        example_output = getattr(chapter, "referenceOutput", None)
    
    # 调试日志：检查参考输出是否存在
    has_ref = bool(example_output and str(example_output).strip())
    mylog.info(f"📝 [章节生成] {chapter_title} (db={'有' if db else '无'}, 参考输出={'有' if has_ref else '无'})")

    try:
        # 使用异步函数构建 chain，支持从数据库读取提示词
        from ai.agents.paragraph_writer import build_paragraph_chain_async
        from templates.ai_templates.paragraph_generate import get_paragraph_generate_prompt
        
        llm_no_usage = llm.bind(stream_options={"include_usage": False})
        chain = await build_paragraph_chain_async(llm_no_usage, db=db, example_output=example_output)
        inputs = {
            "complete_title": highest_level_title or "",
            "last_para_content": last_para_content or "",
            "titleNames": getattr(chapter, "titleName", None) or "",
            "requirements": writing_requirements or "",
            "expected_titles": expected_titles or ""
        }
        
        # 打印完整提示词（用于调试）
        prompt_template = await get_paragraph_generate_prompt(db=db, example_output=example_output)
        full_prompt = prompt_template.format(**inputs)
        mylog.info(f"{'='*60}\n📜 [完整提示词] 章节: {chapter_title}\n{'-'*60}\n{full_prompt}\n{'='*60}")

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
