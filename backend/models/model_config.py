from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from models.database import Base


class AiModelConfig(Base):
    """大模型配置表（不做加密，按 OpenAI 兼容字段存储）"""
    __tablename__ = "ai_model_config"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # user_id 为空表示全局配置
    user_id = Column(String(64), nullable=True, index=True)
    name = Column(String(128), nullable=False)  # 展示名称
    model = Column(String(128), nullable=False)  # 模型名，如 gpt-4o / qwen2.5-72b-instruct
    api_key = Column(String(512), nullable=False)
    base_url = Column(String(256), nullable=False)
    temperature = Column(String(16), nullable=True)  # 简化为字符串存储，便于直写
    max_tokens = Column(Integer, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    status_cd = Column(String(1), nullable=False, default='Y')  # Y/N
    remark = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ---- Pydantic 模型 ----

class ModelConfigBase(BaseModel):
    user_id: Optional[str] = Field(default=None, description="用户ID，空为全局")
    name: str = Field(description="配置名称")
    model: str = Field(description="模型名，如 gpt-4o 或 qwen2.5-72b-instruct")
    api_key: str = Field(description="OpenAI 兼容 API Key")
    base_url: str = Field(description="OpenAI 兼容 Base URL")
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    is_default: Optional[bool] = Field(default=False)
    status_cd: Optional[Literal['Y', 'N']] = Field(default='Y')
    remark: Optional[str] = None


class ModelConfigCreate(ModelConfigBase):
    pass


class ModelConfigUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None  # 为空表示不修改
    base_url: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    is_default: Optional[bool] = None
    status_cd: Optional[Literal['Y', 'N']] = None
    remark: Optional[str] = None


class ModelConfigQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    user_id: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    status_cd: Optional[Literal['Y', 'N']] = 'Y'


class ModelConfigResponse(BaseModel):
    id: int
    user_id: Optional[str]
    name: str
    model: str
    api_key: str
    base_url: str
    temperature: Optional[float]
    max_tokens: Optional[int]
    is_default: bool
    status_cd: str
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SetDefaultModelRequest(BaseModel):
    model_id: int
    user_id: Optional[str] = None
