import json
from models.templates import TemplateContentResponse, TemplateCreateNeed, TemplateRefreshNeed
from utils.template_load import markdown_to_json, json_to_markdown
from ai.agents import template_generator, template_refresher
from utils.logger import mylog
from langchain_core.runnables import RunnablePassthrough
from templates.ai_templates.template_generate import get_template_generate_prompt
from utils.tools import extract_template_generate
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

class TemplateService:
    def __init__(self):
        pass

    async def create_template(self, createNeed: TemplateCreateNeed) -> TemplateContentResponse:
        try:
            mylog.info("创建模板请求: %s", createNeed)
            markdown_result = await template_generator.ainvoke({
                "titleName": createNeed.titleName,
                "writingRequirement": createNeed.writingRequirement
            })
            json_result = markdown_to_json(markdown_result)
            json_result_dict = json.loads(json_result)
            return TemplateContentResponse(code=200, type="success", data=json_result_dict).dict()
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "AuthenticationError" in error_str or "令牌状态不可用" in error_str:
                raise ValueError("AI模型API认证失败，请检查API密钥配置")
            raise

    async def create_template_entryTable(self, createNeed, llm, db: Optional[AsyncSession] = None) -> TemplateContentResponse:
        try:
            mylog.info("创建模板请求: %s", createNeed)
            # 从数据库获取提示词模板，支持示例输出
            example_output = getattr(createNeed, 'exampleOutput', None)
            prompt_template = await get_template_generate_prompt(db=db, example_output=example_output)
            
            # === 使用传入的 llm 动态创建 template_generator ===
            dynamic_template_generator = (
                {"titleName": RunnablePassthrough(), "writingRequirement": RunnablePassthrough()} 
                | prompt_template 
                | llm 
                | extract_template_generate
            )
            markdown_result = await dynamic_template_generator.ainvoke({
                "titleName": createNeed.titleName,
                "writingRequirement": createNeed.writingRequirement
            })
            json_result = markdown_to_json(markdown_result)
            json_result_dict = json.loads(json_result)
            return json_result_dict
        except Exception as e:
            error_str = str(e)
            if "401" in error_str or "AuthenticationError" in error_str or "令牌状态不可用" in error_str:
                raise ValueError("AI模型API认证失败，请检查API密钥配置")
            raise
    
    async def refresh_template(self, refreshNeed: TemplateRefreshNeed) -> dict:
        try:
            mylog.info("刷新模板请求: %s", refreshNeed)
            titleData = json_to_markdown(refreshNeed.originalTemplate[0])
            markdown_result = await template_refresher.ainvoke({
                "titleName": refreshNeed.titleName,
                "writingRequirement": refreshNeed.writingRequirement,
                "originalTemplate": str(titleData)
            })
            json_result = markdown_to_json(get_original_template_or_markdown(markdown_result))
            json_result_dict = json.loads(json_result)
            return TemplateContentResponse(code=200, type="success", data=json_result_dict).dict()
        except json.JSONDecodeError as e:
            return self.log_and_return_error("解析 originalTemplate 时发生错误", e, 400)
        except Exception as e:
            return self.log_and_return_error("刷新模板时发生错误", e, 500)

    def log_and_return_error(self, message: str, exception: Exception, code: int):
        mylog.error(f"{message}: {str(exception)}", exc_info=True)
        return TemplateContentResponse(code=code, type="error", message=message).dict()
def get_original_template_or_markdown(markdown_result):
    try:
        # 尝试将字符串解析为 JSON
        data = json.loads(markdown_result)
        # 如果是字典类型，并且包含 originalTemplate 键
        if isinstance(data, dict) and 'originalTemplate' in data:
            # 返回 originalTemplate 的值
            return data['originalTemplate']
        else:
            # 如果不是预期的字典或者没有 originalTemplate 键，返回 None 或者错误信息
            return "JSON data does not contain 'originalTemplate' key."
    except json.JSONDecodeError:
        # 如果解析失败，假设它是 Markdown 格式
        # 直接返回原始的 markdown_result
        return markdown_result
        

