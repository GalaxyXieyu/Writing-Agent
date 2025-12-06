"""
初始化脚本（仅保留新方式）：
- init_database：启动时自动创建缺失的数据表（包含 ai_model_config、ai_prompt_config 等 Base 关联表）
- 自动初始化默认提示词配置数据
"""

from models.database import Base
from config import get_db_engine
from sqlalchemy import text
from utils.logger import mylog


async def init_database():
    """创建缺失的数据表（包含 ai_model_config、ai_prompt_config 等）。
    依赖 SQLAlchemy Base 元数据，幂等执行。
    同时初始化默认提示词配置数据。
    自动执行数据库迁移（添加缺失的列）。
    """
    # 确保模型已注册到 Base.metadata
    # 仅需导入一次以触发表注册
    from models import model_config  # noqa: F401
    from models import prompt_config  # noqa: F401
    from models import auth  # noqa: F401  确保用户与邀请表注册
    from models import system_config  # noqa: F401  确保系统配置表注册
    
    engine = get_db_engine()
    async with engine.begin() as conn:
        # 使用同步 API 在异步连接中执行 metadata.create_all
        await conn.run_sync(Base.metadata.create_all)
        mylog.info("数据库表结构创建完成")
    
    # 执行数据库迁移（添加缺失的列）
    await migrate_database(engine)
    
    # 初始化默认提示词数据
    await init_default_prompts(engine)
    
    # 无异常则表示完成


async def migrate_database(engine):
    """执行数据库迁移，添加缺失的列（幂等执行）"""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            # 1) ai_user 表新增列：is_admin, parent_admin_id
            result = await session.execute(
                text("""
                    SELECT COLUMN_NAME FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ai_user'
                """)
            )
            cols = {row[0] for row in result.fetchall()}
            if 'is_admin' not in cols:
                mylog.info("添加 ai_user.is_admin 列...")
                await session.execute(
                    text("""
                        ALTER TABLE ai_user 
                        ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否管理员，1是，0否'
                        AFTER status
                    """)
                )
            if 'parent_admin_id' not in cols:
                mylog.info("添加 ai_user.parent_admin_id 列...")
                await session.execute(
                    text("""
                        ALTER TABLE ai_user 
                        ADD COLUMN parent_admin_id VARCHAR(255) NULL COMMENT '所属管理员用户ID（成员归属）'
                        AFTER is_admin
                    """)
                )

            # 管理员账号回填：若当前没有任何管理员用户，则将默认 admin 账户设为管理员
            try:
                result = await session.execute(
                    text("""
                        SELECT COUNT(*) FROM ai_user WHERE is_admin = 1
                    """)
                )
                admin_cnt = result.scalar() or 0
                if admin_cnt == 0:
                    mylog.info("未检测到管理员用户，尝试将 admin 账户设为管理员(is_admin=1)...")
                    await session.execute(
                        text("""
                            UPDATE ai_user 
                            SET is_admin = 1 
                            WHERE user_id = 'admin' OR username = 'admin'
                        """)
                    )
                    await session.commit()
            except Exception as e:
                mylog.error(f"管理员账号回填失败: {e}")
                await session.rollback()

            # 2) ai_invite 邀请表不存在则创建
            result = await session.execute(
                text("""
                    SELECT COUNT(*) FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ai_invite'
                """)
            )
            table_exists = result.scalar() > 0
            if not table_exists:
                mylog.info("创建表 ai_invite ...")
                await session.execute(
                    text("""
                        CREATE TABLE ai_invite (
                            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
                            code VARCHAR(64) NOT NULL UNIQUE COMMENT '邀请码',
                            admin_id VARCHAR(255) NOT NULL COMMENT '邀请方管理员用户ID',
                            status VARCHAR(16) NOT NULL DEFAULT 'unused' COMMENT '状态：unused/used/expired',
                            expire_time DATETIME NULL COMMENT '过期时间',
                            used_by_user_id VARCHAR(255) NULL COMMENT '被谁使用',
                            create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                            KEY idx_admin_id (admin_id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员邀请表'
                    """)
                )

            # 检查并添加 ai_create_template.example_output 列
            result = await session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'ai_create_template' 
                    AND COLUMN_NAME = 'example_output'
                """)
            )
            column_exists = result.scalar() > 0
            
            if not column_exists:
                mylog.info("添加 ai_create_template.example_output 列...")
                await session.execute(
                    text("""
                        ALTER TABLE ai_create_template 
                        ADD COLUMN example_output TEXT NULL COMMENT '示例输出内容'
                    """)
                )
                await session.commit()
                mylog.info("ai_create_template.example_output 列添加完成")
            else:
                mylog.info("ai_create_template.example_output 列已存在，跳过迁移")
                
            # 3) 调整 ai_solution_save 表结构：solution_id -> VARCHAR(20)，日期列为 DATETIME
            try:
                result = await session.execute(
                    text("""
                        SELECT DATA_TYPE, COLUMN_NAME 
                        FROM information_schema.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE() 
                        AND TABLE_NAME = 'ai_solution_save'
                    """)
                )
                rows = result.fetchall()
                if rows:
                    cols = {row[1]: row[0] for row in rows}
                    # solution_id: 若不是 varchar，则修改
                    if 'solution_id' in cols and cols['solution_id'].lower() not in ('varchar', 'char', 'text'):
                        mylog.info("修改 ai_solution_save.solution_id 为 VARCHAR(20)...")
                        await session.execute(
                            text("""
                                ALTER TABLE ai_solution_save 
                                MODIFY COLUMN solution_id VARCHAR(20) NOT NULL COMMENT '方案ID'
                            """)
                        )
                    # create_date -> DATETIME NOT NULL
                    if 'create_date' in cols and cols['create_date'].lower() != 'datetime':
                        mylog.info("修改 ai_solution_save.create_date 为 DATETIME...")
                        await session.execute(
                            text("""
                                ALTER TABLE ai_solution_save 
                                MODIFY COLUMN create_date DATETIME NOT NULL COMMENT '创建时间'
                            """)
                        )
                    # update_date -> DATETIME NULL
                    if 'update_date' in cols and cols['update_date'].lower() != 'datetime':
                        mylog.info("修改 ai_solution_save.update_date 为 DATETIME...")
                        await session.execute(
                            text("""
                                ALTER TABLE ai_solution_save 
                                MODIFY COLUMN update_date DATETIME NULL COMMENT '更新时间'
                            """)
                        )
                    await session.commit()
                else:
                    mylog.info("表 ai_solution_save 不存在或无列信息，跳过结构调整")
            except Exception as e:
                mylog.error(f"调整 ai_solution_save 表结构失败: {e}")
                await session.rollback()

        except Exception as e:
            mylog.error(f"数据库迁移失败: {str(e)}")
            # 不抛出异常，避免影响应用启动
            await session.rollback()


async def init_default_prompts(engine):
    """初始化默认提示词配置数据（幂等执行）"""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            # 检查是否已有提示词配置
            result = await session.execute(
                text("SELECT COUNT(*) FROM ai_prompt_config WHERE prompt_type IN ('template_generate', 'paragraph_generate', 'template_refresh')")
            )
            count = result.scalar()
            
            if count == 0:
                mylog.info("开始初始化默认提示词配置...")
                
                # 默认提示词内容
                default_prompts = [
                    {
                        'prompt_type': 'template_generate',
                        'prompt_content': '''**背景 B (Background):**
- 我将提供一个文章主题和文章要求，你需要通过这段文本生成相应的文章总标题、一级标题、二级标题等信息。

**角色 R (Role):**
- 你是一个专业的解决方案文案专家，能够帮我根据文章主题和要求编写专业的文案大纲，同时要足够结构化

**关键结果 KR (Key Result):**
1. 大纲结构尽量详细，最高层级不超过三级。
2. 能够提供合适的大纲内容。
3. 能够生成合适的文章标题、内容、要求等信息。
4. 设计的执行步骤清晰，逻辑合理，易于理解和实现。
5. 对于无法直接通过API获取的信息，能够通过Python代码进行有效处理和生成。
## 输出案例
### 参考输入
文章主题：数据安全产业关注点
文章要求：详细介绍数据安全产业的关注点、发展情况、特点、行业企业分析、新兴技术和未来展望。分析国家政策支持、市场需求激增、行业核心技术、热点、创新性特征、业务模式、毛利率及未来发展趋势。


### 参考输出：
# 数据安全产业关注点
详细介绍数据安全产业的关注点
## 数据安全产业产业介绍
### 数据安全产业发展情况
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及新兴企业等。
#### 国家政策
详细描述国家在数据安全方面的政策，包括法律法规、行政命令和指导意见等。
#### 市场需求
分析市场对数据安全的需求，包含不同领域如金融、医疗、政府等的具体需求。
#### 市场规模与增速
提供市场规模的具体数据和年增长率，分析其变化趋势。
### 数据安全产业特点
概述行业核心技术、热点、创新性特征、业务模式、毛利率。
#### 核心技术
介绍数据安全产业的核心技术，如加密算法、区块链技术、人工智能在数据安全中的应用等。
#### 行业热点
分析当前数据安全产业的热点问题，如数据隐私保护、GDPR合规、云安全等。
## 行业企业分析
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及总结行业巨头以及新兴企业、技术和产品、研发投入、收入情况；公司亮点与存在的问题。新兴企业等。
### 主要企业分析
详细分析数据安全产业中的主要企业，包括其市场份额、技术优势和财务状况。
#### 企业A
介绍企业A的基本情况、主要产品和技术、市场表现及未来发展规划。
#### 企业B
介绍企业B的基本情况、主要产品和技术、市场表现及未来发展规划。
## 新兴数据安全技术和趋势
介绍数据安全行业的新兴技术，包括名称、时间及国内外最新情况。
### 新兴技术
详细介绍数据安全领域的新兴技术，如量子加密、零信任架构、同态加密等。
### 国际趋势
分析全球范围内数据安全技术的发展趋势和前沿动态。
## 未来展望
介绍数据安全行业未来发展趋势，分析数据安全行业收益主要来源以及利润潜在增长点。
### 市场前景
预测未来数据安全市场的规模和增长潜力，分析驱动因素。
### 技术发展方向
探讨未来数据安全技术的发展方向和可能的技术突破。

只返回markdown数据，其他无关的描述性文字都不要返回，也不要输入其他什么解释性文字

## 文章标题：{titleName}
## 文章要求：{writingRequirement}
{exampleOutput}''',
                        'status_cd': 'Y'
                    },
                    {
                        'prompt_type': 'paragraph_generate',
                        'prompt_content': '''## 角色：你是一个专业的文章创作智能体。根据【整体文章标题】，理解【本章要求】，编写该章节内容，确保自然融合且无冲突。
## 规则：
1- 严格按照【整体文章标题】和【本章要求】生成内容，字数丰富，内容有深度，引用数据和案例。
2- 分析文章类别，调用专业数据，确保内容专业。
3- 内容详细，呼应【上一章节内容】，有层次有深度。
4- 按照【本章要求】编写每个小章节，不漏写不多写。
5- 若提供【预期小节标题列表】，必须严格按该列表逐项写作，不新增、不少写、不更改顺序与名称。
6- 为每个章节标号，多级标号：1.1、xxxx；1.1.1、xxxx
7- **禁止自行拆分或细化大纲结构**：只按给定的章节层级输出内容，不要自动创建新的子标题或进一步细分章节。
8- **严格遵循已有大纲**：如果【预期小节标题列表】为空，则直接输出本章内容，不要自行添加任何层级的子标题。
9- **输出字数要求**：参考【参考输出】的字数和表述方式，保持相似的详细程度和篇幅长度。
参考：
    ## 1.1、xxx产品变化快
    ### 1.1.1、xxxx
    ## 7.1、软件成本
    ### 7.1.1、xxxx
    ## 7.2、硬件成本
    ### 7.2.1、xxxx
    ### 7.2.2、xxxx
    ## 7.3、其他成本

一定要严格遵守【本章标题】和【本章要求】章节标题的序号和格式，不要遗漏，不要多写，不要少写，不要自行细分。

##【整体文章标题】={complete_title}
##【上一章节内容】={last_para_content}
##【本章标题】={titleNames}
##【本章要求】={requirements}
##【预期小节标题列表】={expected_titles}
{exampleOutput}''',
                        'status_cd': 'Y'
                    },
                    {
                        'prompt_type': 'template_refresh',
                        'prompt_content': '''**背景 B (Background):**
- 用户提供了一个现有的大纲，请你从自身的解决方案客户经理的角度出发，针对目前的大纲进行调整，生成一个新的符合要求的结构化大纲。输入和输出格式均为JSON，且必须严格遵守格式规范。

**角色 R (Role):**
- 你是解决方案客户经理，能够优化调整大纲的专家，熟悉JSON数据结构和逻辑层次，能够灵活处理修改意见并生成合适的输出。

**目标 O (Objective):**
- 根据用户提供的修改意见，对现有大纲进行有效修改，输出符合要求的JSON格式大纲。

**关键结果 KR (Key Result):**
1. 确保大纲结构清晰，符合用户的修改意见。
2. 输出的JSON格式正确，避免任何语法或结构性错误。
3. 输出的JSON与用户提供的初始大纲结构保持一致，逻辑合理。
4. 生成的JSON数据不需要换行

## 输出案例
## 参考原有标题：数据安全产业关注点
## 参考文章要求：详细介绍数据安全产业的关注点、发展情况、特点、行业企业分析、新兴技术和未来展望。分析国家政策支持、市场需求激增、行业核心技术、热点、创新性特征、业务模式、毛利率及未来发展趋势。
### 参考原有大纲：

# 数据安全产业关注点
详细介绍数据安全产业的关注点
## 数据安全产业产业介绍
### 数据安全产业发展情况
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及新兴企业等。
### 数据安全产业特点
概述行业核心技术、热点、创新性特征、业务模式、毛利率。
## 行业企业分析
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及总结行业巨头以及新兴企业、技术和产品、研发投入、收入情况；公司亮点与存在的问题。新兴企业等。
## 新兴数据安全技术和趋势
介绍数据安全行业的新兴技术，包括名称、时间及国内外最新情况。
## 未来展望
介绍数据安全行业未来发展趋势，分析数据安全行业收益主要来源以及利润潜在增长点。

### 优化后的大纲：

# 数据安全产业关注点
详细介绍数据安全产业的关注点
## 数据安全产业产业介绍
### 数据安全产业发展情况
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及新兴企业等。
#### 国家政策
详细描述国家在数据安全方面的政策，包括法律法规、行政命令和指导意见等。
#### 市场需求
分析市场对数据安全的需求，包含不同领域如金融、医疗、政府等的具体需求。
#### 市场规模与增速
提供市场规模的具体数据和年增长率，分析其变化趋势。
### 数据安全产业特点
概述行业核心技术、热点、创新性特征、业务模式、毛利率。
#### 核心技术
介绍数据安全产业的核心技术，如加密算法、区块链技术、人工智能在数据安全中的应用等。
#### 行业热点
分析当前数据安全产业的热点问题，如数据隐私保护、GDPR合规、云安全等。
## 行业企业分析
总结数据安全产业国家政策、市场需求、市场规模、增速、分类、行业巨头以及总结行业巨头以及新兴企业、技术和产品、研发投入、收入情况；公司亮点与存在的问题。新兴企业等。
### 主要企业分析
详细分析数据安全产业中的主要企业，包括其市场份额、技术优势和财务状况。
#### 企业A
介绍企业A的基本情况、主要产品和技术、市场表现及未来发展规划。
#### 企业B
介绍企业B的基本情况、主要产品和技术、市场表现及未来发展规划。
## 新兴数据安全技术和趋势
介绍数据安全行业的新兴技术，包括名称、时间及国内外最新情况。
### 新兴技术
详细介绍数据安全领域的新兴技术，如量子加密、零信任架构、同态加密等。
### 国际趋势
分析全球范围内数据安全技术的发展趋势和前沿动态。
## 未来展望
介绍数据安全行业未来发展趋势，分析数据安全行业收益主要来源以及利润潜在增长点。
### 市场前景
预测未来数据安全市场的规模和增长潜力，分析驱动因素。
### 技术发展方向
探讨未来数据安全技术的发展方向和可能的技术突破。

只返回markdown数据，其他无关的描述性文字都不要返回，也不要输入其他什么解释性文字

## 文章标题：{titleName}
## 文章要求：{writingRequirement}
## 原有大纲：{original_template}''',
                        'status_cd': 'Y'
                    }
                ]
                
                # 批量插入
                for prompt_data in default_prompts:
                    await session.execute(
                        text("""
                            INSERT INTO ai_prompt_config (prompt_type, prompt_content, status_cd, created_at, updated_at)
                            VALUES (:prompt_type, :prompt_content, :status_cd, NOW(), NOW())
                        """),
                        prompt_data
                    )
                
                await session.commit()
                mylog.info("默认提示词配置初始化完成")
            else:
                mylog.info("提示词配置已存在，跳过初始化")
                
        except Exception as e:
            mylog.error(f"初始化提示词配置失败: {str(e)}")
            # 不抛出异常，避免影响应用启动
            await session.rollback()