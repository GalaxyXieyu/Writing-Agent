"""
已移除的硬编码 LLM 定义。

请改用基于数据库模型配置的工厂：ai.llm.llm_factory.LLMFactory
"""

def get_llm(*_, **__):
    raise RuntimeError(
        "ai.llm.qwen 已废弃：请使用 ai.llm.llm_factory.LLMFactory 从数据库配置创建 LLM。"
    )
