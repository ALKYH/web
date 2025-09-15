#!/usr/bin/env python3
"""
将 supabase/schema_snapshot.json 转换为可执行的 PostgreSQL DDL (schema.sql)。

输入:  supabase/schema_snapshot.json  (由 export_schema.py 生成)
输出:  supabase/schema.sql

注意:
- 这是基于信息架构的近似 DDL 生成，涵盖列、NOT NULL、DEFAULT、PRIMARY KEY、UNIQUE、FOREIGN KEY。
- 如需精确到索引/触发器/视图/序列，请后续改用 Supabase CLI 的 pg_dump 或手写迁移补充。
"""
import json
import os
from typing import Any, Dict, List

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAPSHOT_PATH = os.path.join(PROJECT_ROOT, 'supabase', 'schema_snapshot.json')
OUTPUT_SQL_PATH = os.path.join(PROJECT_ROOT, 'supabase', 'schema.sql')


def pg_ident(name: str) -> str:
    # 简单转义标识符（保留小写与下划线），如包含大写或特殊字符则加引号
    if name.isidentifier() and name.lower() == name and '__' not in name:
        return name
    return '"' + name.replace('"', '""') + '"'


def render_column(col: Dict[str, Any]) -> str:
    name = pg_ident(col['name'])
    data_type = col['data_type']
    # information_schema 的 data_type 有时较为通用；这里直接使用
    line = f"{name} {data_type}"
    if not col.get('is_nullable', True):
        line += " NOT NULL"
    default = col.get('default')
    if default is not None:
        line += f" DEFAULT {default}"
    return line


def render_primary_key(table: str, cols: List[str]) -> str:
    if not cols:
        return ''
    cols_sql = ', '.join(pg_ident(c) for c in cols)
    name = pg_ident(f"{table}_pkey")
    return f"CONSTRAINT {name} PRIMARY KEY ({cols_sql})"


def render_unique(table: str, cols_list: List[List[str]], idx: int) -> str:
    cols = cols_list[idx]
    if not cols:
        return ''
    cols_sql = ', '.join(pg_ident(c) for c in cols)
    name = pg_ident(f"{table}_uniq_{idx}")
    return f"CONSTRAINT {name} UNIQUE ({cols_sql})"


def render_foreign_key(table: str, fk: Dict[str, Any], idx: int) -> str:
    col = pg_ident(fk['column'])
    ref_table = pg_ident(fk['ref_table'])
    ref_col = pg_ident(fk['ref_column'])
    name = pg_ident(f"{table}_fk_{idx}_{fk['column']}")
    return f"CONSTRAINT {name} FOREIGN KEY ({col}) REFERENCES {ref_table} ({ref_col})"


def build_table_sql(table: str, meta: Dict[str, Any]) -> str:
    parts: List[str] = []
    # 列
    for col in meta.get('columns', []):
        parts.append(render_column(col))

    # 主键
    pk = render_primary_key(table, meta.get('primary_key', []))
    if pk:
        parts.append(pk)

    # 唯一约束
    uniques = meta.get('unique_constraints', []) or []
    for i in range(len(uniques)):
        uq = render_unique(table, uniques, i)
        if uq:
            parts.append(uq)

    # 外键
    fks = meta.get('foreign_keys', []) or []
    for i, fk in enumerate(fks):
        parts.append(render_foreign_key(table, fk, i))

    inner = ",\n    ".join(parts) if parts else ''
    tbl = pg_ident(table)
    return (
        f"CREATE TABLE IF NOT EXISTS {tbl} (\n"
        f"    {inner}\n"
        f");\n"
    )


def main() -> None:
    if not os.path.exists(SNAPSHOT_PATH):
        raise SystemExit(f"未找到快照文件: {SNAPSHOT_PATH}，请先运行 export_schema.py")

    with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)

    tables: Dict[str, Any] = snapshot.get('tables', {})
    out_lines: List[str] = [
        "-- 由 snapshot_to_sql.py 自动生成",
        "-- 来源: supabase/schema_snapshot.json",
        "SET client_min_messages TO WARNING;",
        "SET search_path TO public;",
        "",
    ]

    # 先按名称排序，稳定输出
    for table in sorted(tables.keys()):
        out_lines.append(build_table_sql(table, tables[table]))

    sql_text = "\n".join(out_lines) + "\n"
    os.makedirs(os.path.dirname(OUTPUT_SQL_PATH), exist_ok=True)
    with open(OUTPUT_SQL_PATH, 'w', encoding='utf-8') as f:
        f.write(sql_text)

    print(f"✅ 已生成: {OUTPUT_SQL_PATH}")


if __name__ == '__main__':
    main()


