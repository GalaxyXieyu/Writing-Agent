from pydantic import BaseModel, Field
from typing import Optional, List, Any
from sqlalchemy import Column, String, Integer, Text, DateTime
from models.database import Base
from .templates import TemplateChild, TemplateData


# SQLAlchemy 数据库模型
class AiSolutionSave(Base):
    """方案保存信息表"""
    __tablename__ = 'ai_solution_save'
    
    # 使用业务自生成主键：YYYYMMDD + 4位序列，例如 202511140001
    solution_id = Column(String(20), primary_key=True, nullable=False, comment='方案ID')
    solution_title = Column(String(255), nullable=False, comment='方案标题')
    solution_content = Column(Text, nullable=False, comment='方案内容')
    create_phone = Column(String(255), comment='创建人手机号')
    create_name = Column(String(255), comment='创建人姓名')
    create_date = Column(DateTime, nullable=False, comment='创建时间')
    update_phone = Column(String(255), comment='更新人手机号')
    update_name = Column(String(255), comment='更新人姓名')
    update_date = Column(DateTime, comment='更新时间')
    status_cd = Column(String(255), nullable=False, comment='状态，Y有效，N无效')


# Pydantic 请求/响应模型
class ChapterGenerationRequest(BaseModel):
    chapter: TemplateChild
    last_para_content: str = Field(default="", description="上一段落的内容")
    modelId: int = Field(description="使用的模型配置ID")


class ArticleGenerationRequest(BaseModel):
    outline: TemplateData
    templateId: Optional[str] = None
    userId: Optional[str] = None
    modelId: int = Field(description="使用的模型配置ID")


class GenerationResponse(BaseModel):
    code: int = Field(description="状态码")
    message: Optional[str] = Field(None, description="消息")
    type: str = Field(description="响应类型")
    data: str = Field(description="生成的内容")


class StreamGenerationResponse(BaseModel):
    code: int = Field(description="状态码")
    message: Optional[str] = Field(None, description="消息")
    type: str = Field(description="响应类型")
    data: str = Field(description="当前生成的部分内容")
    is_end: bool = Field(description="是否是最后一个响应")


class saveSolution(BaseModel):
    solution_title: str
    solution_content: str
    create_phone: str
    create_name: str


class querySolution(BaseModel):
    create_phone: str
    solution_title: Optional[str] = None


class deleteSolution(BaseModel):
    solution_id: str


class updateSolution(BaseModel):
    solution_id: str
    solution_title: str
    solution_content: Optional[str] = None
    update_phone: str
    update_name: str


class querySolutionList(BaseModel):
    create_phone: str
    pageNum: int = None
    pageSize: int = None