from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text
from models.database import Base


class AiPromptConfig(Base):
    """AI提示词配置表"""
    __tablename__ = "ai_prompt_config"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    prompt_type = Column(String(64), nullable=False, unique=True, comment='提示词类型：template_generate/paragraph_generate/template_refresh')
    prompt_content = Column(Text, nullable=False, comment='提示词内容')
    status_cd = Column(String(1), nullable=False, default='Y', comment='状态：Y有效，N无效')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ---- Pydantic 模型 ----

class PromptConfigBase(BaseModel):
    prompt_type: str = Field(description="提示词类型：template_generate/paragraph_generate/template_refresh")
    prompt_content: str = Field(description="提示词内容")
    status_cd: Optional[Literal['Y', 'N']] = Field(default='Y', description="状态：Y有效，N无效")


class PromptConfigCreate(PromptConfigBase):
    pass


class PromptConfigUpdate(BaseModel):
    prompt_content: Optional[str] = None
    status_cd: Optional[Literal['Y', 'N']] = None


class PromptConfigResponse(BaseModel):
    id: int
    prompt_type: str
    prompt_content: str
    status_cd: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

