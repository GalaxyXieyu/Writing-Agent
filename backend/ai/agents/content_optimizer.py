import json
import re
import warnings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from templates.ai_templates.content_optimize import content_optimize_prompt

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

def build_optimize_chain(llm: ChatOpenAI):
    """构造优化内容链，外部注入 llm。"""
    return {"original_text": RunnablePassthrough(), "article_type": RunnablePassthrough(), "user_requirements": RunnablePassthrough()} | content_optimize_prompt | llm | StrOutputParser()

# headers = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "Authorization": "Bearer sk-nmyyoncsmaagafmvjmbpyaxbeewtwqaiycitmhtomjzlwbsw"
# }

# llm = ChatOpenAI(
#     temperature=0.2,
#     model="Qwen/Qwen.5-14B-Chat",
#     openai_api_base="https://api.siliconflow.cn/v1",
#     default_headers=headers
# )


warnings.filterwarnings('ignore')
