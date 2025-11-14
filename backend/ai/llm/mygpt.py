"""
已移除的硬编码 OpenAI/Azure 客户端封装。

请统一使用 ai.llm.llm_factory.LLMFactory。
"""

def get_llm(*_, **__):
    raise RuntimeError(
        "ai.llm.mygpt 已废弃：请使用 ai.llm.llm_factory.LLMFactory。"
    )
