"""
初始化脚本（仅保留新方式）：
- init_database：启动时自动创建缺失的数据表（包含 ai_model_config 等 Base 关联表）
"""

from models.database import Base
from config import get_db_engine

async def init_database():
    """创建缺失的数据表（包含 ai_model_config）。
    依赖 SQLAlchemy Base 元数据，幂等执行。
    """
    # 确保模型已注册到 Base.metadata
    # 仅需导入一次以触发表注册
    from models import model_config  # noqa: F401
    engine = get_db_engine()
    async with engine.begin() as conn:
        # 使用同步 API 在异步连接中执行 metadata.create_all
        await conn.run_sync(Base.metadata.create_all)
    # 无异常则表示完成