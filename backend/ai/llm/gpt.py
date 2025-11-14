"""
已移除的硬编码 LLM 定义。

请改用基于数据库模型配置的工厂：ai.llm.llm_factory.LLMFactory

示例：
    from ai.llm.llm_factory import LLMFactory
    llm = await LLMFactory.get_default_llm(db, user_id)
"""

def get_llm(*_, **__):
    raise RuntimeError(
        "ai.llm.gpt 已废弃：请使用 ai.llm.llm_factory.LLMFactory 从数据库配置创建 LLM。"
    )
