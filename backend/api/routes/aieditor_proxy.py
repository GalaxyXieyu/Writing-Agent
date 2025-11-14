from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from config import get_async_db
from ai.llm.llm_factory import LLMFactory
from models.auth import User, UserToken
from services.model_config import list_model_configs, get_default_model
from models.model_config import ModelConfigQuery
from utils.logger import mylog

router = APIRouter()


async def get_current_user(db: AsyncSession, token: str) -> Optional[User]:
    result = await db.execute(select(UserToken).where(UserToken.token == token, UserToken.expire_time > datetime.now()))
    t = result.scalar_one_or_none()
    if not t:
        return None
    result = await db.execute(select(User).where(User.user_id == t.user_id, User.status == 'Y'))
    return result.scalar_one_or_none()


def _extract_token(authorization: Optional[str], token_param: Optional[str]) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return token_param


@router.get("/model-config/aieditor")
async def aieditor_model_config(db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None):
    tok = _extract_token(authorization, token)
    user = await get_current_user(db, tok) if tok else None
    user_id = getattr(user, 'user_id', None)
    is_admin = bool(getattr(user, 'is_admin', 0)) if user else False

    # 读取可用模型列表（当前用户可见且有效）
    q = ModelConfigQuery(page=1, page_size=100, user_id=None, status_cd='Y')
    rows, _total = await list_model_configs(db, q)
    # 默认模型
    default_obj = await get_default_model(db, user_id=user_id)
    default_id = getattr(default_obj, 'id', None) if default_obj else (rows[0].id if rows else None)

    # 提供器：以名称为 key 的对象，AiEditor 某些版本更偏好这种结构
    providers = {
        # 代理模式（安全，推荐）：前端 -> 本服务 /api/aieditor -> 转发到真实模型
        "proxy": {
            "type": "openai",
            "baseURL": "/api/aieditor",
            "apiKey": "use-header"
        }
    }
    # 模型：使用后端配置的实际 model 字段作为唯一名，例如 'glm-4-flashx'
    models = {}
    for r in rows:
        model_name = getattr(r, 'model', None) or f"model-{r.id}"
        # 如果是管理员，则暴露“直连” Provider，名字与模型 ID 绑定，baseURL/apiKey 取自数据库
        provider_name = "proxy"
        if is_admin:
            provider_name = f"openai-{r.id}"
            providers[provider_name] = {
                "type": "openai",
                "baseURL": getattr(r, 'base_url', None) or '',
                "apiKey": getattr(r, 'api_key', None) or ''
            }
        models[model_name] = {
            "provider": provider_name,
            "displayName": getattr(r, 'name', None) or model_name,
            "id": r.id
        }

    # 默认模型名：优先取默认配置的 model 字段
    if default_obj:
        default_name = getattr(default_obj, 'model', None) or f"model-{default_obj.id}"
    elif rows:
        default_name = getattr(rows[0], 'model', None) or f"model-{rows[0].id}"
    else:
        default_name = None

    data = {
        "providers": providers,
        "models": models,
        "defaults": {
            "bubblePanelModel": default_name,
            "commandPanelModel": default_name,
        }
    }
    try:
        mylog.info(
            "[aieditor_model_config] user_id=%s, models=%s, default=%s",
            user_id,
            list(models.keys()),
            default_name,
        )
    except Exception:
        pass
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "type": "success", "message": "ok", "data": data
    }))


def _parse_model_id(model_field) -> Optional[int]:
    if model_field is None:
        return None
    try:
        if isinstance(model_field, int):
            return model_field
        s = str(model_field)
        if s.startswith("model-"):
            return int(s.split("-", 1)[1])
        return int(s)
    except Exception:
        return None


def _combine_messages(messages: List[Dict]) -> str:
    parts = []
    for m in messages or []:
        role = m.get('role', 'user')
        content = m.get('content', '')
        if not content:
            continue
        if role == 'system':
            parts.append(f"[系统]\n{content}\n")
        elif role == 'assistant':
            parts.append(f"[助手]\n{content}\n")
        else:
            parts.append(f"[用户]\n{content}\n")
    return "\n".join(parts).strip()


def _format_openai_sse_chunk(text: str, idx: int = 0) -> str:
    payload = {
        "id": f"chatcmpl-{idx}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "model": "writing-agent",
        "choices": [{
            "index": 0,
            "delta": {"content": text},
            "finish_reason": None
        }]
    }
    return f"data: {jsonable_encoder(payload)}\n\n"


def _format_openai_sse_done() -> str:
    return "data: [DONE]\n\n"


async def _get_llm_for_request(db: AsyncSession, model_field, user_id: Optional[str]):
    model_id = _parse_model_id(model_field)
    llm = None
    if model_id is not None:
        llm = await LLMFactory.get_llm_by_id(db, model_id)
    # 若传的是模型名称字符串（如 'glm-4-flashx'），尝试按名称解析
    if not llm and isinstance(model_field, str) and model_field and not model_field.startswith('model-'):
        q = ModelConfigQuery(page=1, page_size=200, status_cd='Y')
        rows, _ = await list_model_configs(db, q)
        for r in rows:
            if getattr(r, 'model', None) == model_field:
                llm = await LLMFactory.get_llm_by_id(db, r.id)
                break
    if not llm:
        llm = await LLMFactory.get_default_llm(db, user_id=user_id)
    return llm


@router.post("/chat/completions")
@router.post("/chat-completions")
@router.post("/v1/chat/completions")
async def aieditor_chat_completions(req: Request, db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None):
    tok = _extract_token(authorization, token)
    user = await get_current_user(db, tok) if tok else None
    user_id = getattr(user, 'user_id', None)

    body = await req.json()
    model_field = body.get('model')
    messages = body.get('messages') or []
    stream = bool(body.get('stream', True))
    action = (req.query_params.get('action') or '').strip()  # 可选：polish|simplify|enrich|translate|summarize

    # 将不同 action 转换为系统提示
    action_prompts = {
        'polish': '请在不改变原意的前提下润色优化以下文本，提升表达清晰度与逻辑性。',
        'simplify': '请将以下文本简化为更简洁、通俗易懂的表达，保留核心要点。',
        'enrich': '请适度扩写以下文本，增加必要的细节与论据，保持原有风格与结构。',
        'translate': '请将以下文本翻译为中文，保留段落结构与专有名词。',
        'summarize': '请总结以下文本的关键要点，输出 3-5 条要点。',
    }

    try:
        model_id_guess = _parse_model_id(model_field)
        try:
            mylog.info("[aieditor_chat] user_id=%s, model_field=%s, model_id_guess=%s, action=%s, stream=%s",
                       user_id, model_field, model_id_guess, action, stream)
        except Exception:
            pass
        llm = await _get_llm_for_request(db, model_field, user_id)
        if not llm:
            return JSONResponse(status_code=200, content=jsonable_encoder({
                "code": 404, "type": "error", "message": "未找到可用模型，请在模型配置中添加并设为默认", "data": None
            }))

        sys_prompt = action_prompts.get(action) or ''
        prompt = _combine_messages(messages)
        if sys_prompt:
            prompt = f"{sys_prompt}\n\n---\n\n{prompt}"

        async def gen():
            try:
                if stream:
                    # 使用 LangChain OpenAI 兼容客户端进行流式输出
                    for chunk in llm.stream(prompt):
                        text = getattr(chunk, 'content', None) or str(chunk)
                        if text:
                            yield _format_openai_sse_chunk(text)
                else:
                    result = llm.invoke(prompt)
                    text = getattr(result, 'content', None) or str(result)
                    # 非流式也按 OpenAI 结构一次性返回
                    payload = {
                        "id": "chatcmpl-final",
                        "object": "chat.completion",
                        "created": int(datetime.now().timestamp()),
                        "model": "writing-agent",
                        "choices": [{
                            "index": 0,
                            "message": {"role": "assistant", "content": text},
                            "finish_reason": "stop"
                        }]
                    }
                    yield f"data: {jsonable_encoder(payload)}\n\n"
                yield _format_openai_sse_done()
            except Exception as e:
                mylog.exception(f"/aieditor/chat-completions error: {e}")
                # 结束流，避免前端挂起
                yield _format_openai_sse_done()

        return StreamingResponse(gen(), media_type="text/event-stream; charset=utf-8")
    except Exception as e:
        mylog.exception(f"/aieditor/chat-completions exception: {e}")
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 500, "type": "error", "message": f"服务异常: {str(e)}", "data": None
        }))
