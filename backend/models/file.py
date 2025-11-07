from pydantic import BaseModel
from typing import Optional, List, Union
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, BigInteger
from models.database import Base


# SQLAlchemy 数据库模型
class AiFileRel(Base):
    """文件关联表"""
    __tablename__ = 'ai_file_rel'
    
    file_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='附件主键')
    busi_id = Column(String(100), comment='业务标识')
    busi_code = Column(String(10), comment='业务类型')
    file_name = Column(String(1000), comment='原文件名称')
    file_page = Column(Integer, comment='页数')
    create_date = Column(TIMESTAMP, comment='上传时间')
    create_no = Column(String(100), comment='上传人')
    create_name = Column(String(100), comment='上传人名称')
    update_date = Column(TIMESTAMP, comment='修改时间')
    update_no = Column(String(100), comment='修改人')
    update_name = Column(String(100), comment='修改人名称')
    status_cd = Column(String(10), comment='状态，0等待解析，1解析完成，-1无效')
    remark = Column(String(255), comment='备注')
    file_url = Column(String(255), comment='文件地址')
    system_name = Column(String(100), comment='系统文件名称')
    data_path = Column(String(255), comment='文件路径')
    title_data = Column(Text, comment='文件解析标题数据')


# Pydantic 请求/响应模型
class FilePathRequest(BaseModel):
    filePath: str


class FileAnalysisResponse(BaseModel):
    code: int
    type: str
    pages: Optional[int]
    content: Union[str, List[str]]
    fileWords: int
    data: Optional[dict]
    error: Optional[str]


class Docx(BaseModel):
    html_content: str
    title: str


class reFilename(BaseModel):
    file_id: int
    file_name: str = None


class queryFile(BaseModel):
    busiId: str
    pageNum: int = None
    pageSize: int = None


class reAnalysisRequest(BaseModel):
    file_id: int


class deleteFile(BaseModel):
    file_id: int