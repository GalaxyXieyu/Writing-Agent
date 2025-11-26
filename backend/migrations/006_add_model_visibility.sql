-- 添加模型可见性控制字段
-- is_public: 是否公开可见（所有用户可见）
-- visible_to_users: 可见用户ID列表（JSON数组格式，如 ["user1","user2"]）

ALTER TABLE ai_model_config
ADD COLUMN is_public TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否公开可见，1公开，0仅指定用户可见' AFTER is_default,
ADD COLUMN visible_to_users TEXT NULL COMMENT '可见用户ID列表，JSON数组格式' AFTER is_public;

-- 默认所有现有配置为公开可见
UPDATE ai_model_config SET is_public = 1 WHERE is_public IS NULL;
