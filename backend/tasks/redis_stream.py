"""
Redis Stream 工具类
用于管理任务流式内容的存储和读取
"""
import redis
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
from utils.logger import mylog


class RedisStreamManager:
    """Redis Stream 管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        self.stream_expire_days = 7
    
    def _get_stream_key(self, task_id: str) -> str:
        """获取 Stream key"""
        return f"task:{task_id}:stream"
    
    def _get_meta_key(self, task_id: str) -> str:
        """获取任务元信息 key"""
        return f"task:{task_id}:meta"
    
    def write_content(self, task_id: str, content: str) -> bool:
        """
        写入内容片段到 Redis Stream
        """
        try:
            stream_key = self._get_stream_key(task_id)
            self.redis_client.xadd(stream_key, {"content": content})
            self.redis_client.expire(stream_key, timedelta(days=self.stream_expire_days))
            return True
        except Exception as e:
            mylog.error(f"写入 Redis Stream 失败: {e}")
            return False
    
    def read_all_content(self, task_id: str) -> List[Dict]:
        """
        读取所有已生成的内容
        返回格式: [{"id": "xxx", "content": "xxx"}, ...]
        """
        try:
            stream_key = self._get_stream_key(task_id)
            messages = self.redis_client.xrange(stream_key, "-", "+")
            result = []
            for msg_id, fields in messages:
                result.append({
                    "id": msg_id,
                    "content": fields.get("content", "")
                })
            return result
        except Exception as e:
            mylog.error(f"读取 Redis Stream 失败: {e}")
            return []
    
    def read_new_content(self, task_id: str, last_id: str = "0") -> List[Dict]:
        """
        读取新内容（从指定 ID 之后）
        """
        try:
            stream_key = self._get_stream_key(task_id)
            if last_id == "0":
                messages = self.redis_client.xrange(stream_key, "-", "+")
            else:
                messages = self.redis_client.xread({stream_key: last_id}, count=100, block=0)
                if messages:
                    messages = messages[0][1]
                else:
                    messages = []
            
            result = []
            for msg_id, fields in messages:
                result.append({
                    "id": msg_id,
                    "content": fields.get("content", "")
                })
            return result
        except Exception as e:
            mylog.error(f"读取新内容失败: {e}")
            return []
    
    def update_task_meta(self, task_id: str, status: str, progress: int = 0, 
                        error_message: Optional[str] = None) -> bool:
        """
        更新任务元信息
        """
        try:
            meta_key = self._get_meta_key(task_id)
            meta_data = {
                "status": status,
                "progress": str(progress),
                "updated_at": datetime.now().isoformat()
            }
            if error_message:
                meta_data["error_message"] = error_message
            
            self.redis_client.hset(meta_key, mapping=meta_data)
            self.redis_client.expire(meta_key, timedelta(days=self.stream_expire_days))
            return True
        except Exception as e:
            mylog.error(f"更新任务元信息失败: {e}")
            return False
    
    def get_task_meta(self, task_id: str) -> Optional[Dict]:
        """
        获取任务元信息
        """
        try:
            meta_key = self._get_meta_key(task_id)
            meta_data = self.redis_client.hgetall(meta_key)
            if meta_data:
                meta_data["progress"] = int(meta_data.get("progress", 0))
            return meta_data if meta_data else None
        except Exception as e:
            mylog.error(f"获取任务元信息失败: {e}")
            return None
    
    def set_task_result(self, task_id: str, result: str) -> bool:
        """
        设置任务最终结果
        """
        try:
            meta_key = self._get_meta_key(task_id)
            self.redis_client.hset(meta_key, "result", result)
            self.redis_client.hset(meta_key, "completed_at", datetime.now().isoformat())
            return True
        except Exception as e:
            mylog.error(f"设置任务结果失败: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        删除任务相关的 Redis 数据
        """
        try:
            stream_key = self._get_stream_key(task_id)
            meta_key = self._get_meta_key(task_id)
            self.redis_client.delete(stream_key)
            self.redis_client.delete(meta_key)
            return True
        except Exception as e:
            mylog.error(f"删除任务数据失败: {e}")
            return False


# 全局实例
redis_stream_manager = RedisStreamManager()

