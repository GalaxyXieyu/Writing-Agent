from fastapi import APIRouter
from . import file, solution, templates, tasks, model_config

api_router = APIRouter()
api_router.include_router(solution.router, prefix="/solution", tags=["solution"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(file.router, prefix="/file", tags=["file"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(model_config.router, prefix="/model-config", tags=["model-config"])