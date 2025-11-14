from typing import List, Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.model_config import (
    AiModelConfig,
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigQuery,
)


async def create_model_config(db: AsyncSession, data: ModelConfigCreate) -> AiModelConfig:
    """创建模型配置。"""
    obj = AiModelConfig(
        user_id=data.user_id,
        name=data.name,
        model=data.model,
        api_key=data.api_key,
        base_url=data.base_url,
        temperature=str(data.temperature) if data.temperature is not None else None,
        max_tokens=data.max_tokens,
        is_default=bool(data.is_default),
        status_cd=data.status_cd or 'Y',
        remark=data.remark,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    # 如果设置了默认，则取消同用户其他默认
    if obj.is_default:
        await _unset_others_default(db, obj)

    return obj


async def get_model_config(db: AsyncSession, model_id: int) -> Optional[AiModelConfig]:
    stmt = select(AiModelConfig).where(AiModelConfig.id == model_id, AiModelConfig.status_cd == 'Y')
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def list_model_configs(db: AsyncSession, q: ModelConfigQuery) -> Tuple[List[AiModelConfig], int]:
    stmt = select(AiModelConfig)
    if q.status_cd:
        stmt = stmt.where(AiModelConfig.status_cd == q.status_cd)
    if q.user_id is not None:
        stmt = stmt.where(AiModelConfig.user_id == q.user_id)
    if q.name:
        stmt = stmt.where(AiModelConfig.name.like(f"%{q.name}%"))
    if q.model:
        stmt = stmt.where(AiModelConfig.model.like(f"%{q.model}%"))

    # 总数
    total = len((await db.execute(stmt)).scalars().all())

    # 分页
    offset = (q.page - 1) * q.page_size
    stmt = stmt.offset(offset).limit(q.page_size)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return rows, total


async def update_model_config(db: AsyncSession, model_id: int, data: ModelConfigUpdate) -> Optional[AiModelConfig]:
    obj = await get_model_config(db, model_id)
    if not obj:
        return None
    # 仅更新提供的字段
    if data.name is not None:
        obj.name = data.name
    if data.model is not None:
        obj.model = data.model
    if data.api_key is not None:  # 允许留空以跳过
        obj.api_key = data.api_key
    if data.base_url is not None:
        obj.base_url = data.base_url
    if data.temperature is not None:
        obj.temperature = str(data.temperature)
    if data.max_tokens is not None:
        obj.max_tokens = data.max_tokens
    if data.is_default is not None:
        obj.is_default = bool(data.is_default)
    if data.status_cd is not None:
        obj.status_cd = data.status_cd
    if data.remark is not None:
        obj.remark = data.remark

    await db.commit()
    await db.refresh(obj)

    # 若被设置为默认，取消同用户其他默认
    if obj.is_default:
        await _unset_others_default(db, obj)

    # 配置更新后清理对应模型的缓存，确保新配置（base_url/api_key 等）立即生效
    try:
        # 延迟导入以避免循环依赖
        from ai.llm.llm_factory import LLMFactory
        LLMFactory.clear_cache(model_id)
    except Exception:
        pass

    return obj


async def delete_model_config(db: AsyncSession, model_id: int) -> bool:
    obj = await get_model_config(db, model_id)
    if not obj:
        return False
    obj.status_cd = 'N'
    obj.is_default = False
    await db.commit()
    # 清理缓存
    try:
        from ai.llm.llm_factory import LLMFactory
        LLMFactory.clear_cache(model_id)
    except Exception:
        pass
    return True


async def set_default_model(db: AsyncSession, model_id: int) -> Optional[AiModelConfig]:
    obj = await get_model_config(db, model_id)
    if not obj:
        return None
    obj.is_default = True
    await db.commit()
    await _unset_others_default(db, obj)
    await db.refresh(obj)
    # 清理缓存，避免仍使用旧默认
    try:
        from ai.llm.llm_factory import LLMFactory
        LLMFactory.clear_cache(model_id)
    except Exception:
        pass
    return obj


async def get_default_model(db: AsyncSession, user_id: Optional[str] = None) -> Optional[AiModelConfig]:
    # 优先用户级默认
    if user_id is not None:
        stmt = select(AiModelConfig).where(
            AiModelConfig.user_id == user_id,
            AiModelConfig.is_default == True,
            AiModelConfig.status_cd == 'Y',
        )
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        if row:
            return row
    # 回退全局默认
    stmt = select(AiModelConfig).where(
        AiModelConfig.user_id.is_(None),
        AiModelConfig.is_default == True,
        AiModelConfig.status_cd == 'Y',
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def _unset_others_default(db: AsyncSession, obj: AiModelConfig) -> None:
    """取消同 user_id 下其他配置的默认标记（包含全局与用户各自域独立）。"""
    stmt = (
        update(AiModelConfig)
        .where(
            AiModelConfig.id != obj.id,
            AiModelConfig.status_cd == 'Y',
            (AiModelConfig.user_id == obj.user_id) if obj.user_id is not None else AiModelConfig.user_id.is_(None),
        )
        .values(is_default=False)
    )
    await db.execute(stmt)
    await db.commit()
