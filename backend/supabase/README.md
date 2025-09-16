# Supabase 配置和迁移

本目录包含项目的 Supabase 配置和数据库迁移文件。

## 目录结构

```
supabase/
├── config.toml              # Supabase 项目配置文件
├── schema.sql               # 当前数据库模式快照
├── schema_snapshot.json     # Supabase 内部使用的快照文件
├── migrations/              # 数据库迁移文件
│   └── 20250916224258_initial_schema.sql
└── README.md                # 本文档
```

## 迁移文件

### 初始迁移 (20250916224258_initial_schema.sql)

这个迁移文件包含了项目的完整数据库模式，包括：

- UUID v7 生成函数
- 用户系统表 (users, profiles)
- 技能系统表 (skill_categories, skills, user_skills)
- 导师匹配系统表 (mentor_matches, mentorship_relationships, mentorship_sessions)
- 消息系统表 (conversations, conversation_participants, messages)
- 订单和支付系统表 (orders, user_wallets, wallet_transactions)
- 文件上传表 (uploaded_files)
- 论坛系统表 (forum_posts, forum_replies, likes)
- 其他辅助表

## 使用方法

### 1. 本地开发

```bash
# 安装 Supabase CLI (不要安装到项目目录中)
curl -o- https://raw.githubusercontent.com/supabase/cli/main/install.sh | bash

# 启动本地 Supabase 服务
supabase start

# 应用迁移到本地数据库
supabase db reset
```

### 2. 生产环境

```bash
# 推送到远程 Supabase 项目
supabase db push
```

### 3. 创建新迁移

当数据库模式发生变化时：

```bash
# 创建新的迁移文件
supabase migration new migration_name

# 编辑迁移文件
# 然后推送到远程
supabase db push
```

## 注意事项

1. **不要将 Supabase CLI 提交到仓库**：CLI 二进制文件已经添加到 `.gitignore`
2. **迁移文件应按时间顺序执行**：文件名中的时间戳确保了正确的执行顺序
3. **测试迁移**：在推送到生产环境前，先在本地测试迁移
4. **备份数据**：在生产环境中应用迁移前务必备份数据

## 数据库连接

本地开发时，数据库连接信息：
- Host: localhost
- Port: 54322
- Database: postgres
- User: postgres
- Password: postgres

生产环境的连接信息请参考 Supabase 项目设置。
