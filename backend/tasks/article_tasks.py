"""
文章生成异步任务
"""
import asyncio
import sys
from datetime import datetime
from tasks.celery_app import celery_app
from tasks.redis_stream import redis_stream_manager
from services.solution import generate_article, ChapterGenerationState
from models.templates import TemplateChild as OutlineItem
from models.task import AiTask
from config import AsyncSessionLocal
from utils.logger import mylog


@celery_app.task(bind=True)
def generate_article_task(self, task_id: str, outline_dict: dict, user_id: str = None):
    """
    文章生成异步任务
    """
    async def _run():
        try:
            redis_stream_manager.update_task_meta(task_id, "processing", 0)
            
            outline = OutlineItem(**outline_dict)
            state = ChapterGenerationState(outline)
            
            total_chunks = 0
            complete_content = ""
            
            async for content_chunk in generate_article(state):
                complete_content += content_chunk
                total_chunks += 1
                
                redis_stream_manager.write_content(task_id, content_chunk)
                
                if total_chunks % 10 == 0:
                    progress = min(90, int(total_chunks / 100))
                    redis_stream_manager.update_task_meta(task_id, "processing", progress)
            
            redis_stream_manager.set_task_result(task_id, complete_content)
            redis_stream_manager.update_task_meta(task_id, "completed", 100)
            
            async with AsyncSessionLocal() as session:
                task_record = await session.get(AiTask, task_id)
                if task_record:
                    task_record.status = "completed"
                    task_record.progress = 100
                    task_record.result = complete_content
                    task_record.completed_at = datetime.now()
                    await session.commit()
            
            return {"status": "completed", "result": complete_content}
            
        except Exception as e:
            error_msg = str(e)
            mylog.error(f"任务执行失败: {error_msg}")
            import traceback
            mylog.error(traceback.format_exc())
            
            redis_stream_manager.update_task_meta(task_id, "failed", 0, error_msg)
            
            async with AsyncSessionLocal() as session:
                task_record = await session.get(AiTask, task_id)
                if task_record:
                    task_record.status = "failed"
                    task_record.error_message = error_msg
                    await session.commit()
            
            raise
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        existing_loop = asyncio.get_event_loop()
        if existing_loop.is_running():
            existing_loop.close()
    except RuntimeError:
        pass
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(_run())
    finally:
        try:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception as e:
            mylog.error(f"清理任务时出错: {e}")
        finally:
            try:
                loop.close()
            except Exception:
                pass
            asyncio.set_event_loop(None)

