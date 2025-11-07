from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, TIMESTAMP
from models.database import Base


# SQLAlchemy 数据库模型
class User(Base):
    """用户表"""
    __tablename__ = 'ai_user'
    
    user_id = Column(String(255), primary_key=True, comment='用户ID')
    username = Column(String(255), nullable=False, unique=True, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码')
    phone = Column(String(100), comment='手机号')
    name = Column(String(255), comment='姓名')
    create_time = Column(TIMESTAMP, comment='创建时间')
    status = Column(String(10), default='Y', comment='状态，Y有效，N无效')


class UserToken(Base):
    """用户Token表"""
    __tablename__ = 'ai_user_token'
    
    token_id = Column(Integer, primary_key=True, autoincrement=True, comment='Token主键')
    user_id = Column(String(255), nullable=False, comment='用户ID')
    token = Column(String(255), nullable=False, unique=True, comment='Token值')
    expire_time = Column(TIMESTAMP, nullable=False, comment='过期时间')
    create_time = Column(TIMESTAMP, nullable=False, comment='创建时间')


# Pydantic 请求/响应模型
class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应模型"""
    code: int = Field(description="状态码")
    message: Optional[str] = Field(None, description="消息")
    type: str = Field(description="响应类型")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据")


class CheckTokenRequest(BaseModel):
    """Token验证请求模型"""
    key: str = Field(..., description="Token值")


class CheckTokenResponse(BaseModel):
    """Token验证响应模型"""
    code: int = Field(description="状态码")
    message: Optional[str] = Field(None, description="消息")
    type: str = Field(description="响应类型")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据")

