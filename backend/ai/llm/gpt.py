from langchain_openai import ChatOpenAI

gpt = ChatOpenAI(
    temperature=0.2,
    model="gpt-4o-eus2",
    openai_api_key="sk-ZFEd6Am3xCHJZB5BAd2bAa7c2fB749Eb86Ba807dC3D3D192",
    openai_api_base="http://127.0.0.1:13000/v1"
)
