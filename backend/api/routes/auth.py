"""
认证相关路由
包括：用户登录、注册、Token验证
"""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config import get_async_db
from models.auth import (
    LoginRequest, CheckTokenRequest,
    RegisterAdminRequest, RegisterWithInviteRequest,
)
from services.auth import verify_login, generate_token, save_token, verify_token
from services.user import create_user
from sqlalchemy import select
from models.auth import User, AdminInvite
from datetime import datetime, timedelta
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
                    "name": user.name,
                    "is_admin": bool(getattr(user, 'is_admin', 0)),
                    "parent_admin_id": getattr(user, 'parent_admin_id', None)
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


# @router.post("/register")
# async def register(request: LoginRequest, db: AsyncSession = Depends(get_async_db)):
#     """
#     用户注册接口
#     """
#     try:
#         # 创建新用户
#         new_user = await create_user(
#             db=db,
#             username=request.username,
#             password=request.password
#         )
#         
#         # 自动登录，生成 token
#         token = generate_token(new_user.user_id)
#         success = await save_token(db, new_user.user_id, token)
#         
#         if not success:
#             return JSONResponse(
#                 status_code=200,
#                 content=jsonable_encoder({
#                     "code": 500,
#                     "message": "注册成功但Token生成失败",
#                     "type": "warning",
#                     "data": None
#                 })
#             )
#         
#         return JSONResponse(
#             status_code=200,
#             content=jsonable_encoder({
#                 "code": 200,
#                 "message": "注册成功",
#                 "type": "success",
#                 "data": {
#                     "token": token,
#                     "user_id": new_user.user_id,
#                     "username": new_user.username,
#                     "name": new_user.name,
#                     "is_admin": bool(getattr(new_user, 'is_admin', 0)),
#                     "parent_admin_id": getattr(new_user, 'parent_admin_id', None)
#                 }
#             })
#         )
#     except ValueError as e:
#         return JSONResponse(
#             status_code=200,
#             content=jsonable_encoder({
#                 "code": 400,
#                 "message": str(e),
#                 "type": "error",
#                 "data": None
#             })
#         )
#     except Exception as e:
#         mylog.error(f"注册失败: {str(e)}")
#         return JSONResponse(
#             status_code=200,
#             content=jsonable_encoder({
#                 "code": 500,
#                 "message": f"注册失败: {str(e)}",
#                 "type": "error",
#                 "data": None
#             })
#         )


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
                    "name": user.name,
                    "is_admin": bool(getattr(user, 'is_admin', 0)),
                    "parent_admin_id": getattr(user, 'parent_admin_id', None)
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


@router.post("/register-admin")
async def register_admin(request: RegisterAdminRequest, db: AsyncSession = Depends(get_async_db)):
    """注册管理员：
    - 若系统不存在任何管理员，则允许直接创建首个管理员
    - 否则需提供 ADMIN_REGISTER_CODE（环境变量）匹配才允许
    """
    try:
        # 是否已有管理员
        result = await db.execute(select(User).where(User.is_admin == 1))
        existing_admin = result.scalar_one_or_none()
        if existing_admin:
            import os
            expect_code = os.getenv('ADMIN_REGISTER_CODE')
            if not expect_code or request.admin_code != expect_code:
                return JSONResponse(status_code=200, content=jsonable_encoder({
                    "code": 403, "message": "不允许创建管理员", "type": "error", "data": None
                }))

        # 创建管理员
        new_admin = await create_user(db, username=request.username, password=request.password)
        # 将其设为管理员
        new_admin.is_admin = 1
        await db.commit()
        await db.refresh(new_admin)

        token = generate_token(new_admin.user_id)
        await save_token(db, new_admin.user_id, token)
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 200, "message": "管理员创建成功", "type": "success",
            "data": {
                "token": token,
                "user_id": new_admin.user_id,
                "username": new_admin.username,
                "name": new_admin.name,
                "is_admin": True,
                "parent_admin_id": None
            }
        }))
    except Exception as e:
        mylog.error(f"管理员注册失败: {str(e)}")
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 500, "message": f"管理员注册失败: {str(e)}", "type": "error", "data": None
        }))


@router.post("/register-with-invite")
async def register_with_invite(request: RegisterWithInviteRequest, db: AsyncSession = Depends(get_async_db)):
    """通过邀请码注册为某管理员成员"""
    try:
        # 校验邀请码
        result = await db.execute(select(AdminInvite).where(AdminInvite.code == request.invite_code))
        invite = result.scalar_one_or_none()
        if not invite or invite.status != 'unused':
            return JSONResponse(status_code=200, content=jsonable_encoder({
                "code": 400, "message": "邀请码无效", "type": "error", "data": None
            }))
        if invite.expire_time and invite.expire_time < datetime.utcnow():
            return JSONResponse(status_code=200, content=jsonable_encoder({
                "code": 400, "message": "邀请码已过期", "type": "error", "data": None
            }))
        # 创建成员用户
        new_user = await create_user(db, username=request.username, password=request.password)
        # 归属管理员
        new_user.parent_admin_id = invite.admin_id
        # 若未提供手机号，默认用用户名作为手机号标识，便于后台按成员聚合记录
        if not getattr(new_user, 'phone', None):
            new_user.phone = new_user.username
        await db.commit()
        await db.refresh(new_user)

        # 消费邀请码
        invite.status = 'used'
        invite.used_by_user_id = new_user.user_id
        await db.commit()

        token = generate_token(new_user.user_id)
        await save_token(db, new_user.user_id, token)
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 200, "message": "注册成功", "type": "success",
            "data": {
                "token": token,
                "user_id": new_user.user_id,
                "username": new_user.username,
                "name": new_user.name,
                "is_admin": False,
                "parent_admin_id": new_user.parent_admin_id
            }
        }))
    except Exception as e:
        mylog.error(f"邀请码注册失败: {str(e)}")
        return JSONResponse(status_code=200, content=jsonable_encoder({
            "code": 500, "message": f"邀请码注册失败: {str(e)}", "type": "error", "data": None
        }))
