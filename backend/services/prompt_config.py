from typing import List, Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.prompt_config import (
    AiPromptConfig,
    PromptConfigCreate,
    PromptConfigUpdate,
)


async def create_prompt_config(db: AsyncSession, data: PromptConfigCreate) -> AiPromptConfig:
    """创建提示词配置。"""
    obj = AiPromptConfig(
        prompt_type=data.prompt_type,
        prompt_content=data.prompt_content,
        status_cd=data.status_cd or 'Y',
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_prompt_config(db: AsyncSession, prompt_id: int) -> Optional[AiPromptConfig]:
    """根据ID获取提示词配置。"""
    stmt = select(AiPromptConfig).where(AiPromptConfig.id == prompt_id, AiPromptConfig.status_cd == 'Y')
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_prompt_by_type(db: AsyncSession, prompt_type: str) -> Optional[AiPromptConfig]:
    """根据类型获取提示词配置。"""
    stmt = select(AiPromptConfig).where(
        AiPromptConfig.prompt_type == prompt_type,
        AiPromptConfig.status_cd == 'Y'
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def list_prompt_configs(db: AsyncSession) -> List[AiPromptConfig]:
    """列出所有有效的提示词配置。"""
    stmt = select(AiPromptConfig).where(AiPromptConfig.status_cd == 'Y')
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_prompt_config(db: AsyncSession, prompt_id: int, data: PromptConfigUpdate) -> Optional[AiPromptConfig]:
    """更新提示词配置。"""
    obj = await get_prompt_config(db, prompt_id)
    if not obj:
        return None
    # 仅更新提供的字段
    if data.prompt_content is not None:
        obj.prompt_content = data.prompt_content
    if data.status_cd is not None:
        obj.status_cd = data.status_cd

    await db.commit()
    await db.refresh(obj)
    return obj


async def update_prompt_by_type(db: AsyncSession, prompt_type: str, data: PromptConfigUpdate) -> Optional[AiPromptConfig]:
    """根据类型更新提示词配置。"""
    obj = await get_prompt_by_type(db, prompt_type)
    if not obj:
        return None
    # 仅更新提供的字段
    if data.prompt_content is not None:
        obj.prompt_content = data.prompt_content
    if data.status_cd is not None:
        obj.status_cd = data.status_cd

    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_prompt_config(db: AsyncSession, prompt_id: int) -> bool:
    """删除提示词配置（软删除）。"""
    obj = await get_prompt_config(db, prompt_id)
    if not obj:
        return False
    obj.status_cd = 'N'
    await db.commit()
    return True

