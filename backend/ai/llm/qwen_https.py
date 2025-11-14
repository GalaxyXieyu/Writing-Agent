"""
已移除的硬编码 HTTP 客户端。

请统一使用 ai.llm.llm_factory.LLMFactory。
"""

def get_llm(*_, **__):
    raise RuntimeError(
        "ai.llm.qwen_https 已废弃：请使用 ai.llm.llm_factory.LLMFactory。"
    )
