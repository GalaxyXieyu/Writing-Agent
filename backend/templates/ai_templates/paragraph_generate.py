from langchain_core.prompts import PromptTemplate
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from services.prompt_config import get_prompt_by_type

# 默认提示词模板（作为回退）
paragraph_generate_template_default = """
## 角色：你是一个专业的文章创作智能体。根据【整体文章标题】，理解【本章要求】，编写该章节内容，确保自然融合且无冲突。
## 规则：
1- 严格按照【整体文章标题】和【本章要求】生成内容，字数丰富，内容有深度，引用数据和案例。
2- 分析文章类别，调用专业数据，确保内容专业。
3- 内容详细，呼应【上一章节内容】，有层次有深度。
4- 按照【本章要求】编写每个小章节，不漏写不多写。
5- 为每个章节标号，多级标号：1.1、xxxx；1.1.1、xxxx
参考：
    ## 1.1、xxx产品变化快
    ### 1.1.1、xxxx
    ## 7.1、软件成本
    ### 7.1.1、xxxx
    ## 7.2、硬件成本
    ### 7.2.1、xxxx
    ### 7.2.2、xxxx
    ## 7.3、其他成本

一定要严格遵守【本章标题】和【本章要求】章节标题的序号和格式，不要遗漏，不要多写，不要少写。

##【整体文章标题】={complete_title}
##【上一章节内容】={last_para_content}
##【本章标题】={titleNames}
##【本章要求】={requirements}
{exampleOutput}
"""


async def get_paragraph_generate_prompt(db: Optional[AsyncSession] = None, example_output: Optional[str] = None) -> PromptTemplate:
    """
    从数据库获取文章生成提示词，如果数据库中没有则使用默认提示词。
    
    Args:
        db: 数据库会话
        example_output: 可选的章节级示例输出内容
    
    Returns:
        PromptTemplate: LangChain 提示词模板
    """
    prompt_content = paragraph_generate_template_default
    
    # 尝试从数据库读取
    if db:
        try:
            prompt_config = await get_prompt_by_type(db, "paragraph_generate")
            if prompt_config:
                prompt_content = prompt_config.prompt_content
        except Exception:
            # 如果读取失败，使用默认提示词
            pass

    # 处理示例输出：和模板生成保持一致的注入策略
    if example_output and str(example_output).strip():
        section = f"\n## 示例输出：\n{str(example_output).strip()}\n"
        if "{exampleOutput}" not in prompt_content:
            # 插到本章要求后面
            prompt_content = prompt_content.replace(
                "##【本章要求】={requirements}",
                f"##【本章要求】={{requirements}}{section}"
            )
        else:
            prompt_content = prompt_content.replace("{exampleOutput}", section)
    else:
        prompt_content = prompt_content.replace("{exampleOutput}", "")

    return PromptTemplate.from_template(prompt_content)


# 保持向后兼容：直接使用默认模板创建 PromptTemplate
paragraph_generate_prompt = PromptTemplate.from_template(paragraph_generate_template_default)

