"""
数据库基础配置
只包含 Base 和共享的数据库配置
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
