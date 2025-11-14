import json
import re
import warnings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from templates.ai_templates.paragraph_generate import paragraph_generate_prompt, get_paragraph_generate_prompt
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

# 初始化大模型
# headers = {
#     "X-CheckSum": "ef620a8bd9dbe2f67aa2c345b05ded4b",
#     "X-CurTime": "1718784683",
#     "X-Server-Param": "eyJhcHBpZCI6InBvYy1xMTRiIiwiY3NpZCI6InBvYy1xMTRiMTcxODc4NDY4NDE2NDAwMDAwMDAwMDAwY2U0MGFmNzM2N2IzZmYwYmJjNDIzYzViZjUxOWNlMzUifQ==",
#     "Content-Type": "application/json;charset=utf-8"
# }

# llm = ChatOpenAI(
#     temperature=0.2,
#     model="Qwen1.5-14B-Chat",
#     openai_api_base="https://api.siliconflow.cn/v1",
#     default_headers=headers
# )

def build_paragraph_chain(llm: ChatOpenAI):
    """构造段落生成链，外部注入 llm（向后兼容）。"""
    return {"complete_title": RunnablePassthrough(), "last_para_content": RunnablePassthrough(), "titleNames": RunnablePassthrough(), "requirements": RunnablePassthrough()} | paragraph_generate_prompt  | llm | StrOutputParser()

async def build_paragraph_chain_async(llm: ChatOpenAI, db: Optional[AsyncSession] = None):
    """
    异步构造段落生成链，支持从数据库读取提示词。
    
    Args:
        llm: LangChain LLM 实例
        db: 可选的数据库会话，用于从数据库读取提示词
    
    Returns:
        配置好的 LangChain chain
    """
    prompt = await get_paragraph_generate_prompt(db=db)
    return {"complete_title": RunnablePassthrough(), "last_para_content": RunnablePassthrough(), "titleNames": RunnablePassthrough(), "requirements": RunnablePassthrough()} | prompt | llm | StrOutputParser()

async def build_paragraph_chain_async_stream(llm: ChatOpenAI, db: Optional[AsyncSession] = None):
    """
    流式专用链：不接 StrOutputParser，避免流式聚合阶段对 None 做 "+=" 导致报错。
    直接让上层从 chunk/AIMessageChunk 中读取 content。
    """
    prompt = await get_paragraph_generate_prompt(db=db)
    return {"complete_title": RunnablePassthrough(), "last_para_content": RunnablePassthrough(), "titleNames": RunnablePassthrough(), "requirements": RunnablePassthrough()} | prompt | llm

# headers = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "Authorization": "Bearer sk-nmyyoncsmaagafmvjmbpyaxbeewtwqaiycitmhtomjzlwbsw"
# }

# llm = ChatOpenAI(
#     temperature=0.2,
#     model="Qwen/Qwen2.5-14B-Instruct",
#     openai_api_base="https://api.siliconflow.cn/v1",
#     default_headers=headers
# )


warnings.filterwarnings('ignore')
