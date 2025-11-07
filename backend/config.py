import os
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "30306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "tianshu")

# 构建数据库连接字符串
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Redis 配置
# 优先使用环境变量；未设置时尝试从同目录 config.json 读取，避免环境不一致导致 Celery/后端连接不同 Redis。
_CONFIG_JSON = None
try:
    config_path = Path(__file__).with_name("config.json")
    if config_path.exists():
        _CONFIG_JSON = json.loads(config_path.read_text(encoding="utf-8"))
except Exception:
    _CONFIG_JSON = None

def _cfg(path: str, default=None):
    # 从嵌套 dict 中读取，path 形如 "redis.host"
    if not _CONFIG_JSON:
        return default
    node = _CONFIG_JSON
    for key in path.split('.'):
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return default
    return node

REDIS_HOST = os.getenv("REDIS_HOST", _cfg("redis.host", "localhost"))
REDIS_PORT = int(os.getenv("REDIS_PORT", str(_cfg("redis.port", "6379"))))
REDIS_DB = int(os.getenv("REDIS_DB", str(_cfg("redis.db", "0"))))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", _cfg("redis.password", None))

# Redis URL for Celery（broker）
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Celery 配置（与 Redis 使用同一实例，结果后端放 DB 1）
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
if REDIS_PASSWORD:
    CELERY_RESULT_BACKEND = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1"

# 创建异步数据库引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db_engine():
    """获取数据库引擎"""
    return engine

