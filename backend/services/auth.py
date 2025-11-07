import secrets
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.auth import User, UserToken
from utils.logger import mylog


async def verify_login(db: AsyncSession, username: str, password: str):
    """
    验证用户登录
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        User对象或None
    """
    try:
        stmt = select(User).where(
            User.username == username,
            User.password == password,
            User.status == 'Y'
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    except Exception as e:
        mylog.error(f"验证登录失败: {str(e)}")
        return None


def generate_token(user_id: str) -> str:
    """
    生成随机token
    
    Args:
        user_id: 用户ID
        
    Returns:
        32位随机token字符串
    """
    return secrets.token_hex(16)


async def save_token(db: AsyncSession, user_id: str, token: str) -> bool:
    """
    保存token到数据库
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        token: token值
        
    Returns:
        是否保存成功
    """
    try:
        expire_time = datetime.now() + timedelta(days=7)
        
        new_token = UserToken(
            user_id=user_id,
            token=token,
            expire_time=expire_time,
            create_time=datetime.now()
        )
        
        db.add(new_token)
        await db.commit()
        return True
    except Exception as e:
        mylog.error(f"保存token失败: {str(e)}")
        await db.rollback()
        return False


async def verify_token(db: AsyncSession, token: str):
    """
    验证token有效性
    
    Args:
        db: 数据库会话
        token: token值
        
    Returns:
        User对象或None
    """
    try:
        stmt = select(UserToken).where(
            UserToken.token == token,
            UserToken.expire_time > datetime.now()
        )
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            return None
        
        stmt = select(User).where(
            User.user_id == token_record.user_id,
            User.status == 'Y'
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        return user
    except Exception as e:
        mylog.error(f"验证token失败: {str(e)}")
        return None

