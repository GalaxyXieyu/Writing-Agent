import json
from models.templates import TemplateContentResponse, TemplateCreateNeed, TemplateRefreshNeed
from utils.template_load import markdown_to_json, json_to_markdown
from ai.agents import template_generator, template_refresher
from utils.logger import mylog  # 导入日志记录器

class TemplateService:
    def __init__(self):
        pass

    async def create_template(self, createNeed: TemplateCreateNeed) -> TemplateContentResponse:
        mylog.info("创建模板请求: %s", createNeed)
        markdown_result = await template_generator.ainvoke({
            "titleName": createNeed.titleName,
            "writingRequirement": createNeed.writingRequirement
        })
        json_result = markdown_to_json(markdown_result)
        json_result_dict = json.loads(json_result)
        return TemplateContentResponse(code=200, type="success", data=json_result_dict).dict()

    async def create_template_entryTable(self, createNeed) -> TemplateContentResponse:
        mylog.info("创建模板请求: %s", createNeed)
        markdown_result = await template_generator.ainvoke({
            "titleName": createNeed.titleName,
            "writingRequirement": createNeed.writingRequirement
        })
        json_result = markdown_to_json(markdown_result)
        json_result_dict = json.loads(json_result)
        return json_result_dict
    
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
        

