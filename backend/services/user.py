"""
用户管理服务
"""
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.auth import User
from utils.logger import mylog


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    name: str = None,
    phone: str = None
) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码（明文，生产环境应加密）
        name: 姓名
        phone: 手机号
        
    Returns:
        User对象
        
    Raises:
        ValueError: 用户名已存在
    """
    try:
        # 检查用户名是否已存在
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 生成用户ID
        user_id = str(uuid.uuid4())
        
        # 创建新用户
        new_user = User(
            user_id=user_id,
            username=username,
            password=password,  # 生产环境应使用 bcrypt 等加密
            name=name or username,
            phone=phone,
            create_time=datetime.now(),
            status='Y'
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        mylog.info(f"用户创建成功: {username} (ID: {user_id})")
        return new_user
        
    except ValueError:
        raise
    except Exception as e:
        mylog.error(f"创建用户失败: {str(e)}")
        await db.rollback()
        raise


async def get_user_by_username(db: AsyncSession, username: str):
    """
    根据用户名查询用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        User对象或None
    """
    try:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except Exception as e:
        mylog.error(f"查询用户失败: {str(e)}")
        return None


async def update_user(
    db: AsyncSession,
    user_id: str,
    name: str = None,
    phone: str = None,
    password: str = None
) -> User:
    """
    更新用户信息
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        name: 姓名
        phone: 手机号
        password: 新密码
        
    Returns:
        更新后的User对象
        
    Raises:
        ValueError: 用户不存在
    """
    try:
        stmt = select(User).where(User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("用户不存在")
        
        if name is not None:
            user.name = name
        if phone is not None:
            user.phone = phone
        if password is not None:
            user.password = password
        
        await db.commit()
        await db.refresh(user)
        
        mylog.info(f"用户信息更新成功: {user_id}")
        return user
        
    except ValueError:
        raise
    except Exception as e:
        mylog.error(f"更新用户失败: {str(e)}")
        await db.rollback()
        raise
