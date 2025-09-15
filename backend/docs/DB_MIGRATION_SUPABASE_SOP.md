# 数据库迁移与 Supabase 同步 SOP

本文档说明如何在本项目中安全、高效地对齐本地数据模型与远端 Supabase(PostgreSQL) 数据库结构，并形成可审计的迁移流程。

## 一、前置要求
- 已安装 Poetry，并能在项目根目录运行命令。
- 已配置 `.env`（由 `.env.example` 复制），至少包含：
  - `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_DB_PASSWORD`
  - 或提供 `DATABASE_URL`（优先使用）。
- 本地可访问 Supabase 数据库（默认走 `settings.postgres_url` 构造的直连 DSN）。

## 二、流程总览
1) 开发修改 Pydantic `apps/schemas/*` 与仓储/服务代码。
2) 运行对齐检查，确认本地模型与数据库结构差异。
3) 将远端实际结构导出为 JSON 快照 → 生成标准 `schema.sql`。
4) 审阅并提交 `supabase/schema.sql` 变更。
5) 将 `schema.sql` 应用于远端 Supabase（幂等执行）。
6) 回归验证与监控。

## 三、常用脚本与用途
- 导出远端结构为 JSON 快照
  ```bash
  poetry run python scripts/database/export_schema.py
  ```
  输出：`supabase/schema_snapshot.json`

- 将快照转换为可执行 DDL
  ```bash
  poetry run python scripts/database/snapshot_to_sql.py
  ```
  输出：`supabase/schema.sql`

- 将本地 `schema.sql` 同步到 Supabase（幂等执行，已存在对象会忽略）
  ```bash
  poetry run python scripts/database/migrate_remote.py
  ```

- 基础对齐自检（连通性与关键表存在性）
  ```bash
  poetry run python scripts/database/check_alignment.py
  ```

## 四、标准操作步骤（SOP）
### 1. 同步前检查
- 确认本地变更点（schemas、repositories、services）已通过代码审查与单测。
- 本地能启动服务：
  ```bash
  poetry run uvicorn apps.main:app --reload
  ```
- 快速连接检查：
  ```bash
  poetry run python scripts/database/check_alignment.py
  ```

### 2. 获取“当前远端真实结构”
- 执行：
  ```bash
  poetry run python scripts/database/export_schema.py
  ```
- 产物：`supabase/schema_snapshot.json`（请纳入版本控制，便于审计）

### 3. 标准化生成 DDL
- 执行：
  ```bash
  poetry run python scripts/database/snapshot_to_sql.py
  ```
- 产物：`supabase/schema.sql`
- 审阅 `schema.sql` 差异，关注：
  - 列类型、可空性、默认值
  - 主键、唯一、外键约束
  - 注意：脚本未覆盖索引/触发器/视图/序列，如有需求请手工追加对应 DDL（建议集中维护在 `-- 手工追加` 注释区）。

### 4. 评审与提交
- 将以下文件纳入 PR：
  - `apps/schemas/*`（数据模型）
  - `supabase/schema_snapshot.json`（可选）
  - `supabase/schema.sql`（强制）
- PR 通过后合并主干。

### 5. 远端迁移（对齐 Supabase）
- 在受控环境执行：
  ```bash
  poetry run python scripts/database/migrate_remote.py
  ```
- 该脚本逐条执行 `schema.sql`，对已存在对象报错将自动忽略（幂等）。
- 建议对生产环境：
  - 先在「预生产」项目验证；
  - 生产前快照备份（参考“附录：备份/回滚”）。

### 6. 验证与监控
- 运行对齐检查：
  ```bash
  poetry run python scripts/database/check_alignment.py
  ```
- 启动服务并健康检查：
  ```bash
  poetry run uvicorn apps.main:app --reload
  ```
  - 打开 `http://127.0.0.1:8000/health`
  - 打开 `http://127.0.0.1:8000/docs`
- 关键 API 冒烟（PowerShell 示例）：
  ```powershell
  # 健康检查
  iwr -Uri "http://127.0.0.1:8000/health" -Method GET | % Content

  # AI v2 系统状态
  iwr -Uri "http://127.0.0.1:8000/api/v2/agents/status" -Method GET | % Content
  ```

## 五、变更策略与最佳实践
- 变更原则：先模型、后快照、再 SQL、最后迁移。
- DDL 变更审慎：涉及表/列删除、类型收窄、约束增强前，务必评估数据影响。
- 手工 DDL 管理：将索引/触发器等手工语句集中维护在 `schema.sql` 顶部/底部注释分区，便于审计。
- 版本化：
  - 每次结构变更打 Git Tag（如 `db-2025-09-15`）。
  - `schema.sql` 变更必须走 PR + Code Review。
- 多环境：
  - 开发/预生产/生产的 `.env` 应隔离，严禁混用密钥。

## 六、常见问题（FAQ）
- Q: Supabase 不支持原生 SQL 吗？
  - A: 本项目通过 PostgreSQL 直连（`settings.postgres_url`）执行原生 SQL，完全支持。
- Q: 脚本未生成索引怎么办？
  - A: 目前生成器只覆盖列与约束，索引需在 `schema.sql` 手工追加，例如：
    ```sql
    CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
    ```
- Q: 并发执行是否安全？
  - A: `migrate_remote.py` 逐条执行且幂等，建议串行在 CI 或运维机执行。

## 七、附录：备份/回滚建议
- 备份（任选其一）：
  - Supabase 控制台手动备份。
  - `pg_dump`（需要数据库直连权限）：
    ```bash
    pg_dump "$DATABASE_URL" -Fc -f backup_$(date +%F).dump
    ```
- 回滚：
  - 首选恢复备份。
  - 若仅少量对象，手工写反向 DDL（DROP/ALTER）并评审执行。

---
如需自动化到 CI/CD：在合并到主干后触发以下流水线：
1) `export_schema.py` → `snapshot_to_sql.py` → 校验 `schema.sql` 是否有意外差异；
2) 人工审批后执行 `migrate_remote.py` 到目标环境；
3) 运行健康检查与冒烟测试。
