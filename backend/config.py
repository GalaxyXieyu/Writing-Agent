import os
import json
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

"""配置中心
优先级：环境变量 > config.json > 默认值
统一数据库/Redis 配置，避免各路由各自为政。
"""

# 数据库配置（环境变量优先）
_DS_URL = None
_DS_USER = None
_DS_PASSWORD = None

# 延迟加载 config.json
_CONFIG_JSON = None
try:
    config_path = Path(__file__).with_name("config.json")
    if config_path.exists():
        _CONFIG_JSON = json.loads(config_path.read_text(encoding="utf-8"))
except Exception:
    _CONFIG_JSON = None

def _cfg(path: str, default=None):
    if not _CONFIG_JSON:
        return default
    node = _CONFIG_JSON
    for key in path.split('.'):
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return default
    return node

def _parse_ds(url: str):
    """
    解析形如 "host:port/db" 的 datasource.url
    返回 (host, port, db)
    """
    try:
        host_port, db = url.split('/')
        host, port = host_port.split(':')
        return host, port, db
    except Exception:
        return None, None, None

# 读取环境变量或 config.json
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME]):
    # 从 config.json 的 datasource 兜底
    _DS_URL = _cfg("datasource.url")
    _DS_USER = _cfg("datasource.username")
    _DS_PASSWORD = _cfg("datasource.password")
    if _DS_URL and _DS_USER and _DS_PASSWORD:
        h, p, d = _parse_ds(_DS_URL)
        DB_HOST = DB_HOST or h
        DB_PORT = DB_PORT or p
        DB_USER = DB_USER or _DS_USER
        DB_PASSWORD = DB_PASSWORD or _DS_PASSWORD
        DB_NAME = DB_NAME or d

# 最终兜底默认值（开发本地）
DB_HOST = DB_HOST or "127.0.0.1"
DB_PORT = DB_PORT or "30306"
DB_USER = DB_USER or "root"
DB_PASSWORD = DB_PASSWORD or "123456"
DB_NAME = DB_NAME or "tianshu"

# 构建数据库连接字符串（统一使用 aiomysql）
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Redis 配置

REDIS_HOST = os.getenv("REDIS_HOST", _cfg("redis.host", "127.0.0.1"))
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

