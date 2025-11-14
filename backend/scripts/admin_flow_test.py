#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一键验证脚本：管理员创建邀请码 -> 成员注册 -> 保存自定义模板 -> 保存文章(解决方案) -> 管理员查询历史 -> 管理员重置成员密码

无需模型/LLM依赖，避免调用流式生成接口（/solution/generate-article、/templates/create 等）。

用法示例：
  python3 backend/scripts/admin_flow_test.py \
    --base http://127.0.0.1:29847/api \
    --admin-username admin_auto \
    --admin-password admin123 \
    [--admin-code <ADMIN_REGISTER_CODE>]

说明：
  - 若系统首个管理员尚未创建，无需 --admin-code 即可创建。
  - 若系统已存在管理员，创建管理员会被拒绝，此时脚本会自动改为使用提供的账号登录。
  - 生成的成员账号与数据会随机命名，互不冲突。
  - 历史记录通过 /api/admin/records 查询（type=solution），数据来源为 /api/solution/solutionSave。
"""

import argparse
import json
import random
import string
import sys
import time
from urllib import request, parse, error


def _json_headers(token: str = None):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def http_post(base: str, path: str, body: dict, token: str = None):
    url = f"{base}{path}"
    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers=_json_headers(token), method="POST")
    try:
        with request.urlopen(req, timeout=20) as resp:
            payload = resp.read()
            return json.loads(payload.decode("utf-8"))
    except error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            raise
    except Exception:
        raise


def http_get(base: str, path: str, params: dict = None, token: str = None):
    qs = f"?{parse.urlencode(params)}" if params else ""
    url = f"{base}{path}{qs}"
    req = request.Request(url, headers=_json_headers(token), method="GET")
    try:
        with request.urlopen(req, timeout=20) as resp:
            payload = resp.read()
            return json.loads(payload.decode("utf-8"))
    except error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            raise
    except Exception:
        raise


def rand_suffix(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def assert_code_ok(resp: dict, step: str):
    code = resp.get("code") if isinstance(resp, dict) else None
    if code != 200:
        raise SystemExit(f"[{step}] 失败: code={code}, resp={resp}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:29847/api", help="API Base，如 http://127.0.0.1:29847/api")
    ap.add_argument("--admin-username", default=f"admin_{rand_suffix()}")
    ap.add_argument("--admin-password", default="admin123")
    ap.add_argument("--admin-code", default=None, help="ADMIN_REGISTER_CODE（若系统已有管理员时需要）")
    args = ap.parse_args()

    base = args.base.rstrip("/")

    # 0) 健康检查
    try:
        health = http_get(base, "/health")
        if health.get("status") != "ok":
            raise SystemExit(f"[health] 异常: {health}")
        print("health: ok")
    except Exception as e:
        raise SystemExit(f"无法连接后端 {base}: {e}")

    # 1) 注册管理员（若已存在则直接登录）
    print("注册/登录 管理员…")
    admin_token = None
    admin_user_id = None
    reg_admin_resp = http_post(base, "/register-admin", {
        "username": args.admin_username,
        "password": args.admin_password,
        "admin_code": args.admin_code
    })
    if reg_admin_resp.get("code") == 200:
        data = reg_admin_resp.get("data") or {}
        admin_token = data.get("token")
        admin_user_id = data.get("user_id")
        print(f"管理员创建成功: user_id={admin_user_id}")
    else:
        # 已有管理员，则尝试登录
        login_resp = http_post(base, "/login", {
            "username": args.admin_username,
            "password": args.admin_password
        })
        assert_code_ok(login_resp, "管理员登录")
        data = login_resp.get("data") or {}
        if not data.get("is_admin"):
            raise SystemExit("提供的账号不是管理员账号，请更换 --admin-username")
        admin_token = data.get("token")
        admin_user_id = data.get("user_id")
        print(f"管理员登录成功: user_id={admin_user_id}")

    # 2) 管理员创建邀请码
    print("创建邀请码…")
    invite_resp = http_post(base, "/admin/invite/create", {"expire_hours": 24}, token=admin_token)
    assert_code_ok(invite_resp, "创建邀请码")
    invite_code = (invite_resp.get("data") or {}).get("invite_code")
    print(f"邀请码: {invite_code}")

    # 3) 成员使用邀请码注册
    member_username = f"member_{rand_suffix()}"
    member_password = "m123456"
    print(f"注册成员: {member_username}…")
    member_reg = http_post(base, "/register-with-invite", {
        "username": member_username,
        "password": member_password,
        "invite_code": invite_code
    })
    assert_code_ok(member_reg, "成员注册")
    member_data = member_reg.get("data") or {}
    member_token = member_data.get("token")
    member_user_id = member_data.get("user_id")
    print(f"成员注册成功: user_id={member_user_id}")

    # 4) 为成员保存一个“自定义模板”（不用LLM）
    print("保存自定义模板（非LLM）…")
    tpl_resp = http_post(base, "/templates/templateSave", {
        "userId": member_user_id,
        "titleName": "示例模板-公司介绍",
        "writingRequirement": "正式、简洁，包含公司概述与亮点",
        "originalTemplate": [
            {"titleName": "一、公司概述", "writingRequirement": "简述背景与核心业务"},
            {"titleName": "二、产品亮点", "writingRequirement": "列出3-5个差异化优势"}
        ]
    })
    assert_code_ok(tpl_resp, "保存模板")
    print("模板已保存。")

    # 5) 成员保存一篇“文章/解决方案”记录（非LLM）
    # 注意：管理员 /admin/records 通过成员手机号聚合 solution/file 历史。
    # 这里直接指定一个手机号写入记录，并通过该手机号查询。
    demo_phone = f"139{random.randint(1000,9999)}{random.randint(1000,9999)}"
    print(f"保存文章记录（手机号={demo_phone}）…")
    save_sol = http_post(base, "/solution/solutionSave", {
        "solution_title": "示例文章-企业宣传稿",
        "solution_content": "这是一篇用于接口联调验证的示例文章。",
        "create_phone": demo_phone,
        "create_name": member_username
    })
    assert_code_ok(save_sol, "保存文章")
    print("文章已保存。")

    # 6) 管理员查询历史记录（按手机号筛选 solution）
    print("管理员查询历史记录…")
    rec = http_get(base, "/admin/records", params={
        "member_phone": demo_phone,
        "type": "solution",
        "pageNum": 1,
        "pageSize": 10
    }, token=admin_token)
    assert_code_ok(rec, "查询历史记录")
    data = rec.get("data") or {}
    total = data.get("total")
    items = data.get("list") or []
    print(f"历史记录: total={total}, 展示{len(items)}条")
    if items:
        print("示例记录:")
        print(json.dumps(items[0], ensure_ascii=False, indent=2))

    # 7) 管理员重置该成员的密码（演示成员管理能力）
    print("管理员重置成员密码…")
    reset_resp = http_post(base, "/admin/users/reset-password", {
        "user_id": member_user_id,
        "new_password": "m123456_new"
    }, token=admin_token)
    assert_code_ok(reset_resp, "重置成员密码")
    print("成员密码已重置。")

    print("\n全部流程完成 ✅")


if __name__ == "__main__":
    main()
