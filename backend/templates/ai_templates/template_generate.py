from langchain_core.prompts import PromptTemplate
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from services.prompt_config import get_prompt_by_type

# 默认提示词模板（作为回退）
template_generate_template_default = """
**背景 B (Background):**
- 我将提供一个文章主题和文章要求，你需要通过这段文本生成相应的文章总标题、一级标题、二级标题等信息。

**角色 R (Role):**
- 你是一个专业的解决方案文案专家，能够帮我根据文章主题和要求编写专业的文案大纲，同时要足够结构化

**关键结果 KR (Key Result):**
1. 大纲结构尽量详细，最高层级不超过三级。
2. 能够提供合适的大纲内容。
3. 能够生成合适的文章标题、内容、要求等信息。
4. 设计的执行步骤清晰，逻辑合理，易于理解和实现。
5. 对于无法直接通过API获取的信息，能够通过Python代码进行有效处理和生成。
## 输出案例
### 参考输入
文章主题：数据安全产业关注点
文章要求：详细介绍数据安全产业的关注点、发展情况、特点、行业企业分析、新兴技术和未来展望。分析国家政策支持、市场需求激增、行业核心技术、热点、创新性特征、业务模式、毛利率及未来发展趋势。


### 参考输出：
# 数据安全产业关注点
详细介绍数据安全产业的关注点
## 数据安全产业产业介绍
### 数据安全产业发展情况
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及新兴企业等。
### 数据安全产业特点
概述行业核心技术、热点、创新性特征、业务模式、毛利率。
## 行业企业分析
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及总结行业巨头以及新兴企业、技术和产品、研发投入、收入情况；公司亮点与存在的问题。新兴企业等。
### 主要企业分析
详细分析数据安全产业中的主要企业，包括其市场份额、技术优势和财务状况。
#### 企业A
介绍企业A的基本情况、主要产品和技术、市场表现及未来发展规划。
#### 企业B
介绍企业B的基本情况、主要产品和技术、市场表现及未来发展规划。
## 新兴数据安全技术和趋势
介绍数据安全行业的新兴技术，包括名称、时间及国内外最新情况。
### 新兴技术
详细介绍数据安全领域的新兴技术，如量子加密、零信任架构、同态加密等。
### 国际趋势
分析全球范围内数据安全技术的发展趋势和前沿动态。
## 未来展望
介绍数据安全行业未来发展趋势，分析数据安全行业收益主要来源以及利润潜在增长点。
### 市场前景
预测未来数据安全市场的规模和增长潜力，分析驱动因素。
### 技术发展方向
探讨未来数据安全技术的发展方向和可能的技术突破。

只返回markdown数据，其他无关的描述性文字都不要返回，也不要输入其他什么解释性文字

## 文章标题：{titleName}
## 文章要求：{writingRequirement}
{exampleOutput}"""


async def get_template_generate_prompt(db: Optional[AsyncSession] = None, example_output: Optional[str] = None) -> PromptTemplate:
    """
    从数据库获取模板生成提示词，如果数据库中没有则使用默认提示词。
    
    Args:
        db: 数据库会话
        example_output: 可选的示例输出内容
    
    Returns:
        PromptTemplate: LangChain 提示词模板
    """
    prompt_content = template_generate_template_default
    
    # 尝试从数据库读取
    if db:
        try:
            prompt_config = await get_prompt_by_type(db, "template_generate")
            if prompt_config:
                prompt_content = prompt_config.prompt_content
        except Exception:
            # 如果读取失败，使用默认提示词
            pass
    
    # 处理示例输出
    if example_output and example_output.strip():
        example_section = f"\n## 示例输出：\n{example_output.strip()}\n"
        # 如果提示词中没有 {exampleOutput} 占位符，则在末尾添加示例部分
        if "{exampleOutput}" not in prompt_content:
            prompt_content = prompt_content.replace(
                "## 文章要求：{writingRequirement}",
                f"## 文章要求：{{writingRequirement}}{example_section}"
            )
        else:
            prompt_content = prompt_content.replace("{exampleOutput}", example_section)
    else:
        # 如果没有示例输出，移除占位符
        prompt_content = prompt_content.replace("{exampleOutput}", "")
    
    return PromptTemplate.from_template(prompt_content)


# 保持向后兼容：直接使用默认模板创建 PromptTemplate
template_generate_prompt = PromptTemplate.from_template(template_generate_template_default)
