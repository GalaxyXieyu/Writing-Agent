管理员与成员管理接口简表

1) 管理员注册
- POST /api/register-admin
  - body: { username, password, admin_code? }
  - 规则：若系统无管理员可直开；否则需 env: ADMIN_REGISTER_CODE 匹配。

2) 邀请码注册成员
- POST /api/register-with-invite
  - body: { username, password, invite_code }

3) 管理端（需 Authorization: Bearer <token> 且用户 is_admin=1）
- POST /api/admin/invite/create
  - body: { expire_hours?: 24 }
  - resp: { invite_code, expire_time }

- GET /api/admin/users
  - query: { kw?, pageNum?, pageSize? }
  - resp: { total, list: [{ user_id, username, name, phone, status }] }

- POST /api/admin/users/reset-password
  - body: { user_id, new_password }

- POST /api/admin/users/status
  - body: { user_id, status: 'Y'|'N' }

- GET /api/admin/records
  - query: { member_user_id?, member_phone?, type?, kw?, time_from?, time_to?, pageNum?, pageSize? }
  - 类型：solution（文章方案，来自 ai_solution_save）/file（文件，来自 ai_file_rel）
  - 兼容历史：按手机号与成员归属（parent_admin_id）做范围约束

备注
- 登录/校验返回新增 data 字段：is_admin、parent_admin_id；前端据此显隐管理 Tab。
- 推荐使用 Authorization 头传递 token；目前也兼容 query 参数 token（将逐步移除）。
