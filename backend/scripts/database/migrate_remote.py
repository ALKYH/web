#!/usr/bin/env python3
"""
直接对齐远端 Supabase 数据库结构：
- 读取本地 supabase/schema.sql
- 用远端连接（settings.postgres_url）逐条执行 DDL
- 已存在对象（already exists）错误将被忽略

用法：
  poetry run python scripts/database/migrate_remote.py
"""
import os
import re
import sys
from typing import List

import asyncio
import asyncpg
import ssl as _ssl


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQL_PATH = os.path.join(PROJECT_ROOT, 'supabase', 'schema.sql')

# 导入配置
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from libs.config.settings import settings  # noqa: E402


def load_sql_statements(path: str) -> List[str]:
    if not os.path.exists(path):
        raise SystemExit(f"未找到 {path}，请先生成 schema.sql")
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # 去掉行注释与多余空白，仅做简单拆分
    # 注意：本工具生成的 schema.sql 结构简单，按分号拆分即可
    statements: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        # 忽略以 -- 开头的行
        if line.strip().startswith('--'):
            continue
        current.append(line)
        if line.strip().endswith(';'):
            stmt = '\n'.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
    # 末尾残留
    tail = '\n'.join(current).strip()
    if tail:
        statements.append(tail)
    return statements


async def apply_schema() -> None:
    dsn = settings.postgres_url
    ssl_ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = _ssl.CERT_NONE

    conn: asyncpg.Connection = await asyncpg.connect(dsn=dsn, ssl=ssl_ctx, server_settings={'jit': 'off'})
    try:
        statements = load_sql_statements(SQL_PATH)
        applied = 0
        skipped = 0
        for stmt in statements:
            try:
                await conn.execute(stmt)
                applied += 1
            except Exception as e:  # noqa: BLE001
                msg = str(e).lower()
                # 忽略已存在错误
                if 'already exists' in msg or 'exists' in msg:
                    skipped += 1
                    continue
                raise
        print(f"✅ 远端对齐完成：执行 {applied} 条语句，忽略 {skipped} 条已存在对象。")
    finally:
        await conn.close()


def main() -> None:
    asyncio.run(apply_schema())


if __name__ == '__main__':
    main()


