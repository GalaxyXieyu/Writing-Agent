import math
from typing import Optional

from fastapi import APIRouter, Depends, Body
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
from ai.llm.llm_factory import LLMFactory
from langchain_openai import ChatOpenAI
from models.model_config import ModelConfigCreate


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


@router.post("/verify")
async def verify_api(
    model_id: Optional[int] = None,
    user_id: Optional[str] = None,
    body: Optional[ModelConfigCreate] = Body(default=None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    简单连通性校验：
    - 若给定 model_id，用该配置创建 ChatOpenAI 并发起一次极短上下文/最大 1 token 的请求。
    - 否则取默认模型。
    返回 200 表示可用，401 表示鉴权失败，其它为后端或网络问题。
    """
    try:
        if body is not None:
            # 未保存前的临时校验，直接用表单参数构建客户端
            llm = ChatOpenAI(
                temperature=float(body.temperature or 0.2),
                model=body.model,
                openai_api_key=body.api_key,
                openai_api_base=body.base_url,
                max_tokens=body.max_tokens,
            )
        else:
            if model_id:
                llm = await LLMFactory.get_llm_by_id(db, model_id)
            else:
                llm = await LLMFactory.get_default_llm(db, user_id=user_id)
            if not llm:
                return JSONResponse(status_code=200, content=jsonable_encoder({
                    "code": 404, "type": "error", "message": "未找到可用模型配置", "data": None
                }))
        # 触发一次极小请求做连通性验证
        try:
            _ = llm.invoke("ping")  # OpenAI 兼容实现会走一个最小请求
        except Exception as e:
            msg = str(e)
            if "401" in msg or "AuthenticationError" in msg or "unauthorized" in msg.lower() or "invalid" in msg.lower():
                return JSONResponse(status_code=200, content=jsonable_encoder({
                    "code": 401, "type": "error", "message": "AI模型API认证失败，请检查API密钥配置", "data": None
                }))
            return JSONResponse(status_code=200, content=jsonable_encoder({
                "code": 500, "type": "error", "message": f"连通性校验失败: {msg}", "data": None
            }))
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 200, "type": "success", "message": "验证通过", "data": True
        }))
    except Exception as e:
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 500, "type": "error", "message": f"验证异常: {str(e)}", "data": None
        }))
