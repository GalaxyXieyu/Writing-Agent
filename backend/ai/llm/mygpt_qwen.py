"""
已移除的硬编码 OpenAI 客户端与直连示例。

请统一使用 ai.llm.llm_factory.LLMFactory。
"""

def get_llm(*_, **__):
    raise RuntimeError(
        "ai.llm.mygpt_qwen 已废弃：请使用 ai.llm.llm_factory.LLMFactory。"
    )