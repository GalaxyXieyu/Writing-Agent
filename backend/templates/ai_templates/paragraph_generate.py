from langchain_core.prompts import PromptTemplate

paragraph_generate_template = """
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
"""

paragraph_generate_prompt = PromptTemplate.from_template(paragraph_generate_template)

