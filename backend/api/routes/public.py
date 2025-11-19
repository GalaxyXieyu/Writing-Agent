"""
公共接口，无需登录即可访问
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import get_async_db
from models.system_config import SystemConfig
from api.routes.admin import json_ok

router = APIRouter()


@router.get("/public-configs")
async def get_public_configs(db: AsyncSession = Depends(get_async_db)):
    """获取公共配置信息"""
    # 定义哪些 key 是公共的
    public_keys = ['usage_doc_url']
    
    result = await db.execute(select(SystemConfig).where(SystemConfig.config_key.in_(public_keys)))
    configs = result.scalars().all()
    
    data = {c.config_key: c.config_value for c in configs}
    
    return json_ok(data)



