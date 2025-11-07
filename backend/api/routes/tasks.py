"""
任务管理 API
"""
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import AiTask
from models.solution import ArticleGenerationRequest
from models.templates import TemplateData
from config import AsyncSessionLocal
from tasks.celery_app import celery_app
from tasks.article_tasks import generate_article_task
from tasks.redis_stream import redis_stream_manager
from utils.logger import mylog


router = APIRouter()


async def get_async_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@router.post("/generate-article")
async def submit_generate_article_task(
    request: ArticleGenerationRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    提交文章生成任务
    """
    try:
        task_id = str(uuid.uuid4())
        
        outline_dict = request.outline.dict() if hasattr(request.outline, 'dict') else request.outline
        
        task_record = AiTask(
            task_id=task_id,
            task_type="generate_article",
            user_id=request.userId,
            status="pending",
            progress=0,
            input_params=json.dumps(outline_dict, ensure_ascii=False),
            created_at=datetime.now()
        )
        
        db.add(task_record)
        await db.commit()
        
        redis_stream_manager.update_task_meta(task_id, "pending", 0)
        
        generate_article_task.delay(task_id, outline_dict, request.userId)
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "任务已提交",
                "type": "success",
                "data": {"task_id": task_id}
            })
        )
    except Exception as e:
        mylog.error(f"提交任务失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"提交任务失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )


def format_sse(data: str, is_end: bool = False) -> str:
    """格式化 SSE 响应"""
    response = {
        "code": 200,
        "message": "内容生成成功" if is_end else None,
        "type": "success",
        "data": data,
        "is_end": is_end
    }
    return f"data: {json.dumps(response, ensure_ascii=False)}\n\n"


@router.get("/{task_id}/stream")
async def stream_task_result(task_id: str, req: Request):
    """
    SSE 流式输出任务结果（支持断线重连）
    """
    async def generate():
        try:
            last_id = "0"
            sent_count = 0
            
            all_messages = redis_stream_manager.read_all_content(task_id)
            
            if all_messages:
                for msg in all_messages:
                    content = msg.get("content", "")
                    if content:
                        yield format_sse(content, False)
                        sent_count += 1
                        last_id = msg.get("id", "0")
            
            meta = redis_stream_manager.get_task_meta(task_id)
            if meta and meta.get("status") in ["completed", "failed"]:
                yield format_sse("", True)
                return
            
            while True:
                new_messages = redis_stream_manager.read_new_content(task_id, last_id)
                
                if new_messages:
                    for msg in new_messages:
                        content = msg.get("content", "")
                        if content:
                            yield format_sse(content, False)
                            sent_count += 1
                            last_id = msg.get("id", "0")
                
                meta = redis_stream_manager.get_task_meta(task_id)
                if meta:
                    status = meta.get("status")
                    if status == "completed":
                        yield format_sse("", True)
                        break
                    elif status == "failed":
                        error_msg = meta.get("error_message", "任务执行失败")
                        yield format_sse(f"\n\n错误: {error_msg}", True)
                        break
                
                await asyncio.sleep(0.5)
                
        except Exception as e:
            mylog.error(f"流式输出错误: {str(e)}")
            yield format_sse(f"\n\n错误: {str(e)}", True)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream; charset=utf-8"
    )


@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    查询任务状态
    """
    try:
        task_record = await db.get(AiTask, task_id)
        
        if not task_record:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({
                    "code": 404,
                    "message": "任务不存在",
                    "type": "error",
                    "data": None
                })
            )
        
        meta = redis_stream_manager.get_task_meta(task_id)
        
        data = {
            "task_id": task_record.task_id,
            "task_type": task_record.task_type,
            "user_id": task_record.user_id,
            "status": task_record.status,
            "progress": task_record.progress,
            "error_message": task_record.error_message,
            "created_at": task_record.created_at.isoformat() if task_record.created_at else None,
            "updated_at": task_record.updated_at.isoformat() if task_record.updated_at else None,
            "completed_at": task_record.completed_at.isoformat() if task_record.completed_at else None
        }
        
        if meta:
            data["status"] = meta.get("status", task_record.status)
            data["progress"] = meta.get("progress", task_record.progress)
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "查询成功",
                "type": "success",
                "data": data
            })
        )
    except Exception as e:
        mylog.error(f"查询任务状态失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"查询失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )


@router.get("/user/{user_id}")
async def get_user_tasks(
    user_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    查询用户任务列表
    """
    try:
        stmt = select(AiTask).filter(
            AiTask.user_id == user_id
        ).order_by(AiTask.created_at.desc()).limit(50)
        
        result = await db.execute(stmt)
        tasks = result.scalars().all()
        
        task_list = []
        for task in tasks:
            task_list.append({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "查询成功",
                "type": "success",
                "data": {"tasks": task_list, "count": len(task_list)}
            })
        )
    except Exception as e:
        mylog.error(f"查询用户任务列表失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"查询失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    取消任务
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        
        task_record = await db.get(AiTask, task_id)
        if task_record:
            task_record.status = "cancelled"
            task_record.updated_at = datetime.now()
            await db.commit()
        
        redis_stream_manager.update_task_meta(task_id, "cancelled", 0)
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "任务已取消",
                "type": "success",
                "data": None
            })
        )
    except Exception as e:
        mylog.error(f"取消任务失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"取消任务失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )

