import json
import re
import warnings
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from models.templates import TemplateCreateNeed
from templates.ai_templates.template_generate import template_generate_prompt
from utils.tools import extract_template_generate
warnings.filterwarnings('ignore')
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

llm = ChatOpenAI(
    temperature=0.2,
    model="qwen2.5-72b-instruct-awq",
    openai_api_key="sk-0rnrrSH0OsiaWCiv6b37C1E4E60c4b9394325001Ec19A197",
    openai_api_base="http://8.134.195.230:23435/v1"
)

# headers = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "Authorization": "Bearer sk-nmyyoncsmaagafmvjmbpyaxbeewtwqaiycitmhtomjzlwbsw"
# }

# llm = ChatOpenAI(
#     temperature=0.2,
#     model="Qwen/Qwen1.5-14B-Chat",
#     openai_api_base="https://api.siliconflow.cn/v1",
#     default_headers=headers
# )


template_generator = {"titleName": RunnablePassthrough(),"writingRequirement": RunnablePassthrough()} | template_generate_prompt | llm | extract_template_generate
