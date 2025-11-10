-- 在 AICreateTemplate 表中添加 example_output 字段
ALTER TABLE ai_create_template 
ADD COLUMN example_output TEXT NULL COMMENT '示例输出内容' AFTER create_template;

