from fastapi import APIRouter
from . import auth, file, solution, templates, tasks, model_config, prompt_config

api_router = APIRouter()
# 认证路由直接挂在 /api 下
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(solution.router, prefix="/solution", tags=["solution"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(file.router, prefix="/file", tags=["file"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(model_config.router, prefix="/model-config", tags=["model-config"])
api_router.include_router(prompt_config.router, prefix="/prompt-config", tags=["prompt-config"])