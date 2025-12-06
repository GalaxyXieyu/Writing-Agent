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

-- 创建模板标题表
CREATE TABLE IF NOT EXISTS ai_template_title (
  title_id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '标题编号',
  template_id BIGINT COMMENT '模板编号',
  parent_id BIGINT COMMENT '父标题编号',
  title_name VARCHAR(255) COMMENT '标题名称',
  show_order INT COMMENT '顺序',
  writing_requirement VARCHAR(2000) COMMENT '写作要求',
  reference_output TEXT NULL COMMENT '参考输出内容',
  status_cd VARCHAR(1) COMMENT '有效性，Y有效，N无效',
  INDEX idx_template_id (template_id),
  INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模板标题表';

-- 注意：MySQL 8.0 不支持 ADD COLUMN IF NOT EXISTS
-- 初始化脚本仅在首次启动执行，CREATE TABLE IF NOT EXISTS 已包含所有字段
-- 若需兼容旧数据，请手动执行:
-- ALTER TABLE ai_create_template ADD COLUMN example_output TEXT NULL COMMENT '示例输出内容';
-- ALTER TABLE ai_template_title ADD COLUMN reference_output TEXT NULL COMMENT '参考输出内容';
