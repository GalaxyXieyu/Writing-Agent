from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, Text, Date, BigInteger
from models.database import Base


# SQLAlchemy 数据库模型
class WritingTemplate(Base):
    """写作模板表"""
    __tablename__ = 'ai_writing_template'
    
    user_id = Column(String(255), comment='用户id')
    template_id = Column(Integer, primary_key=True, autoincrement=True, comment='模板编号')
    template_name = Column(String(255), comment='模板名称')
    template_type = Column(String(10), comment='模板类型,S-解决方案')
    template_desc = Column(String(255), comment='模板描述')
    status_cd = Column(String(1), comment='是否生效,Y有效,N无效')
    show_order = Column(Integer, comment='顺序')
    create_time = Column(Date, comment='创建时间')


class AiTemplateTitle(Base):
    """模板标题表"""
    __tablename__ = 'ai_template_title'
    
    title_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='标题编号')
    template_id = Column(BigInteger, comment='模板编号')
    parent_id = Column(BigInteger, comment='父标题编号')
    title_name = Column(String(255), comment='标题名称')
    show_order = Column(Integer, comment='顺序')
    writing_requirement = Column(String(2000), comment='写作要求')
    status_cd = Column(String(1), comment='有效性，Y有效，N无效')


class AICreateTemplate(Base):
    """AI生成模板表"""
    __tablename__ = 'ai_create_template'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    user_id = Column(String(255), nullable=False, comment='用户id')
    template_name = Column(String(255), comment='模板名称')
    create_template = Column(Text, comment='所生成模板')
    example_output = Column(Text, nullable=True, comment='示例输出内容')
    create_time = Column(Date, nullable=False, comment='生成时间')
    update_time = Column(Date, comment='更新时间')
    update_id = Column(String(255), comment='更新人')
    show_cd = Column(String(255), nullable=False, comment='模板是否有效（Y-有效，N-无效）')


class AIUsuallyTemplate(Base):
    """常用模板表"""
    __tablename__ = 'ai_usually_template'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    user_id = Column(String(255), nullable=False, comment='用户id')
    template_id = Column(String(255), comment='模板id')
    use_template = Column(Text, comment='使用的模板')
    use_count = Column(String(255), comment='使用次数')
    use_time = Column(Date, comment='最近使用时间')


# Pydantic 请求/响应模型
class TemplateCreateNeed(BaseModel):
    titleName: str
    writingRequirement: str


class TemplateRefreshNeed(BaseModel):
    titleName: str
    writingRequirement: Optional[str] = None
    originalTemplate: list


class Template(BaseModel):
    templateId: int
    templateName: str
    templateType: str
    templateDesc: str
    statusCd: str
    showOrder: int


class TemplateListResponse(BaseModel):
    code: int
    message: Optional[str] = None
    type: str
    data: List[Template]


class TemplateChild(BaseModel):
    titleId: Optional[int] = None
    templateId: Optional[int] = None
    parentId: Optional[int] = None
    titleName: str
    showOrder: Optional[int] = None
    writingRequirement: Optional[str] = None
    # 新增：章节级参考输出（可选），用于指导本章节生成
    referenceOutput: Optional[str] = None
    statusCd: Optional[str] = None
    children: Optional[List['TemplateChild']] = Field(default=None, allow_none=True)


class TemplateData(BaseModel):
    titleId: Optional[int] = None
    templateId: Optional[int] = None
    parentId: Optional[int] = None
    titleName: str
    showOrder: Optional[int] = None
    writingRequirement: Optional[str] = None
    # 新增：章节级参考输出（可选）
    referenceOutput: Optional[str] = None
    statusCd: Optional[str] = None
    children: Optional[List[TemplateChild]] = Field(default=None, allow_none=True)


class TemplateContentResponse(BaseModel):
    code: int
    message: Optional[str] = None
    type: str
    data: Dict[str, Any]


class TemplateQueryRequest(BaseModel):
    userId: str = None
    templateId: int = None


class TemplateSaveRequest(BaseModel):
    userId: str
    titleName: str
    writingRequirement: Optional[str] = None
    originalTemplate: list


class TemplateUpdateRequest(BaseModel):
    templateId: str
    userId: str
    titleName: str = None
    writingRequirement: Optional[str] = None
    originalTemplate: list = None


class TemplateCreate(BaseModel):
    titleName: str
    writingRequirement: str
    userId: str
    templateName: str
    modelId: Optional[int] = None
    exampleOutput: Optional[str] = None


class reTemplatename(BaseModel):
    id: int
    template_name: str = None


class deleteTemplate(BaseModel):
    id: int


class queryCreateTemplate(BaseModel):
    userId: str
    pageNum: int = None
    pageSize: int = None


class queryUsuallyTemplate(BaseModel):
    userId: str


class queryTempalteList(BaseModel):
    userId: str
    templateTitle: Optional[str] = None