-- 强制使用 utf8mb4，避免中文乱码
SET NAMES utf8mb4;
-- 默认管理员账号：admin / admin123
-- 默认测试账号：test / test123

-- 创建用户表
CREATE TABLE IF NOT EXISTS ai_user (
  user_id VARCHAR(255) PRIMARY KEY COMMENT '用户ID',
  username VARCHAR(255) NOT NULL UNIQUE COMMENT '用户名',
  password VARCHAR(255) NOT NULL COMMENT '密码',
  phone VARCHAR(100) COMMENT '手机号',
  name VARCHAR(255) COMMENT '姓名',
  create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  status VARCHAR(10) DEFAULT 'Y' COMMENT '状态，Y有效，N无效',
  is_admin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否管理员，1是，0否',
  parent_admin_id VARCHAR(255) NULL COMMENT '所属管理员用户ID（成员归属）',
  INDEX idx_username (username),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建用户Token表
CREATE TABLE IF NOT EXISTS ai_user_token (
  token_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Token主键',
  user_id VARCHAR(255) NOT NULL COMMENT '用户ID',
  token VARCHAR(255) NOT NULL UNIQUE COMMENT 'Token值',
  expire_time TIMESTAMP NOT NULL COMMENT '过期时间',
  create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_user_id (user_id),
  INDEX idx_token (token),
  INDEX idx_expire_time (expire_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户Token表';

-- 说明：将 admin 设为管理员（is_admin=1），test 为普通用户（is_admin=0）
INSERT INTO ai_user (user_id, username, password, name, phone, create_time, status, is_admin)
VALUES 
  ('admin', 'admin', 'admin123', '系统管理员', NULL, NOW(), 'Y', 1),
  ('test_user', 'test', 'test123', '测试用户', NULL, NOW(), 'Y', 0)
ON DUPLICATE KEY UPDATE status = 'Y', is_admin = VALUES(is_admin);

-- 创建管理员邀请表（若不存在）
CREATE TABLE IF NOT EXISTS ai_invite (
  id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
  code VARCHAR(64) NOT NULL UNIQUE COMMENT '邀请码',
  admin_id VARCHAR(255) NOT NULL COMMENT '邀请方管理员用户ID',
  status VARCHAR(16) NOT NULL DEFAULT 'unused' COMMENT '状态：unused/used/expired',
  expire_time DATETIME NULL COMMENT '过期时间',
  used_by_user_id VARCHAR(255) NULL COMMENT '被谁使用',
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  KEY idx_admin_id (admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员邀请表';
