import math
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_async_db
from models.model_config import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelConfigQuery,
)
from services.model_config import (
    create_model_config,
    get_model_config,
    list_model_configs,
    update_model_config,
    delete_model_config,
    set_default_model,
    get_default_model,
)


router = APIRouter()


@router.post("/create")
async def create_api(body: ModelConfigCreate, db: AsyncSession = Depends(get_async_db)):
    obj = await create_model_config(db, body)
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "创建成功", "data": obj
    }))


@router.get("/list")
async def list_api(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[str] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    status_cd: Optional[str] = 'Y',
    db: AsyncSession = Depends(get_async_db)
):
    q = ModelConfigQuery(page=page, page_size=page_size, user_id=user_id, name=name, model=model, status_cd=status_cd)
    rows, total = await list_model_configs(db, q)
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200,
        "type": "success",
        "message": "查询成功",
        "data": {
            "list": rows,
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": math.ceil(total / page_size) if page_size else 1
        }
    }))


@router.get("/{model_id}")
async def detail_api(model_id: int, db: AsyncSession = Depends(get_async_db)):
    obj = await get_model_config(db, model_id)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到模型配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "查询成功", "data": obj
    }))


@router.put("/{model_id}")
async def update_api(model_id: int, body: ModelConfigUpdate, db: AsyncSession = Depends(get_async_db)):
    obj = await update_model_config(db, model_id, body)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到模型配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "更新成功", "data": obj
    }))


@router.delete("/{model_id}")
async def delete_api(model_id: int, db: AsyncSession = Depends(get_async_db)):
    ok = await delete_model_config(db, model_id)
    if not ok:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到模型配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "删除成功", "data": True
    }))


@router.post("/set-default")
async def set_default_api(model_id: int, db: AsyncSession = Depends(get_async_db)):
    obj = await set_default_model(db, model_id)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到模型配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "设置默认成功", "data": obj
    }))


@router.get("/default")
async def get_default_api(user_id: Optional[str] = None, db: AsyncSession = Depends(get_async_db)):
    obj = await get_default_model(db, user_id=user_id)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到默认模型", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "查询成功", "data": obj
    }))
