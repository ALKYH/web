"""
服务仓库层
提供服务相关的数据访问操作
统一管理所有服务相关的数据访问操作
"""
from typing import Optional, List
from datetime import datetime

from apps.schemas.service import Service, ServiceCreate, ServiceUpdate
from libs.database.adapters import DatabaseAdapter


# ============ 服务管理 ============

async def get_by_id(db: DatabaseAdapter, service_id: int) -> Optional[Service]:
    """根据ID获取服务"""
    query = """
        SELECT id, mentor_id, skill_id, title, description, price,
               duration_hours, is_active, created_at, updated_at
        FROM services
        WHERE id = $1
    """
    row = await db.fetch_one(query, service_id)
    return Service(**row) if row else None


async def get_by_mentor_id(db: DatabaseAdapter, mentor_id: int) -> List[Service]:
    """根据导师ID获取所有服务"""
    query = """
        SELECT id, mentor_id, skill_id, title, description, price,
               duration_hours, is_active, created_at, updated_at
        FROM services
        WHERE mentor_id = $1 AND is_active = true
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, mentor_id)
    return [Service(**row) for row in rows]

async def create(db: DatabaseAdapter, mentor_id: int, service_in: ServiceCreate) -> Optional[Service]:
    """为指定导师创建服务"""
    query = """
        INSERT INTO services (
            mentor_id, skill_id, title, description, price,
            duration_hours, is_active, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        RETURNING id, mentor_id, skill_id, title, description, price,
                  duration_hours, is_active, created_at, updated_at
    """

    values = (
        mentor_id, service_in.skill_id, service_in.title, service_in.description,
        service_in.price, service_in.duration_hours, service_in.is_active
    )

    row = await db.fetch_one(query, *values)
    return Service(**row) if row else None


async def update(db: DatabaseAdapter, service_id: int, service_in: ServiceUpdate) -> Optional[Service]:
    """更新指定服务"""
    update_data = service_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_by_id(db, service_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE services
        SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING id, mentor_id, skill_id, title, description, price,
                  duration_hours, is_active, created_at, updated_at
    """

    row = await db.fetch_one(query, service_id, *update_data.values())
    return Service(**row) if row else None


async def delete(db: DatabaseAdapter, service_id: int) -> bool:
    """删除指定服务"""
    query = "DELETE FROM services WHERE id = $1"
    result = await db.execute(query, service_id)
    return "DELETE 1" in result


async def search(
    db: DatabaseAdapter,
    mentor_id: Optional[int] = None,
    skill_id: Optional[int] = None,
    search_query: Optional[str] = None,
    is_active: bool = True,
    limit: int = 20,
    offset: int = 0
) -> List[Service]:
    """搜索服务列表"""
    where_clauses = ["is_active = $1"]
    params = [is_active]

    if mentor_id:
        params.append(mentor_id)
        where_clauses.append(f"mentor_id = ${len(params)}")

    if skill_id:
        params.append(skill_id)
        where_clauses.append(f"skill_id = ${len(params)}")

    if search_query:
        params.append(f"%{search_query}%")
        where_clauses.append(f"(title ILIKE ${len(params)} OR description ILIKE ${len(params)})")

    where_clause = " AND ".join(where_clauses)
    params.extend([limit, offset])

    query = f"""
        SELECT id, mentor_id, skill_id, title, description, price,
               duration_hours, is_active, created_at, updated_at
        FROM services
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${len(params) - 1} OFFSET ${len(params)}
    """

    rows = await db.fetch_all(query, *params[:-2], limit, offset)
    return [Service(**row) for row in rows]