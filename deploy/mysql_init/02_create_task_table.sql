-- 创建任务表
CREATE TABLE IF NOT EXISTS ai_task (
  task_id VARCHAR(64) PRIMARY KEY COMMENT '任务ID',
  task_type VARCHAR(50) NOT NULL COMMENT '任务类型',
  user_id VARCHAR(255) COMMENT '用户ID',
  status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态',
  progress INT DEFAULT 0 COMMENT '进度百分比',
  input_params TEXT COMMENT '输入参数',
  result LONGTEXT COMMENT '任务结果',
  error_message TEXT COMMENT '错误信息',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  completed_at DATETIME DEFAULT NULL COMMENT '完成时间',
  INDEX idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异步任务表';

