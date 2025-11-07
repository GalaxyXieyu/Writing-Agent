"""
Celery 应用配置

注意：
1. 为了让命令行 `celery -A tasks.celery_app worker` 能自动发现应用，
   这里额外导出变量名 `celery` 指向应用实例（Celery 默认查找名为 `celery` 的变量）。
2. 显式设置默认队列为 `celery`，避免 Worker 以 `-Q` 监听其它队列时收不到默认任务。
"""
from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# 创建 Celery 应用
celery_app = Celery(
    'writingagent',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['tasks.article_tasks']  # 确保任务模块被 Worker 导入
)

# 运行时配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    result_expires=604800,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    # 显式默认队列，和 Celery 默认一致，但更不易踩坑
    task_default_queue='celery'
)

# 为了兼容命令 `celery -A tasks.celery_app worker`
# Celery CLI 会默认寻找变量名 `celery` 的应用实例
celery = celery_app

