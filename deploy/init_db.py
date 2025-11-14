"""
数据库初始化脚本
用于创建所有表结构并插入测试数据
"""
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

import asyncio
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models.database import Base
from models.auth import User, UserToken
from models.solution import AiSolutionSave
from models.templates import WritingTemplate, AiTemplateTitle, AICreateTemplate, AIUsuallyTemplate
from models.file import AiFileRel
from config import DATABASE_URL
from initialization import migrate_database, init_default_prompts

# 确保所有模型注册到 Base（包括新表）
from models import model_config  # noqa: F401
from models import prompt_config  # noqa: F401

async def init_database():
    """初始化数据库"""
    print("=" * 100)
    print("开始初始化数据库...")
    print(f"数据库连接: {DATABASE_URL}")
    print("=" * 100)
    
    # 创建数据库引擎
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True
    )
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            print("\n正在创建表结构...")
            await conn.run_sync(Base.metadata.create_all)
            print("表结构创建完成！")
        
        # 创建会话并插入测试数据
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            print("\n正在插入测试用户...")
            
            # 检查用户是否已存在
            result = await session.execute(
                text("SELECT COUNT(*) FROM ai_user WHERE user_id IN ('admin', 'test')")
            )
            count = result.scalar()
            
            if count == 0:
                # 插入测试用户（admin 直接为管理员）
                admin_user = User(
                    user_id='admin',
                    username='admin',
                    password='admin123',
                    phone='13800138000',
                    name='管理员',
                    create_time=datetime.now(),
                    status='Y'
                )
                setattr(admin_user, 'is_admin', 1)
                test_user = User(
                    user_id='test',
                    username='test',
                    password='test123',
                    phone='13900139000',
                    name='测试用户',
                    create_time=datetime.now(),
                    status='Y'
                )
                session.add_all([admin_user, test_user])
                await session.commit()
                print("测试用户创建成功！")
                print("\n测试账号信息：")
                print("  1. 用户名: admin, 密码: admin123")
                print("  2. 用户名: test, 密码: test123")
            else:
                print("测试用户已存在，跳过创建。")
        
        # 运行数据库迁移（新增列、缺失表等）
        print("\n执行数据库迁移（幂等）...")
        await migrate_database(engine)
        print("数据库迁移完成！")

        # 初始化提示词配置（幂等）
        print("\n初始化默认提示词配置（幂等）...")
        await init_default_prompts(engine)
        print("提示词配置初始化完成！")

        print("\n" + "=" * 100)
        print("数据库初始化完成！")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n数据库初始化失败: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())

