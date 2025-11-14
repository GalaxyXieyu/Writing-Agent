"""
管理员相关路由：创建邀请码、成员管理、记录查询
"""
from fastapi import APIRouter, Depends, Header
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text
from datetime import datetime, timedelta
import secrets

from config import get_async_db
from models.auth import User, AdminInvite, CreateInviteRequest, ResetPasswordRequest, SetUserStatusRequest, AdminRecordsQuery
from models.file import AiFileRel
from models.solution import AiSolutionSave
from utils.logger import mylog

router = APIRouter()


async def get_current_user(db: AsyncSession, token: str) -> User:
    """简化版：从 token 表解析用户；此处为安全考虑，建议复用 services.auth.verify_token。
    这里避免循环依赖，采用 SQL 直接查。
    """
    from models.auth import UserToken
    result = await db.execute(select(UserToken).where(UserToken.token == token, UserToken.expire_time > datetime.now()))
    t = result.scalar_one_or_none()
    if not t:
        return None
    result = await db.execute(select(User).where(User.user_id == t.user_id, User.status == 'Y'))
    return result.scalar_one_or_none()


def json_ok(data=None, message="success"):
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": 200, "message": message, "type": "success", "data": data
    }))


def json_err(msg, code=400):
    return JSONResponse(status_code=200, content=jsonable_encoder({
        "code": code, "message": msg, "type": "error", "data": None
    }))


def _extract_token(authorization: Optional[str], token_param: Optional[str]) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return token_param


@router.post("/invite/create")
async def create_invite(payload: CreateInviteRequest, db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None):
    tok = _extract_token(authorization, token)
    if not tok:
        return json_err("缺少token")
    user = await get_current_user(db, tok)
    if not user or not getattr(user, 'is_admin', 0):
        return json_err("无权限", 403)
    code = secrets.token_urlsafe(12)
    expire_hours = payload.expire_hours or 24
    invite = AdminInvite(
        code=code,
        admin_id=user.user_id,
        status='unused',
        expire_time=datetime.utcnow() + timedelta(hours=expire_hours)
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    return json_ok({"invite_code": invite.code, "expire_time": str(invite.expire_time)})


@router.get("/users")
async def list_members(db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None, kw: str = None, pageNum: int = 1, pageSize: int = 20):
    tok = _extract_token(authorization, token)
    if not tok:
        return json_err("缺少token")
    admin = await get_current_user(db, tok)
    if not admin or not getattr(admin, 'is_admin', 0):
        return json_err("无权限", 403)
    stmt = select(User).where(User.parent_admin_id == admin.user_id)
    if kw:
        stmt = stmt.where(or_(User.username.like(f"%{kw}%"), User.name.like(f"%{kw}%"), User.phone.like(f"%{kw}%")))
    # 分页
    total_result = await db.execute(stmt)
    total = len(total_result.scalars().all())
    offset = (pageNum - 1) * pageSize
    page_stmt = stmt.offset(offset).limit(pageSize)
    page_result = await db.execute(page_stmt)
    records = page_result.scalars().all()
    data = [{
        "user_id": u.user_id,
        "username": u.username,
        "name": u.name,
        "phone": u.phone,
        "status": u.status
    } for u in records]
    return json_ok({"total": total, "list": data})


@router.post("/users/reset-password")
async def reset_member_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None):
    tok = _extract_token(authorization, token)
    if not tok:
        return json_err("缺少token")
    admin = await get_current_user(db, tok)
    if not admin or not getattr(admin, 'is_admin', 0):
        return json_err("无权限", 403)
    # 校验归属
    result = await db.execute(select(User).where(User.user_id == payload.user_id))
    user = result.scalar_one_or_none()
    if not user or user.parent_admin_id != admin.user_id:
        return json_err("目标用户不存在或无权限")
    user.password = payload.new_password
    await db.commit()
    return json_ok()


@router.post("/users/status")
async def set_member_status(payload: SetUserStatusRequest, db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None):
    tok = _extract_token(authorization, token)
    if not tok:
        return json_err("缺少token")
    admin = await get_current_user(db, tok)
    if not admin or not getattr(admin, 'is_admin', 0):
        return json_err("无权限", 403)
    result = await db.execute(select(User).where(User.user_id == payload.user_id))
    user = result.scalar_one_or_none()
    if not user or user.parent_admin_id != admin.user_id:
        return json_err("目标用户不存在或无权限")
    if payload.status not in ('Y', 'N'):
        return json_err("status 仅支持 Y/N")
    user.status = payload.status
    await db.commit()
    return json_ok()


@router.get("/records")
async def list_records(db: AsyncSession = Depends(get_async_db), authorization: str = Header(None), token: str = None,
                       member_user_id: str = None, member_phone: str = None,
                       type: str = None, kw: str = None, time_from: str = None, time_to: str = None,
                       pageNum: int = 1, pageSize: int = 20):
    tok = _extract_token(authorization, token)
    if not tok:
        return json_err("缺少token")
    admin = await get_current_user(db, tok)
    if not admin or not getattr(admin, 'is_admin', 0):
        return json_err("无权限", 403)

    # 兼容旧数据：solution 使用 create_phone，file 使用 create_no
    items = []
    total = 0

    # 时间条件
    def in_time(col):
        conds = []
        if time_from:
            conds.append(col >= text(f"'{time_from} 00:00:00'"))
        if time_to:
            conds.append(col <= text(f"'{time_to} 23:59:59'"))
        return conds

    # 成员解析：兼容历史数据中 create_phone/create_no 可能存 user_id 的情况
    target_phone = member_phone
    member_user = None
    if member_user_id:
        res = await db.execute(select(User).where(User.user_id == member_user_id, User.parent_admin_id == admin.user_id))
        member_user = res.scalar_one_or_none()
        if not target_phone:
            target_phone = member_user.phone if member_user else None
    elif target_phone:
        res = await db.execute(select(User).where(User.phone == target_phone, User.parent_admin_id == admin.user_id))
        member_user = res.scalar_one_or_none()

    # 针对单个成员时的可匹配标识（手机号 + user_id + 兜底用户名）
    def member_allowed_idents(u: User):
        if not u:
            return []
        cands = []
        if getattr(u, 'phone', None):
            cands.append(u.phone)
        if getattr(u, 'user_id', None):
            cands.append(u.user_id)
        if getattr(u, 'username', None):
            cands.append(u.username)
        # 去重并过滤空
        return [x for i, x in enumerate(cands) if x and cands.index(x) == i]

    # 查询 Solution
    if type in (None, '', 'solution'):
        stmt = select(AiSolutionSave).where(AiSolutionSave.status_cd == 'Y')
        # 限制在当前管理员成员范围（同时兼容 create_phone 存为 user_id 的历史数据）
        if member_user:
            idents = member_allowed_idents(member_user)
            if idents:
                stmt = stmt.where(AiSolutionSave.create_phone.in_(idents))
            else:
                stmt = stmt.where(text('1=0'))
        else:
            # 聚合当前管理员下所有成员的可匹配标识
            res = await db.execute(select(User.user_id, User.phone, User.username).where(User.parent_admin_id == admin.user_id))
            rows = res.fetchall()
            idents = []
            for uid, phone, username in rows:
                if phone: idents.append(phone)
                if uid: idents.append(uid)
                if username: idents.append(username)
            # 去重
            idents = list(dict.fromkeys([x for x in idents if x]))
            if idents:
                stmt = stmt.where(AiSolutionSave.create_phone.in_(idents))
            else:
                stmt = stmt.where(text('1=0'))
        if kw:
            stmt = stmt.where(AiSolutionSave.solution_title.like(f"%{kw}%"))
        for c in in_time(AiSolutionSave.create_date):
            stmt = stmt.where(c)
        all_res = await db.execute(stmt)
        sols = all_res.scalars().all()
        total += len(sols)
        items.extend([{
            "type": "solution",
            "id": s.solution_id,
            "title": s.solution_title,
            "owner_phone": s.create_phone,
            "owner_name": s.create_name,
            "created_at": str(s.create_date)
        } for s in sols])

    # 查询 File
    if type in (None, '', 'file'):
        stmt = select(AiFileRel).where(AiFileRel.status_cd != '-1')
        # 限制范围（兼容 create_no 为 user_id 的历史数据）
        if member_user:
            idents = member_allowed_idents(member_user)
            if idents:
                stmt = stmt.where(AiFileRel.create_no.in_(idents))
            else:
                stmt = stmt.where(text('1=0'))
        else:
            res = await db.execute(select(User.user_id, User.phone, User.username).where(User.parent_admin_id == admin.user_id))
            rows = res.fetchall()
            idents = []
            for uid, phone, username in rows:
                if phone: idents.append(phone)
                if uid: idents.append(uid)
                if username: idents.append(username)
            idents = list(dict.fromkeys([x for x in idents if x]))
            if idents:
                stmt = stmt.where(AiFileRel.create_no.in_(idents))
            else:
                stmt = stmt.where(text('1=0'))
        if kw:
            stmt = stmt.where(AiFileRel.file_name.like(f"%{kw}%"))
        for c in in_time(AiFileRel.create_date):
            stmt = stmt.where(c)
        all_res = await db.execute(stmt)
        fs = all_res.scalars().all()
        total += len(fs)
        items.extend([{
            "type": "file",
            "id": f.file_id,
            "title": f.file_name,
            "owner_phone": f.create_no,
            "owner_name": f.create_name,
            "created_at": str(f.create_date)
        } for f in fs])

    # 简单分页（内存分页；若数据多可改为 union + SQL 分页，或分别分页）
    items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    start = (pageNum - 1) * pageSize
    end = start + pageSize
    page_items = items[start:end]
    return json_ok({"total": total, "list": page_items})
