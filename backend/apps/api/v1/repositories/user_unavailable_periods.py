"""
用户不可用时间段系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_unavailable_periods import UserUnavailablePeriodCreate, UserUnavailablePeriodUpdate
from libs.database.adapters import DatabaseAdapter
from datetime import date


async def get_unavailable_period_by_id(db: DatabaseAdapter, period_id: int) -> Optional[Dict]:
    """根据ID获取不可用时间段"""
    query = """
        SELECT uup.*, u.username, u.avatar_url
        FROM user_unavailable_periods uup
        JOIN users u ON uup.user_id = u.id
        WHERE uup.id = $1
    """
    return await db.fetch_one(query, period_id)


async def get_user_unavailable_periods(db: DatabaseAdapter, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户不可用时间段"""
    where_clause = "WHERE uup.user_id = $1"
    params = [user_id]

    if start_date:
        params.append(start_date)
        where_clause += f" AND uup.end_date >= ${len(params)}"

    if end_date:
        params.append(end_date)
        where_clause += f" AND uup.start_date <= ${len(params)}"

    query = f"""
        SELECT uup.*, u.username, u.avatar_url
        FROM user_unavailable_periods uup
        JOIN users u ON uup.user_id = u.id
        {where_clause}
        ORDER BY uup.start_date, uup.start_time
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_unavailable_period(db: DatabaseAdapter, period: UserUnavailablePeriodCreate) -> Optional[Dict]:
    """创建不可用时间段"""
    query = """
        INSERT INTO user_unavailable_periods (
            user_id, start_date, end_date, start_time, end_time,
            reason, description, affects_mentoring, affects_learning, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
        RETURNING *
    """
    values = (
        period.user_id, period.start_date, period.end_date, period.start_time,
        period.end_time, period.reason, period.description,
        period.affects_mentoring, period.affects_learning
    )
    return await db.fetch_one(query, *values)


async def update_unavailable_period(db: DatabaseAdapter, period_id: int, period: UserUnavailablePeriodUpdate) -> Optional[Dict]:
    """更新不可用时间段"""
    update_data = period.model_dump(exclude_unset=True)
    if not update_data:
        return await get_unavailable_period_by_id(db, period_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_unavailable_periods SET {set_clause}
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, period_id, *update_data.values())


async def delete_unavailable_period(db: DatabaseAdapter, period_id: int) -> bool:
    """删除不可用时间段"""
    query = "DELETE FROM user_unavailable_periods WHERE id = $1"
    result = await db.execute(query, period_id)
    return result == "DELETE 1"


async def bulk_create_unavailable_periods(db: DatabaseAdapter, periods: List[UserUnavailablePeriodCreate]) -> List[Dict]:
    """批量创建不可用时间段"""
    if not periods:
        return []

    # 使用批量插入
    values_list = []
    for period in periods:
        values_list.extend([
            period.user_id, period.start_date, period.end_date, period.start_time,
            period.end_time, period.reason, period.description,
            period.affects_mentoring, period.affects_learning
        ])

    # 构建批量插入的占位符
    placeholders = []
    param_index = 1
    for i in range(len(periods)):
        offset = i * 9
        placeholders.append(f"(${param_index + offset}, ${param_index + offset + 1}, ${param_index + offset + 2}, ${param_index + offset + 3}, ${param_index + offset + 4}, ${param_index + offset + 5}, ${param_index + offset + 6}, ${param_index + offset + 7}, ${param_index + offset + 8}, NOW())")

    query = f"""
        INSERT INTO user_unavailable_periods (
            user_id, start_date, end_date, start_time, end_time,
            reason, description, affects_mentoring, affects_learning, created_at
        )
        VALUES {', '.join(placeholders)}
        RETURNING *
    """
    return await db.fetch_all(query, *values_list)


async def get_conflicting_periods(db: DatabaseAdapter, user_id: int, start_date: date, end_date: date, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict]:
    """获取冲突的不可用时间段"""
    where_clause = "WHERE user_id = $1 AND ((start_date <= $2 AND end_date >= $2) OR (start_date <= $3 AND end_date >= $3) OR (start_date >= $2 AND end_date <= $3))"
    params = [user_id, end_date, start_date]

    # 如果提供了具体时间，进一步检查时间冲突
    if start_time and end_time:
        params.extend([start_time, end_time])
        where_clause += f""" AND (
            (start_time IS NULL AND end_time IS NULL) OR
            (start_time <= ${len(params) - 1} AND end_time >= ${len(params) - 1}) OR
            (start_time <= ${len(params)} AND end_time >= ${len(params)}) OR
            (start_time >= ${len(params) - 1} AND end_time <= ${len(params)})
        )"""

    query = f"SELECT * FROM user_unavailable_periods {where_clause} ORDER BY start_date, start_time"
    return await db.fetch_all(query, *params)


async def check_availability(db: DatabaseAdapter, user_id: int, check_date: date, start_time: Optional[str] = None, end_time: Optional[str] = None) -> bool:
    """检查用户在指定时间是否可用"""
    conflicting_periods = await get_conflicting_periods(db, user_id, check_date, check_date, start_time, end_time)
    return len(conflicting_periods) == 0


async def get_upcoming_unavailable_periods(db: DatabaseAdapter, user_id: int, days_ahead: int = 30) -> List[Dict]:
    """获取即将到来的不可用时间段"""
    query = """
        SELECT *, u.username, u.avatar_url
        FROM user_unavailable_periods uup
        JOIN users u ON uup.user_id = u.id
        WHERE uup.user_id = $1
        AND uup.start_date >= CURRENT_DATE
        AND uup.start_date <= CURRENT_DATE + INTERVAL '%s days'
        ORDER BY uup.start_date, uup.start_time
    """ % days_ahead
    return await db.fetch_all(query, user_id)


async def cleanup_expired_periods(db: DatabaseAdapter) -> int:
    """清理过期的不可用时间段"""
    query = "DELETE FROM user_unavailable_periods WHERE end_date < CURRENT_DATE"
    result = await db.execute(query)
    # 从结果字符串中提取删除的行数
    if result and "DELETE" in result:
        return int(result.split()[-1])
    return 0


async def get_unavailable_periods_stats(db: DatabaseAdapter, user_id: Optional[int] = None) -> Dict[str, Any]:
    """获取不可用时间段统计"""
    if user_id:
        query = """
            SELECT
                COUNT(*) as total_periods,
                COUNT(CASE WHEN start_date >= CURRENT_DATE THEN 1 END) as upcoming_periods,
                COUNT(CASE WHEN end_date < CURRENT_DATE THEN 1 END) as expired_periods,
                COUNT(CASE WHEN affects_mentoring = true THEN 1 END) as mentoring_affected,
                COUNT(CASE WHEN affects_learning = true THEN 1 END) as learning_affected,
                MAX(end_date) as latest_end_date
            FROM user_unavailable_periods
            WHERE user_id = $1
        """
        result = await db.fetch_one(query, user_id)
    else:
        query = """
            SELECT
                COUNT(*) as total_periods,
                COUNT(DISTINCT user_id) as users_with_periods,
                AVG(EXTRACT(EPOCH FROM (end_date - start_date))/86400) as avg_period_days,
                COUNT(CASE WHEN affects_mentoring = true THEN 1 END) as mentoring_affected_total,
                COUNT(CASE WHEN affects_learning = true THEN 1 END) as learning_affected_total
            FROM user_unavailable_periods
        """
        result = await db.fetch_one(query)

    return result or {}
