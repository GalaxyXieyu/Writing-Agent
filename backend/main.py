from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.api import api_router
from initialization import init_database
import logging

logging.basicConfig(level=logging.INFO)


app = FastAPI()
# 配置跨域中间件，不限制任何来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=False,  # 无需携带 Cookie，避免与通配符冲突
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """健康检查端点，用于容器探针与状态检测"""
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    # 启动时初始化数据库表（幂等）
    await init_database()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=29847)