#!/usr/bin/env python3
"""
提示词调试测试脚本
用于验证提示词是否正确从数据库加载，以及检查提示词内容
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from templates.ai_templates.paragraph_generate import get_paragraph_generate_prompt
from templates.ai_templates.template_generate import get_template_generate_prompt
from services.prompt_config import get_prompt_by_type
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库配置（从环境变量读取）
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://gmccai:123456@mysql:3306/tianshu")


async def test_prompt_loading():
    """测试提示词加载"""
    print("\n" + "="*80)
    print("🧪 提示词加载测试")
    print("="*80 + "\n")

    # 创建数据库连接
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("📦 测试1: 从数据库加载 paragraph_generate 提示词")
        print("-" * 80)

        # 直接查询数据库
        prompt_config = await get_prompt_by_type(session, "paragraph_generate")
        if prompt_config:
            print(f"✅ 数据库中找到配置 (ID: {prompt_config.id})")
            print(f"📝 提示词内容前500字符:")
            print(prompt_config.prompt_content[:500])
            print("...")

            # 检查关键字
            if "最高层级不超过三级" in prompt_config.prompt_content:
                print("⚠️  警告: 发现硬编码'三级'限制")
            if "1.1.1" in prompt_config.prompt_content:
                print("⚠️  警告: 发现三级标号示例 (1.1.1)")
            if "####" in prompt_config.prompt_content:
                print("⚠️  警告: 发现四级标题示例 (####)")
        else:
            print("❌ 数据库中未找到 paragraph_generate 配置")

        print("\n" + "-" * 80)
        print("📦 测试2: 通过函数加载 paragraph_generate 提示词")
        print("-" * 80)

        # 通过函数加载（会触发日志）
        prompt_template = await get_paragraph_generate_prompt(db=session)
        print(f"✅ 提示词模板加载成功")
        print(f"📝 模板变量: {prompt_template.input_variables}")

        print("\n" + "-" * 80)
        print("📦 测试3: 从数据库加载 template_generate 提示词")
        print("-" * 80)

        prompt_config = await get_prompt_by_type(session, "template_generate")
        if prompt_config:
            print(f"✅ 数据库中找到配置 (ID: {prompt_config.id})")
            print(f"📝 提示词内容前500字符:")
            print(prompt_config.prompt_content[:500])
            print("...")

            # 检查关键字
            if "最高层级不超过三级" in prompt_config.prompt_content:
                print("⚠️  警告: 发现硬编码'三级'限制")
            if "####" in prompt_config.prompt_content:
                print("⚠️  警告: 发现四级标题示例 (####)")
        else:
            print("❌ 数据库中未找到 template_generate 配置")

    await engine.dispose()

    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80 + "\n")


async def test_without_db():
    """测试不使用数据库时的默认提示词"""
    print("\n" + "="*80)
    print("🧪 默认提示词测试（无数据库连接）")
    print("="*80 + "\n")

    prompt_template = await get_paragraph_generate_prompt(db=None)
    print(f"✅ 默认提示词模板加载成功")
    print(f"📝 模板变量: {prompt_template.input_variables}")

    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🚀 开始提示词调试测试\n")

    # 测试1: 有数据库连接
    try:
        asyncio.run(test_prompt_loading())
    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)

    # 测试2: 无数据库连接
    try:
        asyncio.run(test_without_db())
    except Exception as e:
        logger.error(f"❌ 测试失败: {str(e)}", exc_info=True)

    print("\n✅ 所有测试完成\n")
