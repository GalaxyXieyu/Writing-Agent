import json
import re
import warnings
from utils.logger import mylog
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from templates.ai_templates.planner_prompt import planner_prompt

warnings.filterwarnings('ignore')
# 初始化大模型
gpt2 = ChatOpenAI(
    temperature=0.7,
    model="gpt-4o-eus2",
    openai_api_key="sk-ZFEd6Am3xCHJZB5BAd2bAa7c2fB749Eb86Ba807dC3D3D192",
    openai_api_base="http://127.0.0.1:13000/v1"
)
llm = gpt2


def extract_planner(data2):
    try:
        print("测试GPT返回数据：", data2.content)
        match = re.search(r'```json([\s\S]*?)```', data2.content)
        if match:
            json_data_string = match.group(1).strip()
            try:
                json_data = json.loads(json_data_string)
                return json_data
            except json.JSONDecodeError as e:
                print(f"解析JSON数据时发生错误: {e}")
        else:
            print("没有找到匹配的JSON数据")
            json_data = json.loads(data2.content)
            return json_data
        content = data2.content
        pattern = r'^```json(.*?)```$'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            parsed_data = json.loads(json_str)
            return parsed_data
        else:
            raise ValueError("未找到有效的JSON格式数据")
    except Exception as e:
        return data2.content


class Plan(BaseModel):
    titleName: str = Field(description="文章标题")
    writingRequirement: str = Field(description="写作要求")


parser = PydanticOutputParser(pydantic_object=Plan)

planner_prompt1 = planner_prompt

planner = {"query": RunnablePassthrough()} | planner_prompt1 | llm | extract_planner
