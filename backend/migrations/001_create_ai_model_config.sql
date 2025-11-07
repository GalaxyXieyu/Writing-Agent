-- 创建 ai_model_config 表（OpenAI 兼容字段）
CREATE TABLE IF NOT EXISTS ai_model_config (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64) NULL,
  name VARCHAR(128) NOT NULL,
  model VARCHAR(128) NOT NULL,
  api_key VARCHAR(512) NOT NULL,
  base_url VARCHAR(256) NOT NULL,
  temperature VARCHAR(16) NULL,
  max_tokens INT NULL,
  is_default TINYINT(1) NOT NULL DEFAULT 0,
  status_cd CHAR(1) NOT NULL DEFAULT 'Y',
  remark VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_status (status_cd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
