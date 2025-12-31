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
# 注意：标题由代码自动生成，大模型只需生成正文内容
paragraph_generate_template_default = """## 角色
你是一个专业的学术论文写作智能体。

## 任务
根据【本章标题】和【本章要求】，直接输出该章节的**正文内容**。

##【整体文章标题】={complete_title}
##【上一章节内容】={last_para_content}
##【本章标题】={titleNames}
##【本章要求】={requirements}
{exampleOutput}

## 核心规则
1. **只输出正文内容**：不要输出任何标题、编号或Markdown标题标记（如#、##等），标题由系统自动生成
2. **学术严谨性**：内容必须严谨、专业、有深度，使用学术化的表达方式，适当引用数据和研究案例
3. **上下文连贯**：内容需呼应【上一章节内容】，保持全文逻辑连贯
4. **直接开始**：直接输出正文段落，不要任何开头语或引导词

## 示例输出参考要求（最高优先级）
**【重要】若提供了【示例输出】，你的输出必须在各方面与示例高度一致：**
1. **字数长度**：输出字数必须与示例字数基本相同（误差控制在10%以内）
2. **语气风格**：完全模仿示例的学术语气和表达风格
3. **结构层次**：严格参考示例的段落组织、论述逻辑和行文结构
4. **详细程度**：信息密度、展开深度、论证方式必须与示例保持一致
5. **专业术语**：使用与示例一致的专业术语和表达习惯

**示例输出是你的写作标杆，请仔细分析示例后再输出。**
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
    import logging
    logger = logging.getLogger(__name__)

    prompt_content = paragraph_generate_template_default
    prompt_source = "默认提示词(fallback)"

    # 尝试从数据库读取
    if db:
        try:
            prompt_config = await get_prompt_by_type(db, "paragraph_generate")
            if prompt_config:
                prompt_content = prompt_config.prompt_content
                prompt_source = f"数据库(ID:{prompt_config.id})"
            else:
                logger.warning(f"⚠️ 数据库中未找到 paragraph_generate，使用默认")
        except Exception as e:
            logger.error(f"❌ 数据库读取失败: {str(e)}")

    # 简化日志输出
    logger.info(f"📝 [提示词] 来源: {prompt_source}, 长度: {len(prompt_content)}字符")

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
