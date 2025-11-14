import threading
import time
from typing import Optional, Dict

from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from models.model_config import AiModelConfig
from services.model_config import get_model_config, get_default_model
from utils.logger import mylog


class LLMFactory:
    """
    简单的 LLM 工厂：
    - 统一使用 ChatOpenAI（OpenAI 兼容，支持自定义 base_url）
    - 基于 model_id 的实例缓存，带 TTL
    """

    _cache: Dict[int, Dict] = {}
    _lock = threading.Lock()
    _ttl_seconds = 15 * 60

    @classmethod
    def _make_llm(cls, cfg: AiModelConfig) -> ChatOpenAI:
        temperature = float(cfg.temperature) if cfg.temperature is not None else 0.2
        return ChatOpenAI(
            temperature=temperature,
            model=cfg.model,
            openai_api_key=cfg.api_key,
            openai_api_base=cfg.base_url,
            max_tokens=cfg.max_tokens
        )

    @classmethod
    def create_llm(cls, cfg: AiModelConfig, use_cache: bool = True) -> ChatOpenAI:
        now = time.time()
        if not use_cache:
            llm = cls._make_llm(cfg)
            cls._log_cfg(cfg, from_cache=False)
            return llm
        with cls._lock:
            entry = cls._cache.get(cfg.id)
            if entry and now - entry["ts"] < cls._ttl_seconds:
                cls._log_cfg(cfg, from_cache=True)
                return entry["llm"]
            llm = cls._make_llm(cfg)
            cls._cache[cfg.id] = {"llm": llm, "ts": now}
            cls._log_cfg(cfg, from_cache=False)
            return llm

    @staticmethod
    def _mask_key(key: str | None) -> str:
        if not key:
            return "<empty>"
        if len(key) <= 8:
            return key[0:2] + "****"
        return f"{key[:3]}****{key[-4:]}"

    @classmethod
    def _log_cfg(cls, cfg: AiModelConfig, from_cache: bool):
        try:
            mylog.info(
                "LLMFactory 使用模型: id=%s, name=%s, model=%s, base_url=%s, max_tokens=%s, temperature=%s, api_key=%s, from_cache=%s",
                getattr(cfg, 'id', None), getattr(cfg, 'name', None), getattr(cfg, 'model', None), getattr(cfg, 'base_url', None),
                getattr(cfg, 'max_tokens', None), getattr(cfg, 'temperature', None), cls._mask_key(getattr(cfg, 'api_key', None)), from_cache
            )
        except Exception:
            # 保底不让日志失败影响主流程
            pass

    @classmethod
    def clear_cache(cls, model_id: Optional[int] = None) -> None:
        with cls._lock:
            if model_id is None:
                cls._cache.clear()
            else:
                cls._cache.pop(model_id, None)

    @classmethod
    async def get_llm_by_id(cls, db: AsyncSession, model_id: int) -> Optional[ChatOpenAI]:
        cfg = await get_model_config(db, model_id)
        if not cfg:
            return None
        if cfg.status_cd != 'Y':
            return None
        return cls.create_llm(cfg, use_cache=True)

    @classmethod
    async def get_default_llm(cls, db: AsyncSession, user_id: Optional[str] = None) -> Optional[ChatOpenAI]:
        cfg = await get_default_model(db, user_id=user_id)
        if not cfg:
            return None
        return cls.create_llm(cfg, use_cache=True)
