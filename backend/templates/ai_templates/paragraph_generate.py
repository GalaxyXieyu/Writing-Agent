from langchain_core.prompts import PromptTemplate
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from services.prompt_config import get_prompt_by_type

# 参考输出最大字符数限制（避免 token 超限）
MAX_EXAMPLE_OUTPUT_CHARS = 3000


def truncate_example_output(text: str, max_chars: int = MAX_EXAMPLE_OUTPUT_CHARS) -> str:
    """
    智能截断参考输出，避免 token 超限。
    保留前后关键段落，中间用省略提示。
    """
    if not text or len(text) <= max_chars:
        return text
    
    # 保留前40%和后20%，中间截断
    front_chars = int(max_chars * 0.4)
    back_chars = int(max_chars * 0.2)
    
    front_part = text[:front_chars]
    back_part = text[-back_chars:] if back_chars > 0 else ""
    
    truncated = f"{front_part}\n\n... [内容过长，已截断 {len(text) - front_chars - back_chars} 字符] ...\n\n{back_part}"
    return truncated

# 默认提示词模板（作为回退）
paragraph_generate_template_default = """
## 角色：你是一个专业的文章创作智能体。根据【整体文章标题】，理解【本章要求】，编写该章节内容，确保自然融合且无冲突。
## 规则：
1- 严格按照【整体文章标题】和【本章要求】生成内容，字数丰富，内容有深度，引用数据和案例。
2- 分析文章类别，调用专业数据，确保内容专业。
3- 内容详细，呼应【上一章节内容】，有层次有深度。
4- 按照【本章要求】编写每个小章节，不漏写不多写。
5- 若提供【预期小节标题列表】，必须严格按该列表逐项写作，不新增、不少写、不更改顺序与名称。
6- 为每个章节标号，多级标号：1.1、xxxx；1.1.1、xxxx
7- **禁止自行拆分或细化大纲结构**：只按给定的章节层级输出内容，不要自动创建新的子标题或进一步细分章节。
8- **严格遵循已有大纲**：如果【预期小节标题列表】为空，则直接输出本章内容，不要自行添加任何层级的子标题。
9- **输出字数要求**：参考【参考输出】的字数和表述方式，保持相似的详细程度和篇幅长度。
参考：
    ## 1.1、xxx产品变化快
    ### 1.1.1、xxxx
    ## 7.1、软件成本
    ### 7.1.1、xxxx
    ## 7.2、硬件成本
    ### 7.2.1、xxxx
    ### 7.2.2、xxxx
    ## 7.3、其他成本

一定要严格遵守【本章标题】和【本章要求】章节标题的序号和格式，不要遗漏，不要多写，不要少写，不要自行细分。

##【整体文章标题】={complete_title}
##【上一章节内容】={last_para_content}
##【本章标题】={titleNames}
##【本章要求】={requirements}
##【预期小节标题列表】={expected_titles}
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

    # 处理示例输出：和模板生成保持一致的注入策略，并应用截断避免 token 超限
    if example_output and str(example_output).strip():
        # 截断过长的参考输出
        truncated_output = truncate_example_output(str(example_output).strip())
        section = f"\n## 示例输出：\n{truncated_output}\n"
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
