import asyncio
import json
import threading
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from models.solution import (ChapterGenerationRequest, ArticleGenerationRequest, 
                            GenerationResponse, StreamGenerationResponse, AiSolutionSave)
from models.templates import TemplateContentResponse
from services.solution import generate_chapter, ChapterGenerationState, generate_article, optimize_content
from ai.llm.llm_factory import LLMFactory
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from datetime import datetime, timedelta
from utils.logger import mylog
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Text, Date, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_async_db
from api.routes.file import select_file_by_title
# 注：此前从 templates 路由导入的函数 `title_query_by_templateName` 并不存在且未使用，
# 会导致应用在启动阶段 ImportError，从而阻断所有接口，包括生成报告接口。
# 因此移除该无效导入以恢复服务启动。
router = APIRouter()
Base = declarative_base()
# 用于存储序列号的字典，键为日期，值为序列号
sequence_numbers = {}
# 锁，用于在多线程环境中安全地更新序列号
sequence_lock = threading.Lock()

# 存储每个IP的请求状态
request_in_progress = {}


def format_sse(data: str, is_end: bool = False) -> str:
    """SSE 格式包装，兼容前端解析结构"""
    response = StreamGenerationResponse(
        code=200,
        message="内容生成成功" if is_end else None,
        type="success",
        data=data,
        is_end=is_end,
    )
    return f"data: {json.dumps(response.dict(), ensure_ascii=False)}\n\n"


@router.post("/generate-chapter")
async def generate_chapter_api(request: ChapterGenerationRequest, req: Request, db: AsyncSession = Depends(get_async_db)):
    # client_ip = req.client.host
    # if request_in_progress.get(client_ip, False):
    #     mylog.warning(f"请求过于频繁: {client_ip} 上一个请求仍在进行中。")
    #     raise HTTPException(status_code=429, detail="请求过于频繁: 上一个请求仍在进行中。")
    
    # request_in_progress[client_ip] = True
    
    # 强制要求 modelId
    if not request.modelId:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 400, "type": "error", "message": "缺少 modelId 参数", "data": None
        }))

    llm = await LLMFactory.get_llm_by_id(db, request.modelId)
    if not llm:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到可用模型，请先配置", "data": None
        }))

    async def generate():
        # try:
            async for content in generate_chapter(request.chapter, request.last_para_content, highest_level_title="", llm=llm, db=db):
                yield format_sse(content)
                await asyncio.sleep(0)  # 给予事件循环处理其他任务的机会
            yield format_sse("", is_end=True)
        # finally:
        #     request_in_progress[client_ip] = False
        #     mylog.info(f"请求完成: {client_ip}")
    mylog.info("*"*100)
    # mylog.info(f"开始生成章节: {client_ip}")
    mylog.info(f"请求数据: {json.dumps(request.dict(), ensure_ascii=False, indent=2)}")
    mylog.info("--------------------------------------------------")
    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8",
        background=BackgroundTask(lambda: None)
    )

from sqlalchemy import DateTime
class Template(Base):
    __tablename__ = 'ai_usually_template'  # 表名

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String(255), nullable=False)
    template_id = Column(String(255), nullable=False)
    use_template = Column(Text, nullable=True)
    use_count = Column(String(255), nullable=True)
    use_time = Column(DateTime, nullable=True)


async def get_template_record(db, user_id, template_id):
    stmt = select(Template).filter(
        Template.user_id == user_id,
        Template.template_id == template_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
    
@router.post("/generate-article")
async def generate_article_api(request: ArticleGenerationRequest,db: AsyncSession = Depends(get_async_db)):
    # client_ip = req.client.host
    # if request_in_progress.get(client_ip, False):
    #     mylog.warning(f"请求过于频繁: {client_ip} 上一个请求仍在进行中。")
    #     raise HTTPException(status_code=429, detail="请求过于频繁: 上一个请求仍在进行中。")
    
    # request_in_progress[client_ip] = True
    mylog.info("*"*100)
    # 打印出入参的整体大纲
    mylog.info(f"收到的大纲: {json.dumps(request.outline.dict(), ensure_ascii=False, indent=2)}")
    mylog.info("--------------------------------------------------")
    if request.userId:               
        # 如果 request.outline 是 Pydantic 模型
        if hasattr(request.outline, 'dict'):
            outline_dict = request.outline.dict()
        # 如果 request.outline 是普通对象或元组
        else:
            outline_dict = request.outline
        # 获取现有记录
        existing_template = await get_template_record(db, request.userId, request.templateId)
        if existing_template:
            # 更新现有记录
            existing_template.use_count = str(int(existing_template.use_count) + 1)
            existing_template.use_template = json.dumps(outline_dict, ensure_ascii=False)
            existing_template.use_time = datetime.now()
        else:
            # 创建新记录
            new_template = Template(
                user_id=request.userId,
                template_id=request.templateId,
                use_template=json.dumps(outline_dict, ensure_ascii=False),
                use_count="1",
                use_time=datetime.now()
            )
            db.add(new_template)
        await db.commit()


    # 强制要求 modelId
    if not request.modelId:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 400, "type": "error", "message": "缺少 modelId 参数", "data": None
        }))

    llm = await LLMFactory.get_llm_by_id(db, request.modelId)
    if not llm:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到可用模型，请先配置", "data": None
        }))

    async def generate():
        # try:
            state = ChapterGenerationState(request.outline)
            async for content in generate_article(state, llm, db=db):
                yield format_sse(content)
                await asyncio.sleep(0)  # 给予事件循环处理其他任务的机会
            yield format_sse("", is_end=True)
    #     finally:
    #         request_in_progress[client_ip] = False
    #         mylog.info(f"请求完成: {client_ip}")
    # mylog.info(f"开始生成文章: {client_ip}")
    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8",
        background=BackgroundTask(lambda: None)
    )

@router.post("/optimize-content")
async def optimize_content_api(request: dict, req: Request, db: AsyncSession = Depends(get_async_db)):
    """
    流式优化内容的API接口，根据原文、文章类型和用户要求进行内容优化，并流式返回结果。

    :param request: 包含 original_text, article_type 和 user_requirements 的字典
    :return: 优化后的内容流
    """
    async def generate():
        original_text = request.get("original_text", "")
        article_type = request.get("article_type", "")
        user_requirements = request.get("user_requirements", "")

        model_id = request.get("model_id")
        if not model_id:
            yield format_sse("", is_end=True)
            return
        llm = await LLMFactory.get_llm_by_id(db, int(model_id))
        if not llm:
            yield format_sse("", is_end=True)
            return
        async for content in optimize_content(original_text, article_type, user_requirements, llm):
            yield format_sse(content)
            await asyncio.sleep(0)  # 给予事件循环处理其他任务的机会
        yield format_sse("", is_end=True)
    mylog.info("*"*100)
    mylog.info(f"开始优化内容: {req.client.host}")
    mylog.info(f"请求数据: {json.dumps(request, ensure_ascii=False, indent=2)}")
    mylog.info("--------------------------------------------------")
    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8",
        background=BackgroundTask(lambda: None)
    )

# 统一使用 models.solution.AiSolutionSave，不在路由内重复定义




class saveSolution(BaseModel):
    solution_title: str
    solution_content: str
    create_phone: str
    create_name: str


class querySolution(BaseModel):
    create_phone: str
    solution_title: Optional[str] = None

class deleteSolution(BaseModel):
    solution_id: str

class updateSolution(BaseModel):
    solution_id: str
    solution_title: str
    solution_content: Optional[str] = None
    update_phone: str
    update_name: str




async def get_next_sequence_number(db):
    """
    获取下一个序列号。
    如果当天的序列号已经存在，则递增；否则，从0001开始。
    """
    with sequence_lock:
        today = datetime.now().strftime('%Y-%m-%d')
        # 直接按 solution_id 前缀过滤；create_date 已为 DATETIME，但为避免字符串 vs 时间比较问题，这里用主键前缀更稳妥
        prefix = datetime.now().strftime('%Y%m%d')
        stmt = select(AiSolutionSave.solution_id).filter(AiSolutionSave.solution_id.like(f"{prefix}%")).order_by(AiSolutionSave.solution_id.desc())
        result = await db.execute(stmt)
        max_sequence_query = result.scalars().all()
        if max_sequence_query:
            # 从solution_id中提取序列号部分并加1
            max_sequence = int(str(max_sequence_query[0])[-4:]) + 1
        else:
            # 如果没有记录，序列号从1开始
            max_sequence = 1
        # 格式化序列号为四位字符串，不足四位前面补零
        return f"{max_sequence:04d}"

@router.post("/solutionSave")
async def ai_solution_save(save_solution: saveSolution,db: AsyncSession = Depends(get_async_db)):
    try:
        # 获取当前日期和时间
        current_datetime = datetime.now()
        current_date = current_datetime.strftime('%Y%m%d')
        
        # 获取下一个序列号
        sequence_number = await get_next_sequence_number(db)
        solution_id = current_date + sequence_number
        solution_data = {
            'solution_id': solution_id,
            'solution_title': save_solution.solution_title,
            'solution_content': save_solution.solution_content,
            'create_phone': save_solution.create_phone,
            'create_name': save_solution.create_name,
            'create_date': datetime.now(),
            'status_cd': 'Y'
        }
        mylog.info(f"[solutionSave] solution_id={solution_id}, seq={sequence_number}, title={save_solution.solution_title!r}")
        # 创建一个新的AiSolutionSave实例
        new_solution = AiSolutionSave(**solution_data)

        db.add(new_solution)
        await db.commit()
        await db.refresh(new_solution)

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": f"解决方案信息保存成功", "type": "success"})
        )
    except SQLAlchemyError as e:
        mylog.exception(f"[solutionSave] DB error: {e}")
        try:
            mylog.error(f"[solutionSave] payload={json.dumps(solution_data, ensure_ascii=False)}")
        except Exception:
            pass
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"解决方案信息保存失败，请重新保存或联系系统管理员", "type": "failed"})
        )
    

@router.post("/querySolution")
async def ai_solution_query(query_solution: querySolution,db: AsyncSession = Depends(get_async_db)):
    try:

        if query_solution.solution_title:
            # 执行查询并获取结果
            stmt = select(AiSolutionSave).filter((AiSolutionSave.solution_title.like(f'%{query_solution.solution_title}%'))
                                                     & (AiSolutionSave.create_phone==query_solution.create_phone)
                                                      & (AiSolutionSave.status_cd=="Y")).order_by(AiSolutionSave.create_date.desc())
            # 模糊查询文章标题
            query = await db.execute(stmt)
        else:
            # 默认全查
            stmt = select(AiSolutionSave).filter((AiSolutionSave.create_phone==query_solution.create_phone) & (AiSolutionSave.status_cd=="Y")).order_by(AiSolutionSave.create_date.desc())
            query = await db.execute(stmt)
        results = query.scalars().all()
        solution_count = len(results)
        for result in results:
            if isinstance(result.create_date, str):
                # 将字符串转换为 datetime 对象
                result.create_date = datetime.fromisoformat(result.create_date.replace('Z', '+00:00'))
            # 格式化日期
            result.create_date = result.create_date.strftime("%Y-%m-%d %H:%M:%S")
        fileResults = await select_file_by_title(db, query_solution.solution_title, query_solution.create_phone)
        file_count = len(fileResults)
        for result in fileResults:
            if isinstance(result.create_date, str):
                # 将字符串转换为 datetime 对象
                result.create_date = datetime.fromisoformat(result.create_date.replace('Z', '+00:00'))
            # 格式化日期
            result.create_date = result.create_date.strftime("%Y-%m-%d %H:%M:%S")    
        # templateResults = await title_query_by_templateName(query_solution.solution_title, query_solution.create_phone)
        data = {
            "fileCont": file_count,
            "fileDatas": fileResults,
            "solutionCount": solution_count,
            "solutionDatas": results
        }
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": f"查询成功", "type": "success", "data": data})
        )
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"查询失败，请重试或联系系统管理员", "type": "failed"})
        )

class querySolutionList(BaseModel):
    create_phone: str
    pageNum: int = None
    pageSize: int = None

@router.post("/querySolutionList")
async def ai_solution_query(query_solution_list: querySolutionList,db: AsyncSession = Depends(get_async_db)):
    try:
        # 默认全查
        stmt = select(AiSolutionSave).filter((AiSolutionSave.create_phone==query_solution_list.create_phone) & (AiSolutionSave.status_cd=="Y")).order_by(AiSolutionSave.create_date.desc())
        # 获取总条数
        result = await db.execute(stmt)
        total_count = len(result.scalars().all())
        # 分页查询
        page_size = query_solution_list.pageSize
        page_number = query_solution_list.pageNum
        offset = (page_number - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        result = await db.execute(stmt)
        results = result.scalars().all()
        for result in results:
            if isinstance(result.create_date, str):
                # 将字符串转换为 datetime 对象
                result.create_date = datetime.fromisoformat(result.create_date.replace('Z', '+00:00'))
            # 格式化日期
            result.create_date = result.create_date.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "solutionCount": total_count,
            "solutionList": results
        }
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {"code": 200, "message": f"查询成功", "type": "success", "data": data})
        )
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                {"code": 500, "message": f"查询失败，请重试或联系系统管理员", "type": "failed"})
        )
    

@router.post("/deleteSolution")
async def solution_delete(delete_solution: deleteSolution,db: AsyncSession = Depends(get_async_db)):
    kwargs = {
        'status_cd': 'N',
    }
    # 删除方案信息
    stmt = update(AiSolutionSave).where(
        (AiSolutionSave.solution_id == delete_solution.solution_id)
    ).values(**kwargs)
    await db.execute(stmt)
    # 提交事务
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": f"方案信息删除成功", "type": "success"})
    )


@router.post("/updateSolution")
async def update_solution(update_solution: updateSolution,db: AsyncSession = Depends(get_async_db)):
    kwargs = {
        'solution_title': update_solution.solution_title,
        'solution_content': update_solution.solution_content,
        'update_phone': update_solution.update_phone,
        'update_name': update_solution.update_name,
        'update_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    # 过滤掉 None 值
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    # 构建更新语句
    stmt = update(AiSolutionSave).where(
        (AiSolutionSave.solution_id == update_solution.solution_id)
    ).values(**kwargs)
    # 执行更新操作
    await db.execute(stmt)
    # 提交事务
    await db.commit()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {"code": 200, "message": f"方案信息更新成功", "type": "success"})
    )


class GetSolutionRequest(BaseModel):
    solution_id: str


@router.post("/getSolution")
async def get_solution(req: GetSolutionRequest, db: AsyncSession = Depends(get_async_db)):
    try:
        stmt = select(AiSolutionSave).where(AiSolutionSave.solution_id == req.solution_id)
        result = await db.execute(stmt)
        sol = result.scalar_one_or_none()
        if not sol:
            return JSONResponse(status_code=200, content=jsonable_encoder({
                "code": 404, "message": "未找到记录", "type": "error", "data": None
            }))
        data = {
            "solution_id": sol.solution_id,
            "solution_title": sol.solution_title,
            "solution_content": sol.solution_content,
            "create_phone": sol.create_phone,
            "create_name": sol.create_name,
            "create_date": str(sol.create_date),
            "status_cd": sol.status_cd
        }
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 200, "message": "查询成功", "type": "success", "data": data
        }))
    except Exception as e:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 500, "message": f"查询失败: {str(e)}", "type": "error", "data": None
        }))
