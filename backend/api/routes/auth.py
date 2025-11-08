"""
认证相关路由
包括：用户登录、注册、Token验证
"""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_async_db
from models.auth import LoginRequest, CheckTokenRequest
from services.auth import verify_login, generate_token, save_token, verify_token
from services.user import create_user
from utils.logger import mylog

router = APIRouter()


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    """
    用户登录接口
    """
    try:
        user = await verify_login(db, request.username, request.password)
        
        if not user:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({
                    "code": 401,
                    "message": "用户名或密码错误",
                    "type": "error",
                    "data": None
                })
            )
        
        token = generate_token(user.user_id)
        success = await save_token(db, user.user_id, token)
        
        if not success:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({
                    "code": 500,
                    "message": "Token生成失败",
                    "type": "error",
                    "data": None
                })
            )
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "登录成功",
                "type": "success",
                "data": {
                    "token": token,
                    "user_id": user.user_id,
                    "username": user.username,
                    "name": user.name
                }
            })
        )
    except Exception as e:
        mylog.error(f"登录失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"登录失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )


@router.post("/register")
async def register(request: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    """
    用户注册接口
    """
    try:
        # 创建新用户
        new_user = await create_user(
            db=db,
            username=request.username,
            password=request.password
        )
        
        # 自动登录，生成 token
        token = generate_token(new_user.user_id)
        success = await save_token(db, new_user.user_id, token)
        
        if not success:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({
                    "code": 500,
                    "message": "注册成功但Token生成失败",
                    "type": "warning",
                    "data": None
                })
            )
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "注册成功",
                "type": "success",
                "data": {
                    "token": token,
                    "user_id": new_user.user_id,
                    "username": new_user.username,
                    "name": new_user.name
                }
            })
        )
    except ValueError as e:
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 400,
                "message": str(e),
                "type": "error",
                "data": None
            })
        )
    except Exception as e:
        mylog.error(f"注册失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"注册失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )


@router.post("/checkToken")
async def check_token(request: CheckTokenRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Token验证接口
    """
    try:
        user = await verify_token(db, request.key)
        
        if not user:
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder({
                    "code": 401,
                    "message": "Token无效或已过期",
                    "type": "error",
                    "data": None
                })
            )
        
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 200,
                "message": "Token有效",
                "type": "success",
                "data": {
                    "user_id": user.user_id,
                    "username": user.username,
                    "name": user.name
                }
            })
        )
    except Exception as e:
        mylog.error(f"Token验证失败: {str(e)}")
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({
                "code": 500,
                "message": f"Token验证失败: {str(e)}",
                "type": "error",
                "data": None
            })
        )
