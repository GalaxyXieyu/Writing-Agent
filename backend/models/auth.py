from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Integer, TIMESTAMP, Boolean, DateTime
from models.database import Base
from datetime import datetime


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
    # 角色/组织
    is_admin = Column(Integer, default=0, comment='是否管理员，1是，0否')
    parent_admin_id = Column(String(255), nullable=True, comment='所属管理员用户ID（成员归属）')


class UserToken(Base):
    """用户Token表"""
    __tablename__ = 'ai_user_token'
    
    token_id = Column(Integer, primary_key=True, autoincrement=True, comment='Token主键')
    user_id = Column(String(255), nullable=False, comment='用户ID')
    token = Column(String(255), nullable=False, unique=True, comment='Token值')
    expire_time = Column(TIMESTAMP, nullable=False, comment='过期时间')
    create_time = Column(TIMESTAMP, nullable=False, comment='创建时间')


class AdminInvite(Base):
    """管理员邀请表"""
    __tablename__ = 'ai_invite'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    code = Column(String(64), nullable=False, unique=True, comment='邀请码')
    admin_id = Column(String(255), nullable=False, comment='邀请方管理员用户ID')
    status = Column(String(16), default='unused', comment="状态：unused/used/expired")
    expire_time = Column(DateTime, nullable=True, comment='过期时间')
    used_by_user_id = Column(String(255), nullable=True, comment='被谁使用')
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')


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


class RegisterAdminRequest(BaseModel):
    """注册管理员请求"""
    username: str
    password: str
    admin_code: Optional[str] = None


class RegisterWithInviteRequest(BaseModel):
    """使用邀请码注册成员请求"""
    username: str
    password: str
    invite_code: str


class CreateInviteRequest(BaseModel):
    """创建邀请码请求（管理员）"""
    expire_hours: Optional[int] = Field(default=24, description='过期小时数，默认24h')


class ResetPasswordRequest(BaseModel):
    user_id: str
    new_password: str


class SetUserStatusRequest(BaseModel):
    user_id: str
    status: str  # 'Y' or 'N'


class AdminRecordsQuery(BaseModel):
    member_user_id: Optional[str] = None
    member_phone: Optional[str] = None
    type: Optional[str] = Field(default=None, description='solution|file')
    kw: Optional[str] = None
    time_from: Optional[str] = None  # 'YYYY-MM-DD'
    time_to: Optional[str] = None
    pageNum: Optional[int] = 1
    pageSize: Optional[int] = 20

