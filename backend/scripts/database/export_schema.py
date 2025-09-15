#!/usr/bin/env python3
"""
导出 Supabase(PostgreSQL) 的数据库结构为 JSON 快照。

生成内容包含：
- 表列表（public schema）
- 每个表的字段（名称、类型、是否可空、默认值）
- 主键、唯一约束、外键约束

输出位置：supabase/schema_snapshot.json

使用方法：
  poetry run python scripts/database/export_schema.py
"""
import asyncio
import json
import os
from typing import Any, Dict, List

import asyncpg
import ssl as _ssl

# 允许从项目根目录导入配置
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from libs.config.settings import settings  # noqa: E402


async def fetch_tables(connection: asyncpg.Connection) -> List[str]:
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """
    rows = await connection.fetch(query)
    return [r[0] for r in rows]


async def fetch_columns(connection: asyncpg.Connection, table_name: str) -> List[Dict[str, Any]]:
    query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            udt_name,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = $1
        ORDER BY ordinal_position
    """
    rows = await connection.fetch(query, table_name)
    columns: List[Dict[str, Any]] = []
    for r in rows:
        columns.append({
            "name": r[0],
            "data_type": r[1],
            "is_nullable": (r[2] == 'YES'),
            "default": r[3],
            "udt_name": r[4],
            "char_max_len": r[5],
            "num_precision": r[6],
            "num_scale": r[7],
        })
    return columns


async def fetch_primary_key(connection: asyncpg.Connection, table_name: str) -> List[str]:
    query = """
        SELECT a.attname
        FROM   pg_index i
        JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE  i.indrelid = 'public.""" + table_name + """'::regclass
        AND    i.indisprimary;
    """
    rows = await connection.fetch(query)
    return [r[0] for r in rows]


async def fetch_unique_constraints(connection: asyncpg.Connection, table_name: str) -> List[List[str]]:
    query = """
        SELECT ARRAY(
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = 'public.""" + table_name + """'::regclass
            AND    i.indisunique AND NOT i.indisprimary
        ) AS cols
    """
    rows = await connection.fetch(query)
    constraints: List[List[str]] = []
    for r in rows:
        cols = list(r[0]) if r[0] is not None else []
        if cols:
            constraints.append(cols)
    return constraints


async def fetch_foreign_keys(connection: asyncpg.Connection, table_name: str) -> List[Dict[str, Any]]:
    query = """
        SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
             AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = 'public' 
          AND tc.table_name = $1 AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.constraint_name, kcu.ordinal_position
    """
    rows = await connection.fetch(query, table_name)
    fks: List[Dict[str, Any]] = []
    for r in rows:
        fks.append({
            "constraint": r[0],
            "column": r[1],
            "ref_table": r[2],
            "ref_column": r[3],
        })
    return fks


async def export_schema() -> Dict[str, Any]:
    dsn = settings.postgres_url
    # 为兼容某些环境的自签名证书，放宽 SSL 校验（仅用于读取元数据）
    ssl_ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = _ssl.CERT_NONE

    conn: asyncpg.Connection = await asyncpg.connect(
        dsn=dsn,
        server_settings={'jit': 'off'},
        ssl=ssl_ctx,
    )
    try:
        tables = await fetch_tables(conn)
        result: Dict[str, Any] = {
            "database": "supabase",
            "schema": "public",
            "tables": {},
        }
        for table in tables:
            columns = await fetch_columns(conn, table)
            pkey = await fetch_primary_key(conn, table)
            uniques = await fetch_unique_constraints(conn, table)
            fkeys = await fetch_foreign_keys(conn, table)
            result["tables"][table] = {
                "columns": columns,
                "primary_key": pkey,
                "unique_constraints": uniques,
                "foreign_keys": fkeys,
            }
        return result
    finally:
        await conn.close()


def ensure_output_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def main() -> None:
    output_path = os.path.join(PROJECT_ROOT, 'supabase', 'schema_snapshot.json')
    ensure_output_dir(output_path)
    data = asyncio.run(export_schema())
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 导出完成: {output_path}")


if __name__ == "__main__":
    main()


