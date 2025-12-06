import re
from datetime import datetime
import json
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_fixed
from api.routes.file import select_file_by_title
from models.templates import (
    TemplateCreateNeed, TemplateContentResponse, TemplateRefreshNeed,
    WritingTemplate, AiTemplateTitle, AICreateTemplate, AIUsuallyTemplate,
    TemplateCreate, TemplateQueryRequest, TemplateSaveRequest, TemplateUpdateRequest,
    reTemplatename, deleteTemplate, queryCreateTemplate, queryUsuallyTemplate, queryTempalteList
)
from services.templates import TemplateService
from ai.llm.llm_factory import LLMFactory
from utils.logger import mylog
from pydantic import ValidationError
from config import get_async_db
from sqlalchemy import Date, and_, case, cast, Column, Integer, String, delete, func, select, types
from sqlalchemy import or_, update, BigInteger
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased


# 创建一个FastAPI的APIRouter实例，用于定义模板相关的API路由
router = APIRouter()

# 创建一个模板服务实例，用于处理模板相关的业务逻辑
template_service = TemplateService()

@router.post("/create", response_model=TemplateContentResponse)
async def create_template(request_data: TemplateCreateNeed, request: Request):
    """
    创建模板（不保存到数据库）
    
    这个接口用于临时生成模板预览，不保存到数据库
    """
    mylog.info("=== 开始处理生成模板请求（不保存） ===")
    mylog.info(f"源IP: {request.client.host}, 请求数据: {request_data}")
    try:
        # === 调用模板服务生成模板 ===
        data = await template_service.create_template(request_data)
        response = TemplateContentResponse(code=200, message="模板创建成功", type="success", data=data)
        mylog.info("=== 模板创建成功 ===")
        return response
    except ValidationError as e:
        mylog.error(f"数据验证错误: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        error_msg = f"创建模板时发生错误: {str(e)}"
        mylog.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/refresh", response_model=TemplateContentResponse)
async def refresh_template(request: Request, refreshNeed: TemplateRefreshNeed):
    """
    刷新模板（不保存到数据库）
    
    这个接口用于刷新现有模板，不保存到数据库
    """
    mylog.info("=== 开始处理刷新模板请求 ===")
    mylog.info(f"源IP: {request.client.host}, 请求数据: {refreshNeed}")
    try:
        # === 调用模板服务刷新模板 ===
        data = await template_service.refresh_template(refreshNeed)
        response = TemplateContentResponse(code=200, message="模板刷新成功", type="success", data=data)
        mylog.info("=== 模板刷新成功 ===")
        return response
    except ValidationError as e:
        mylog.error(f"数据验证错误: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        error_msg = f"刷新模板时发生错误: {str(e)}"
        mylog.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)
    
# 统一使用全局配置的 get_async_db，避免环境不一致


# 去除同步 Session，会话统一走异步依赖注入

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
            create_time=datetime.now().date(),
        )
        # 添加到会话并提交
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        template_id = new_template.template_id
        global show_order
        show_order = 0
        await save_children(db, template_id, 0, children or [])
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
        pass

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
            writing_requirement=child.get('writingRequirement'),
            reference_output=child.get('referenceOutput'),
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
            global show_order
            show_order = 0
            await save_children(db, templateId, 0, originalTemplate or [])
            return return_json(True, "模板数据更新成功。")
    except Exception as e:
        error_msg = f"模板更新接口发生异常: {str(e)}"
        mylog.error(error_msg)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"模板数据更新失败，请重试或联系系统管理员", "type": "failed"})
        )

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
        pass

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
            "referenceOutput": item.reference_output,
            "statusCd": item.status_cd,
            "children": item.children
        }

    # 找到所有根节点（parent_id为0）
    root_nodes = [item for item in data if item.parent_id == 0]
    # 构建树状结构
    tree = [build_node(root) for root in root_nodes]
    return tree








@router.post("/createTemplateEntryTable", response_model=TemplateContentResponse)
async def create_template_entry_table(request_data: TemplateCreate, db: AsyncSession = Depends(get_async_db)):
    """
    创建模板并保存到数据库
    
    这个接口用于生成模板并保存到 ai_create_template 表
    """
    mylog.info("=== 开始处理创建模板并保存请求 ===")
    mylog.info(f"请求数据: {request_data}")
    try:
        # === 获取用户的模型配置 ===
        if request_data.modelId:
            llm = await LLMFactory.get_llm_by_id(db, request_data.modelId)
            if not llm:
                raise HTTPException(status_code=404, detail="未找到指定的模型配置")
        else:
            llm = await LLMFactory.get_default_llm(db, user_id=request_data.userId)
            if not llm:
                raise HTTPException(status_code=404, detail="未找到可用的模型配置，请先配置模型")
        
        # === 调用模板服务生成模板 ===
        data = await template_service.create_template_entryTable(request_data, llm, db=db)
        
        # === 保存模板到数据库 ===
        create_template_json = json.dumps(data, ensure_ascii=False)
        new_template_data = {
            'user_id': request_data.userId,
            'template_name': request_data.templateName,
            'create_template': create_template_json,
            'example_output': getattr(request_data, 'exampleOutput', None),
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'show_cd': 'Y'
        }
        new_template = AICreateTemplate(**new_template_data)
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        
        response = TemplateContentResponse(code=200, message="模板创建成功", type="success", data=data)
        mylog.info("=== 模板创建并保存成功 ===")
        return response
    except ValidationError as e:
        mylog.error(f"数据验证错误: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        error_msg = str(e)
        mylog.error(f"业务逻辑错误: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "AuthenticationError" in error_str or "令牌状态不可用" in error_str or "认证失败" in error_str:
            # 追加打印本次所用模型配置要点，便于排查
            try:
                cfg_id = getattr(llm, 'model_name', None)  # ChatOpenAI 不含 cfg，打印其关键字段
            except Exception:
                cfg_id = None
            mylog.error("AI模型认证错误: %s", error_str)
            mylog.error("本次请求模型信息: model=%s, base_url=%s", getattr(llm, 'model', None), getattr(llm, 'openai_api_base', None))
            error_msg = "AI模型API认证失败，请检查API密钥配置或网关可用性"
            raise HTTPException(status_code=401, detail=error_msg)
        error_msg = f"创建模板时发生错误: {error_str}"
        mylog.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)



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
    union_query = (
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
    ).subquery()

    # 对 union 结果进行排序（必须对外层列排序，不能引用子查询别名）
    ordered_query = select(
        union_query.c.user_id,
        union_query.c.template_id,
        union_query.c.template_name,
        union_query.c.use_count,
        union_query.c.show_order,
        union_query.c.create_time
    ).order_by(
        case((union_query.c.use_count == 0, 1), else_=0),
        union_query.c.use_count.desc(),
        union_query.c.show_order.asc()
    )

    result = await db.execute(ordered_query)
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

@router.post("/queryUsuallyTemplate")
async def query_file_list(query_usually_template: queryUsuallyTemplate, db: AsyncSession = Depends(get_async_db)):
    try:
        user_id = query_usually_template.userId
        templates_list = await query_usually_template_list(user_id, db)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": "常用模板列表查询成功", "type": "success",
                 "data": templates_list})
        )
    except SQLAlchemyError as e:
        error_msg = f"常用模板查询接口发生数据库异常: {str(e)}"
        mylog.error(error_msg, exc_info=True)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": "常用模板查询失败，请重试或联系系统管理员", "type": "failed"})
        )
    except Exception as e:
        error_msg = f"常用模板查询接口发生异常: {str(e)}"
        mylog.error(error_msg, exc_info=True)
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": "常用模板查询失败，请重试或联系系统管理员", "type": "failed"})
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
