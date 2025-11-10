from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_async_db
from models.prompt_config import (
    PromptConfigCreate,
    PromptConfigUpdate,
)
from services.prompt_config import (
    create_prompt_config,
    get_prompt_config,
    get_prompt_by_type,
    list_prompt_configs,
    update_prompt_config,
    update_prompt_by_type,
    delete_prompt_config,
)


router = APIRouter()


@router.post("/create")
async def create_api(body: PromptConfigCreate, db: AsyncSession = Depends(get_async_db)):
    obj = await create_prompt_config(db, body)
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "创建成功", "data": obj
    }))


@router.get("/list")
async def list_api(db: AsyncSession = Depends(get_async_db)):
    rows = await list_prompt_configs(db)
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200,
        "type": "success",
        "message": "查询成功",
        "data": rows
    }))


@router.get("/type/{prompt_type}")
async def get_by_type_api(prompt_type: str, db: AsyncSession = Depends(get_async_db)):
    obj = await get_prompt_by_type(db, prompt_type)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到提示词配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "查询成功", "data": obj
    }))


@router.get("/{prompt_id}")
async def detail_api(prompt_id: int, db: AsyncSession = Depends(get_async_db)):
    obj = await get_prompt_config(db, prompt_id)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到提示词配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "查询成功", "data": obj
    }))


@router.put("/{prompt_id}")
async def update_api(prompt_id: int, body: PromptConfigUpdate, db: AsyncSession = Depends(get_async_db)):
    obj = await update_prompt_config(db, prompt_id, body)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到提示词配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "更新成功", "data": obj
    }))


@router.put("/type/{prompt_type}")
async def update_by_type_api(prompt_type: str, body: PromptConfigUpdate, db: AsyncSession = Depends(get_async_db)):
    obj = await update_prompt_by_type(db, prompt_type, body)
    if not obj:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到提示词配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "更新成功", "data": obj
    }))


@router.delete("/{prompt_id}")
async def delete_api(prompt_id: int, db: AsyncSession = Depends(get_async_db)):
    ok = await delete_prompt_config(db, prompt_id)
    if not ok:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 404, "type": "error", "message": "未找到提示词配置", "data": None
        }))
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "删除成功", "data": True
    }))

