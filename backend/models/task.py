"""
任务数据模型
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Index
from sqlalchemy.sql import func
from models.database import Base


class AiTask(Base):
    """任务表"""
    __tablename__ = 'ai_task'
    
    task_id = Column(String(64), primary_key=True, nullable=False)
    task_type = Column(String(50), nullable=False)
    user_id = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False)
    progress = Column(Integer, default=0)
    input_params = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )

