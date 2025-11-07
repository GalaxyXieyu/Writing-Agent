import re
from datetime import datetime
import json
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_fixed
from api.routes.file import select_file_by_title
from models.templates import TemplateCreateNeed, TemplateListResponse, TemplateContentResponse, TemplateRefreshNeed
from services.templates import TemplateService
from utils.logger import mylog
from pydantic import ValidationError
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Date, and_, case, cast, create_engine, Column, Integer, String, delete, func, select, types
from sqlalchemy import or_, update, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from sqlalchemy.exc import SQLAlchemyError


# 创建一个FastAPI的APIRouter实例，用于定义模板相关的API路由
router = APIRouter()

# 创建一个模板服务实例，用于处理模板相关的业务逻辑
template_service = TemplateService()

@router.get("/templates", response_model=TemplateListResponse)
async def get_templates():
    """
    获取所有模板的列表

    这个API端点用于获取所有模板的列表。它会调用模板服务的get_templates方法，
    并返回一个TemplateListResponse对象，该对象包含所有模板的详细信息。

    Returns:
        TemplateListResponse: 包含所有模板的详细信息
    """
    mylog.info("*"*100)
    mylog.info("开始处理获取模板列表请求")
    return await template_service.get_templates()

@router.get("/templates/{templateId}", response_model=TemplateContentResponse)
async def get_template_content(templateId: int):
    """
    获取指定ID的模板内容

    这个API端点用于获取指定ID的模板内容。它会调用模板服务的get_template_content方法，
    并返回一个TemplateContentResponse对象。如果模板ID不存在，则会抛出404错误。

    Args:
        templateId (int): 模板的唯一标识符

    Returns:
        TemplateContentResponse: 包含模板内容的详细信息

    Raises:
        HTTPException: 如果模板ID不存在，则抛出404错误
    """
    mylog.info("*"*100)
    mylog.info(f"开始处理获取模板内容请求，模板ID: {templateId}")
    response = await template_service.get_template_content(templateId)
    if response.code == 404:
        raise HTTPException(status_code=404, detail="Template not found")
    return response

@router.post("/create", response_model=TemplateContentResponse)
async def create_template(request_data: TemplateCreateNeed, request: Request):
    """
    创建一个新的模板

    这个API端点用于创建一个新的模板。它会调用模板服务的create_template方法，
    并返回一个TemplateContentResponse对象，该对象包含新创建的模板的详细信息。

    Args:
        request_data (TemplateCreateNeed): 包含创建模板所需的数据
        request (Request): 请求对象，用于获取客户端的IP地址

    Returns:
        TemplateContentResponse: 包含新创建的模板的详细信息
    """
    mylog.info("*"*100)    
    mylog.info(f"开始处理生成模板请求，源IP: {request.client.host}")
    mylog.info(f"请求数据: {request_data}")
    try:
        # 调用模板服务的create_template方法，并获取返回的数据
        data = await template_service.create_template(request_data)
        response = TemplateContentResponse(code=200, message="模板创建成功", type="success", data=data)
        mylog.info(f"模板创建成功: {response}")
        return response
    except ValidationError as e:
        mylog.error(f"数据验证错误: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        mylog.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/refresh", response_model=TemplateContentResponse)
async def refresh_template(request: Request, refreshNeed: TemplateRefreshNeed):
    """
    刷新现有的模板

    这个API端点用于刷新现有的模板。它会调用模板服务的refresh_template方法，
    并返回一个TemplateContentResponse对象，该对象包含刷新后的模板的详细信息。

    Args:
        request (Request): 请求对象，用于获取客户端的IP地址
        refreshNeed (TemplateRefreshNeed): 包含需要刷新的模板数据
    Returns:
        TemplateContentResponse: 包含刷新后的模板的详细信息
    """
    mylog.info("*"*100)
    mylog.info(f"开始处理刷新模板请求，源IP: {request.client.host}")
    mylog.info(f"请求数据: {refreshNeed}")
    try:
        # 调用模板服务的refresh_template方法，并获取返回的数据
        data = await template_service.refresh_template(refreshNeed)
        response = TemplateContentResponse(code=200, message="模板刷新成功", type="success", data=data)
        return response
    except ValidationError as e:
        mylog.error(f"数据验证错误: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        mylog.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
Base = declarative_base()
class WritingTemplate(Base):
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
    __tablename__ = 'ai_template_title'
    title_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='标题编号')
    template_id = Column(BigInteger, comment='模板编号')
    parent_id = Column(BigInteger, comment='父标题编号')
    title_name = Column(String(255), comment='标题名称')
    show_order = Column(Integer, comment='顺序')
    writing_requirement = Column(String(2000), comment='写作要求')
    status_cd = Column(String(1), comment='有效性，Y有效，N无效')

# 创建异步数据库引擎
engine = create_async_engine(
    "mysql+aiomysql://gmccai:LPDY!iLrUd8irpGp@36.137.180.157:3306/tianshu",
    echo=True,
    pool_pre_ping=True,  # 在获取连接之前检查连接是否有效
    pool_size=10,        # 设置连接池大小
    max_overflow=20,     # 设置最大溢出连接数
    pool_timeout=30,     # 设置连接池超时时间
)

# 创建数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 依赖项函数，为每个请求单独创建和关闭会话
# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 创建会话类
Session = sessionmaker(bind=engine)


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
    originalTemplate: list = None  # 将 originalTemplate 类型改为 Any


# 创建会话
session = Session()

# 重试装饰器配置
# stop=stop_after_attempt(3) 表示最多重试3次
# wait=wait_fixed(2) 表示每次重试之间等待1秒
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def execute_query_with_retry(db: AsyncSession, stmt):
    try:
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        mylog.error(f"查询失败，将重试: {str(e)}")
        raise  # 重新抛出异常以触发重试

@router.post("/templateQuery")
async def template_query(request_data: TemplateQueryRequest,db: AsyncSession = Depends(get_async_db)):
    try:
        stmt = select(WritingTemplate).filter(
            or_(WritingTemplate.user_id == request_data.userId, WritingTemplate.user_id == '0')
            & (WritingTemplate.status_cd == "Y")
        )

        results = await execute_query_with_retry(db, stmt)

        # 执行查询并返回结果
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": f"查询成功", "type": "success", "data": results})
        )
    except Exception as e:
        error_msg = f"模板查询接口发生异常: {str(e)}"
        mylog.error(error_msg)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"查询失败，请重试或联系系统管理员", "type": "failed"})
        )

@router.post("/templateSave")
async def template_save(request_data: TemplateSaveRequest,db: AsyncSession = Depends(get_async_db)):
    try:
        userId = request_data.userId
        titleName = request_data.titleName
        writingRequirement = request_data.writingRequirement
        children = request_data.originalTemplate

        # 创建新模板
        new_template = WritingTemplate(
            user_id=userId,
            template_name=titleName,
            template_type='S',
            template_desc=writingRequirement,
            status_cd='Y',
            create_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        # 添加到会话并提交
        db.add(new_template)
        await db.commit()
        template_id = new_template.template_id
        await save_children(db, template_id, 0, children)
        return return_json(True,"模板数据保存成功。")
    except Exception as e:
        error_msg = f"模板保存接口发生异常: {str(e)}"
        mylog.error(error_msg)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"模板保存失败，请重试或联系系统管理员", "type": "failed"})
        )
    finally:
        session.close()  # 确保会话被关闭

show_order = 0
async def save_children(db :AsyncSession,template_id: int, parent_id: int, children: list):
    """
    递归保存children字段的数据到数据库中。
    """
    global show_order
    for child in children:
        # 创建AiTemplateTitle实例
        show_order += 1
        node = AiTemplateTitle(
            template_id=template_id,  # 假设template_id为1，根据实际情况调整
            parent_id=parent_id,
            title_name=child['titleName'],
            show_order=show_order,
            writing_requirement=child['writingRequirement'],
            status_cd='Y'
        )
        db.add(node)  # 添加到会话中
        await db.commit()
        title_id = node.title_id
        # 如果子节点有children，递归调用save_children
        if 'children' in child and child['children']:
            await save_children(db, template_id, title_id, child['children'])

@router.post("/templateUpdate")
async def template_update(request_data: TemplateUpdateRequest,db: AsyncSession = Depends(get_async_db)):
    try:
        userId = request_data.userId
        templateId = request_data.templateId
        titleName = request_data.titleName
        writingRequirement = request_data.writingRequirement
        originalTemplate = request_data.originalTemplate
        kwargs = {
            'template_name': titleName,
            'template_desc': writingRequirement
        }
        # 构建更新语句
        stmt = update(WritingTemplate).where(
            (WritingTemplate.user_id == userId) &
            (WritingTemplate.template_id == templateId)
        ).values(**kwargs)
        # 执行更新操作
        await db.execute(stmt)
        # 提交事务
        await db.commit()
        # 更新ai_template_title表数据,先删除，再添加
        if await delete_template_title(db, templateId):
            await save_children(db, templateId, 0, originalTemplate)
            return return_json(True, "模板数据更新成功。")
    except Exception as e:
        error_msg = f"模板更新接口发生异常: {str(e)}"
        mylog.error(error_msg)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"模板数据更新失败，请重试或联系系统管理员", "type": "failed"})
        )

async def delete_template(db: AsyncSession, user_id, template_id):
    try:
        # 删除模板
        # 构建查询，匹配userId和templateId
        stmt = select(WritingTemplate).filter(
            WritingTemplate.user_id == user_id,
            WritingTemplate.template_id == template_id
        )
        result = await db.execute(stmt)
        templateIfo = result.scalar_one_or_none()
        if templateIfo:
            await db.delete(templateIfo)
            await db.commit()
            return True  # 删除成功
        else:
            return False  # 没有找到匹配的模板，删除失败
    except Exception as e:
        error_msg = f"模板删除发生异常: {str(e)}"
        mylog.error(error_msg)

async def delete_template_title(db: AsyncSession,template_id):
    try:
        # 删除模板,构建查询，匹配templateId
        stmt = select(AiTemplateTitle).filter(
            AiTemplateTitle.template_id == template_id
        )
        query = await db.execute(stmt)
        templateInfo = query.scalars().all()
        if templateInfo:
            # 构建删除语句
            delete_stmt = delete(AiTemplateTitle).where(AiTemplateTitle.template_id == template_id)
            await db.execute(delete_stmt)
            await db.commit()
            return True  # 删除成功
        else:
            return False  # 没有找到匹配的模板，删除失败
    except Exception as e:
        error_msg = f"标题数据删除发生异常: {str(e)}"
        mylog.error(error_msg)

def return_json(isSuccess: bool, data: str):
    if isSuccess:
        return {"code": 200, "type": "success", "message": data}
    else:
        return {"code": 500, "type": "failed", "message": f"{data},请重试或联系系统管理员！"}

@router.post("/templateDelete")
async def template_delete(request_data: TemplateUpdateRequest,db: AsyncSession = Depends(get_async_db)):
    try:
        user_id = request_data.userId
        template_id = request_data.templateId
        if user_id == '0':
            return return_json(False, "不能删除公共模板")
        # 检查userId和templateId是否有效
        if not user_id or not template_id:
            return return_json(False, "userId和templateId不能为空")
        kwargs = {
            'status_cd': 'N',
        }
        # 删除文件信息
        stmt = update(WritingTemplate).where(
            (WritingTemplate.template_id == template_id) & (WritingTemplate.user_id == user_id)
        ).values(**kwargs)
        await db.execute(stmt)
        # 提交事务
        await db.commit()
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": f"模板删除成功", "type": "success"})
        )
        # if await delete_template_title(db, template_id) and await delete_template(db, user_id, template_id):
        #     return return_json(True, "模板删除成功")
        # else:
        #     return return_json(False, "模板删除失败")

    except Exception as e:
        error_msg = f"模板删除接口发生异常: {str(e)}"
        mylog.error(error_msg)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"模板删除失败，请重试或联系系统管理员", "type": "failed"})
        )




@router.post("/titleDataQuery")
async def title_data_query(request_data: TemplateQueryRequest,db: AsyncSession = Depends(get_async_db)):
    try:
        stmt = select(AiTemplateTitle).filter(
            or_(AiTemplateTitle.template_id == request_data.templateId)
        )
        result = await db.execute(stmt)
        results = result.scalars().all()
        returnData = {
            "code": 200,
            "message": "标题数据查询成功",
            "type": "success",
            "data": build_tree(results)
        }
        # 执行查询并返回结果
        return returnData
    except Exception as e:
        error_msg = f"标题数据查询接口发生异常: {str(e)}"
        mylog.error(error_msg)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"标题数据查询失败，请重试或联系系统管理员", "type": "failed"})
        )
    finally:
        session.close()

def build_tree(data):
    def build_children(parent_id, data):
        return [item for item in data if item.parent_id == parent_id]

    def build_node(item):
        children = build_children(item.title_id, data)
        item.children = [build_node(child) for child in children]
        return {
            "titleId": item.title_id,
            "templateId": item.template_id,
            "parentId": item.parent_id,
            "titleName": item.title_name,
            "showOrder": item.show_order,
            "writingRequirement": item.writing_requirement,
            "statusCd": item.status_cd,
            "children": item.children
        }

    # 找到所有根节点（parent_id为0）
    root_nodes = [item for item in data if item.parent_id == 0]
    # 构建树状结构
    tree = [build_node(root) for root in root_nodes]
    return tree



async def title_query_by_templateName(db: AsyncSession, template_name, user_id):
    try:
        if template_name:
            stmt = select(WritingTemplate).filter((WritingTemplate.user_id == user_id) & (WritingTemplate.template_name.like(f'%{template_name}%'))).all()
        else:
            stmt = select(WritingTemplate).filter((WritingTemplate.user_id == user_id)).all()
        result = await db.execute(stmt)
        results = result.scalars().all()
        return results
    except Exception as e:
        error_msg = f"标题数据查询接口发生异常: {str(e)}"
        mylog.error(error_msg)
    finally:
        session.close()




class AICreateTemplate(Base):
    __tablename__ = 'ai_create_template'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    user_id = Column(String(255), nullable=False, comment='用户id')
    template_name = Column(String(255), comment='模板名称')
    create_template = Column(String, comment='所生成模板')
    create_time = Column(Date, nullable=False, comment='生成时间')
    update_time = Column(Date, comment='更新时间')
    update_id = Column(String(255), comment='更新人')
    show_cd = Column(String(255), nullable=False,comment='模板是否有效（Y-有效，N-无效）')

class TemplateCreate(BaseModel):
    titleName: str
    writingRequirement: str
    userId: str
    templateName: str

@router.post("/createTemplateEntryTable", response_model=TemplateContentResponse)
async def create_template(request_data: TemplateCreate,db: AsyncSession = Depends(get_async_db)):
    mylog.info("*"*100)    
    try:
        # 调用模板服务的create_template方法，并获取返回的数据
        data = await template_service.create_template_entryTable(request_data)
        response = TemplateContentResponse(code=200, message="模板创建成功", type="success", data=data)
        create_template_json = json.dumps(data, ensure_ascii=False)
        new_template_data = {
            'user_id': request_data.userId,
            'template_name': request_data.templateName,
            'create_template': create_template_json,
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'show_cd': 'Y'
        }
        new_template = AICreateTemplate(**new_template_data)

        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        mylog.info(f"模板创建成功: {response}")
        return response
    except ValidationError as e:
        mylog.error(f"数据验证错误: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        mylog.error(f"处理请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


class reTemplatename(BaseModel):
    id: int
    template_name: str = None

@router.post("/reCreateTemplateName")
async def re_filename(re_TemplateName: reTemplatename, db: AsyncSession = Depends(get_async_db)):
    stmt = update(AICreateTemplate).where(
        AICreateTemplate.id == re_TemplateName.id
    ).values(
        template_name=re_TemplateName.template_name,
        update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
    await db.execute(stmt)
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": "模板重命名成功", "type": "success"})
    )

@router.post("/reTemplateName")
async def re_filename(re_TemplateName: reTemplatename, db: AsyncSession = Depends(get_async_db)):
    stmt = update(WritingTemplate).where(
        WritingTemplate.template_id == re_TemplateName.id
    ).values(
        template_name=re_TemplateName.template_name,
    )
    await db.execute(stmt)
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": "模板重命名成功", "type": "success"})
    )


class deleteTemplate(BaseModel):
    id: int

@router.post("/deleteCreateTemplate")
async def file_delete(delete_template: deleteTemplate, db: AsyncSession = Depends(get_async_db)):
    kwargs = {
        'show_cd': 'N',
    }
    stmt = update(AICreateTemplate).where(
        (AICreateTemplate.id == delete_template.id)
    ).values(**kwargs)
    await db.execute(stmt)
    # 提交事务
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": f"删除生成模板成功", "type": "success"})
    )

class queryCreateTemplate(BaseModel):
    userId: str
    pageNum: int = None
    pageSize: int = None

@router.post("/queryCreateTemplateList")
async def query_file_list(query_template: queryCreateTemplate, db: AsyncSession = Depends(get_async_db)):
    try:
        stmt = select(AICreateTemplate).filter(
            (AICreateTemplate.user_id == query_template.userId)
            & (AICreateTemplate.show_cd == "Y")
        ).order_by(AICreateTemplate.create_time.desc())
        
        result = await db.execute(stmt)
        total_count = len(result.scalars().all())
        
        # 分页
        stmt = stmt.offset((query_template.pageNum - 1) * query_template.pageSize).limit(query_template.pageSize)
        result = await db.execute(stmt)
        results = result.scalars().all()
        
        # 格式化日期
        for result in results:
            if isinstance(result.create_time, str):
                result.create_time = datetime.fromisoformat(result.create_time.replace('Z', '+00:00'))
            result.create_time = result.create_time.strftime("%Y-%m-%d %H:%M:%S")
            
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": "生成模板列表查询成功", "type": "success", 
                 "data": {"templateCount": total_count, "templateList": results}})
        )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return JSONResponse(
            status_code=500, 
            content=jsonable_encoder({"code": 500, "message": str(e), "type": "error"})
        )



from sqlalchemy.orm import aliased
class AIUsuallyTemplate(Base):
    __tablename__ = 'ai_usually_template'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    user_id = Column(String(255), nullable=False, comment='用户id')
    template_id = Column(String(255), comment='模板id')
    use_template = Column(String, comment='使用的模板')
    use_count = Column(String(255), comment='使用次数')
    use_time = Column(Date, comment='最近使用时间')

async def query_usually_template_list(user_id, db: AsyncSession):

    # Aliases for the tables
    ai_writing_template = aliased(WritingTemplate)
    ai_usually_template = aliased(AIUsuallyTemplate)

    # Subquery for RankedTemplates
    ranked_templates_subquery = (
        select(
            ai_writing_template.user_id,
            ai_writing_template.template_id,
            ai_writing_template.template_name,
            cast(ai_usually_template.use_count, types.Integer).label('use_count'),
            ai_writing_template.show_order,
            ai_usually_template.use_time.label('use_time')
        )
        .join(ai_usually_template, ai_writing_template.template_id == ai_usually_template.template_id)
        .where(
            and_(
                ai_usually_template.user_id == user_id,
                or_(
                    ai_writing_template.user_id == user_id,
                    ai_writing_template.user_id == '0'
                )
            )
        )
        .subquery()
    )

    # Subquery for UnrankdTemplates
    unranked_templates_subquery = (
        select(
            ai_writing_template.user_id,
            ai_writing_template.template_id,
            ai_writing_template.template_name,
            func.coalesce(cast(ai_usually_template.use_count, types.Integer), 0).label('use_count'),
            ai_writing_template.show_order,
            ai_writing_template.create_time.label('use_time'),
        )
        .outerjoin(ai_usually_template,
                   (ai_writing_template.template_id == ai_usually_template.template_id) & (
                               ai_usually_template.user_id == user_id))
        .where(
            (ai_writing_template.user_id == user_id) | (ai_writing_template.user_id == '0'),
            (ai_usually_template.user_id == None) | (ai_usually_template.template_id == None),
            ai_writing_template.status_cd == "Y"
        )
        .subquery()
    )

    # Main query combining both subqueries
    combined_query = (
        select(
            ranked_templates_subquery.c.user_id,
            ranked_templates_subquery.c.template_id,
            ranked_templates_subquery.c.template_name,
            ranked_templates_subquery.c.use_count,
            ranked_templates_subquery.c.show_order,
            ranked_templates_subquery.c.use_time.label('create_time')
        )
        .union_all(
            select(
                unranked_templates_subquery.c.user_id,
                unranked_templates_subquery.c.template_id,
                unranked_templates_subquery.c.template_name,
                unranked_templates_subquery.c.use_count,
                unranked_templates_subquery.c.show_order,
                unranked_templates_subquery.c.use_time.label('create_time')
            )
        )
        .order_by(
            case((ranked_templates_subquery.c.use_count == 0, 1), else_=0),
            ranked_templates_subquery.c.use_count.desc(),
            ranked_templates_subquery.c.show_order.asc()
        )
    )

    result = await db.execute(combined_query)
    templates = result.fetchall()

    # Convert the result to a list of dictionaries
    templates_list = [
        {
            "user_id": row.user_id,
            "template_id": row.template_id,
            "template_name": row.template_name,
            "use_count": row.use_count,
            "show_order": row.show_order,
            "create_time": row.create_time
        }
        for row in templates
    ]
    return templates_list

class queryUsuallyTemplate(BaseModel):
    userId: str

@router.post("/queryUsuallyTemplate")
async def query_file_list(query_usually_template: queryUsuallyTemplate, db: AsyncSession = Depends(get_async_db)):
    user_id = query_usually_template.userId
    templates_list = await query_usually_template_list(user_id, db)

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": "常用模板列表查询成功", "type": "success",
             "data": templates_list})
    )


def get_create_time(item):
    # 如果 item 是字典，直接使用方括号访问 'create_time'
    # 如果 item 是对象，使用点符号访问 create_time 属性
    if isinstance(item, dict):
        create_time = item.get('create_time')
    else:
        create_time = getattr(item, 'create_time', None)

    # 如果 create_time 是 None 或者不是 datetime 对象，则返回一个默认的 datetime 对象
    if create_time is None or not isinstance(create_time, datetime):
        # 可以选择一个默认的 datetime 对象，例如 datetime.min 或者当前时间
        return datetime.min
    return create_time

def format_create_time(create_time):
    if isinstance(create_time, str):
        try:
            # 将字符串转换为 datetime 对象
            create_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
        except ValueError:
            # 如果转换失败，打印错误信息或处理异常
            print(f"Error: Unable to parse create_time string '{create_time}'")
            return None
    # 如果 create_time 是 None 或不是 datetime 对象，则返回 None
    if create_time is None or not isinstance(create_time, datetime):
        return None
    # 格式化日期
    return create_time.strftime("%Y-%m-%d %H:%M:%S")
class queryTempalteList(BaseModel):
    userId: str
    templateTitle: Optional[str] = None
@router.post("/queryTemplateList")
async def ai_solution_query(query_template_list: queryTempalteList,db: AsyncSession = Depends(get_async_db)):
    try:
        #查询用户常用模板
        template_list = await query_usually_template_list(query_template_list.userId, db)
        pattern = re.compile(query_template_list.templateTitle, re.IGNORECASE)  # 编译正则表达式模式，不区分大小写
        # 创建一个空列表来存储匹配的结果
        matching_results = []
        for item in template_list:
            # 在 template_name 字段中搜索匹配的内容
            match = pattern.search(item['template_name'])
            if match:  # 如果找到匹配的内容
                item['type'] = 1
                matching_results.append(item)  # 将匹配的元素添加到结果列表中

        # 查询文件模板
        fileResults = await select_file_by_title(db, query_template_list.templateTitle, query_template_list.userId)

        #查询用户生成模板
        stmt1 = select(AICreateTemplate).filter(
            (AICreateTemplate.template_name.like(f'%{query_template_list.templateTitle}%'))
            & (AICreateTemplate.user_id == query_template_list.userId)
            & (AICreateTemplate.show_cd == "Y")
        ).order_by(AICreateTemplate.create_time.desc())

        result = await db.execute(stmt1)
        results1 = result.scalars().all()
        data = []
        data.extend(matching_results)
        # 给results1数据全部加上字段type=3
        for result1_item in results1:
            result1_item_dict = result1_item.__dict__.copy()
            result1_item_dict['type'] = 3  # 给results1数据加上字段type=3
            data.append(result1_item_dict)
        # 处理 fileResults，重命名字段
        for file_result in fileResults:
            # 创建一个新的字典，包含重命名后的字段
            new_file_result = {
                "template_name": file_result.file_name,
                "create_time": file_result.create_date,
                "type": 2  # 给fileResults数据加上字段type=2
            }
            # 将 fileResult 中的其他字段添加到新字典中
            for key, value in file_result.__dict__.items():
                if key not in ["file_name", "create_date"]:
                    new_file_result[key] = value
            # 将新字典添加到 data 列表中
            data.append(new_file_result)
        total_count = len(data)
        for item in data:
            # 检查 item 是否为字典，并且包含 'create_time' 键
            if isinstance(item, dict) and 'create_time' in item:
                if isinstance(item['create_time'], str):
                    # 将字符串格式的 create_time 转换为 datetime 对象
                    item['create_time'] = datetime.strptime(item['create_time'], '%Y-%m-%d %H:%M:%S')
        # 使用 sorted 函数
        sorted_data = sorted(data, key=get_create_time, reverse=True)
        for result in sorted_data:
            if isinstance(result, dict):
                # 如果 result 是字典，使用方括号访问 'create_time'
                result['create_time'] = format_create_time(result['create_time'])
            elif hasattr(result, 'create_time'):
                # 如果 result 是对象，使用点符号访问 create_time 属性
                result.create_time = format_create_time(getattr(result, 'create_time'))
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": f"查询成功", "type": "success", "total_count": total_count, "data": sorted_data})
        )
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"查询失败，请重试或联系系统管理员", "type": "failed"})
        )