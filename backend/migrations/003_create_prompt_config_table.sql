-- 创建 ai_prompt_config 表（提示词配置表）
CREATE TABLE IF NOT EXISTS ai_prompt_config (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prompt_type VARCHAR(64) NOT NULL COMMENT '提示词类型：template_generate/paragraph_generate/template_refresh',
  prompt_content TEXT NOT NULL COMMENT '提示词内容',
  status_cd CHAR(1) NOT NULL DEFAULT 'Y' COMMENT '状态：Y有效，N无效',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_prompt_type (prompt_type),
  INDEX idx_status (status_cd)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI提示词配置表';

