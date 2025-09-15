"""
用户可用性系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_availability import UserAvailabilityCreate, UserAvailabilityUpdate
from libs.database.adapters import DatabaseAdapter
from datetime import date


async def get_user_availability(db: DatabaseAdapter, user_id: int, day_of_week: Optional[int] = None) -> List[Dict]:
    """获取用户的可用性设置"""
    where_clause = "WHERE ua.user_id = $1"
    params = [user_id]

    if day_of_week is not None:
        where_clause += " AND ua.day_of_week = $2"
        params.append(day_of_week)

    query = f"""
        SELECT ua.*, u.username, u.avatar_url
        FROM user_availability ua
        JOIN users u ON ua.user_id = u.id
        {where_clause}
        AND ua.is_active = true
        ORDER BY ua.day_of_week, ua.start_time
    """
    return await db.fetch_all(query, *params)


async def get_availability_by_id(db: DatabaseAdapter, availability_id: int) -> Optional[Dict]:
    """根据ID获取可用性设置"""
    query = """
        SELECT ua.*, u.username, u.avatar_url
        FROM user_availability ua
        JOIN users u ON ua.user_id = u.id
        WHERE ua.id = $1
    """
    return await db.fetch_one(query, availability_id)


async def create_availability(db: DatabaseAdapter, availability: UserAvailabilityCreate) -> Optional[Dict]:
    """创建用户可用性"""
    query = """
        INSERT INTO user_availability (
            user_id, day_of_week, start_time, end_time, timezone,
            availability_type, is_active, notes, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
        RETURNING *
    """
    values = (
        availability.user_id, availability.day_of_week, availability.start_time,
        availability.end_time, availability.timezone, availability.availability_type,
        availability.is_active, availability.notes
    )
    return await db.fetch_one(query, *values)


async def update_availability(db: DatabaseAdapter, availability_id: int, availability: UserAvailabilityUpdate) -> Optional[Dict]:
    """更新用户可用性"""
    update_data = availability.model_dump(exclude_unset=True)
    if not update_data:
        return await get_availability_by_id(db, availability_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_availability SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, availability_id, *update_data.values())


async def delete_availability(db: DatabaseAdapter, availability_id: int) -> bool:
    """删除用户可用性设置"""
    query = "DELETE FROM user_availability WHERE id = $1"
    result = await db.execute(query, availability_id)
    return result == "DELETE 1"


async def bulk_create_availability(db: DatabaseAdapter, availabilities: List[UserAvailabilityCreate]) -> List[Dict]:
    """批量创建用户可用性"""
    if not availabilities:
        return []

    # 使用批量插入
    values_list = []
    for availability in availabilities:
        values_list.extend([
            availability.user_id, availability.day_of_week, availability.start_time,
            availability.end_time, availability.timezone, availability.availability_type,
            availability.is_active, availability.notes
        ])

    # 构建批量插入的占位符
    placeholders = []
    param_index = 1
    for i in range(len(availabilities)):
        offset = i * 8
        placeholders.append(f"(${param_index + offset}, ${param_index + offset + 1}, ${param_index + offset + 2}, ${param_index + offset + 3}, ${param_index + offset + 4}, ${param_index + offset + 5}, ${param_index + offset + 6}, ${param_index + offset + 7}, NOW(), NOW())")

    query = f"""
        INSERT INTO user_availability (
            user_id, day_of_week, start_time, end_time, timezone,
            availability_type, is_active, notes, created_at, updated_at
        )
        VALUES {', '.join(placeholders)}
        RETURNING *
    """
    return await db.fetch_all(query, *values_list)


async def bulk_update_availability(db: DatabaseAdapter, user_id: int, availabilities: List[Dict]) -> bool:
    """批量更新用户的可用性"""
    if not availabilities:
        return True

    # 先删除用户的现有可用性
    await db.execute("DELETE FROM user_availability WHERE user_id = $1", user_id)

    # 重新插入
    create_data = [UserAvailabilityCreate(**avail) for avail in availabilities]
    result = await bulk_create_availability(db, create_data)
    return len(result) == len(availabilities)


async def get_available_users(db: DatabaseAdapter, day_of_week: int, start_time: str, end_time: str, timezone: str = "Asia/Shanghai") -> List[Dict]:
    """获取指定时间段内可用的用户"""
    query = """
        SELECT DISTINCT ua.*, u.username, u.avatar_url, u.role
        FROM user_availability ua
        JOIN users u ON ua.user_id = u.id
        WHERE ua.day_of_week = $1
        AND ua.start_time <= $2::time
        AND ua.end_time >= $3::time
        AND ua.timezone = $4
        AND ua.is_active = true
        AND u.is_active = true
        ORDER BY u.username
    """
    return await db.fetch_all(query, day_of_week, start_time, end_time, timezone)


async def get_unavailable_periods(db: DatabaseAdapter, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
    """获取用户不可用时间段"""
    where_clause = "WHERE user_id = $1"
    params = [user_id]

    if start_date:
        params.append(start_date)
        where_clause += f" AND end_date >= ${len(params)}"

    if end_date:
        params.append(end_date)
        where_clause += f" AND start_date <= ${len(params)}"

    query = f"""
        SELECT *
        FROM user_unavailable_periods
        {where_clause}
        ORDER BY start_date, start_time
    """
    return await db.fetch_all(query, *params)
