# 数据库迁移说明

## 数据库管理方式

本项目使用 **SQLAlchemy ORM** 自动管理数据库表结构,不需要手动编写建表 SQL。

### 工作原理

1. **表结构定义**: 在 `models/` 目录下定义 SQLAlchemy 模型
2. **自动建表**: 启动时 `initialization.py` 中的 `Base.metadata.create_all()` 自动创建表
3. **字段迁移**: `migrate_database()` 函数检查并添加缺失的字段

### 添加新表

1. 在 `models/` 目录创建模型文件
2. 在 `initialization.py` 中导入模型: `from models import your_model`
3. 重启服务,表会自动创建

### 添加新字段

**方式一: 修改模型 (推荐)**
- 直接在模型类中添加字段
- 在 `initialization.py` 的 `migrate_database()` 中添加迁移逻辑

**方式二: 仅迁移**
- 在 `migrate_database()` 中添加 ALTER TABLE 语句

### 当前迁移脚本

- `001_create_ai_model_config.sql` - 仅作为参考,实际由 SQLAlchemy 创建

### 注意事项

- ❌ 不要创建新的 SQL 迁移脚本
- ✅ 所有表结构变更都在代码中管理
- ✅ 保持单一数据源,避免维护混乱
