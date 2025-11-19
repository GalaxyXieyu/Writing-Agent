from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text
from models.database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    config_key = Column(String(128), nullable=False, unique=True, index=True, comment="配置键")
    config_value = Column(Text, nullable=True, comment="配置值")
    remark = Column(String(255), nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ---- Pydantic 模型 ----

class SystemConfigBase(BaseModel):
    config_key: str = Field(description="配置键")
    config_value: Optional[str] = Field(default=None, description="配置值")
    remark: Optional[str] = Field(default=None, description="备注")


class SystemConfigUpdate(BaseModel):
    config_value: Optional[str] = Field(default=None, description="配置值")
    remark: Optional[str] = Field(default=None, description="备注")



