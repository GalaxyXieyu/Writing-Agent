from langchain_openai import ChatOpenAI

qwen = ChatOpenAI(
    temperature=0.2,
    model="Qwen\Qwen2.5-14B-Chat",
    openai_api_key="sk-whdzfxxaxzykjleoerjxrlgwehixdjbbqrzomhdisrnithog",
    openai_api_base="https://api.siliconflow.cn/v1"
)
