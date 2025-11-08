-- 初始化用户表数据
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

-- 插入初始管理员账号（密码：admin123，未加密）
INSERT INTO ai_user (user_id, username, password, name, phone, create_time, status)
VALUES 
  ('admin', 'admin', 'admin123', '系统管理员', NULL, NOW(), 'Y'),
  ('test_user', 'test', 'test123', '测试用户', NULL, NOW(), 'Y')
ON DUPLICATE KEY UPDATE status = 'Y';
