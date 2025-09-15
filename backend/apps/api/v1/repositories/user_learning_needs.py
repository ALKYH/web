"""
用户学习需求系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_learning_needs import UserLearningNeedCreate, UserLearningNeedUpdate
from libs.database.adapters import DatabaseAdapter


async def get_learning_need_by_id(db: DatabaseAdapter, need_id: int) -> Optional[Dict]:
    """根据ID获取学习需求"""
    query = """
        SELECT uln.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name
        FROM user_learning_needs uln
        JOIN users u ON uln.user_id = u.id
        LEFT JOIN skills s ON uln.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE uln.id = $1
    """
    return await db.fetch_one(query, need_id)


async def get_user_learning_needs(db: DatabaseAdapter, user_id: int, is_active: Optional[bool] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户学习需求列表"""
    where_clause = "WHERE uln.user_id = $1"
    params = [user_id]

    if is_active is not None:
        where_clause += " AND uln.is_active = $2"
        params.append(is_active)

    query = f"""
        SELECT uln.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COUNT(mm.id) as matching_mentors_count
        FROM user_learning_needs uln
        JOIN users u ON uln.user_id = u.id
        LEFT JOIN skills s ON uln.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN mentor_matches mm ON uln.id = mm.learning_need_id AND mm.status IN ('suggested', 'contacted', 'accepted')
        {where_clause}
        GROUP BY uln.id, u.username, u.avatar_url, s.name, s.description, sc.name
        ORDER BY uln.urgency_level DESC, uln.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def get_learning_need_by_user_skill(db: DatabaseAdapter, user_id: int, skill_id: int) -> Optional[Dict]:
    """获取用户特定技能的学习需求"""
    query = """
        SELECT uln.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name
        FROM user_learning_needs uln
        JOIN users u ON uln.user_id = u.id
        LEFT JOIN skills s ON uln.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE uln.user_id = $1 AND uln.skill_id = $2
    """
    return await db.fetch_one(query, user_id, skill_id)


async def create_learning_need(db: DatabaseAdapter, need: UserLearningNeedCreate) -> Optional[Dict]:
    """创建学习需求"""
    # 检查是否已存在相同技能的需求
    existing = await get_learning_need_by_user_skill(db, need.user_id, need.skill_id)
    if existing:
        return None  # 或更新现有需求

    query = """
        INSERT INTO user_learning_needs (
            user_id, skill_id, urgency_level, budget_min, budget_max, currency,
            preferred_format, preferred_duration, description, learning_goals,
            current_level, target_level, is_active, created_at, updated_at, expires_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW(),
                NOW() + INTERVAL '3 months')
        RETURNING *
    """
    values = (
        need.user_id, need.skill_id, need.urgency_level, need.budget_min, need.budget_max,
        need.currency, need.preferred_format, need.preferred_duration, need.description,
        need.learning_goals, need.current_level, need.target_level, need.is_active
    )
    return await db.fetch_one(query, *values)


async def update_learning_need(db: DatabaseAdapter, need_id: int, need: UserLearningNeedUpdate) -> Optional[Dict]:
    """更新学习需求"""
    update_data = need.model_dump(exclude_unset=True)
    if not update_data:
        return await get_learning_need_by_id(db, need_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_learning_needs SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, need_id, *update_data.values())


async def delete_learning_need(db: DatabaseAdapter, need_id: int) -> bool:
    """删除学习需求"""
    query = "DELETE FROM user_learning_needs WHERE id = $1"
    result = await db.execute(query, need_id)
    return result == "DELETE 1"


async def expire_learning_needs(db: DatabaseAdapter) -> int:
    """过期学习需求处理"""
    query = """
        UPDATE user_learning_needs
        SET is_active = false, updated_at = NOW()
        WHERE expires_at <= NOW() AND is_active = true
    """
    result = await db.execute(query)
    # 从结果字符串中提取更新的行数
    if result and "UPDATE" in result:
        return int(result.split()[-1])
    return 0


async def get_matching_needs_for_mentor(db: DatabaseAdapter, mentor_id: int, mentor_skills: List[int], skip: int = 0, limit: int = 50) -> List[Dict]:
    """为导师获取匹配的学习需求"""
    if not mentor_skills:
        return []

    query = f"""
        SELECT DISTINCT uln.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name
        FROM user_learning_needs uln
        JOIN users u ON uln.user_id = u.id
        LEFT JOIN skills s ON uln.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE uln.skill_id = ANY($1)
        AND uln.is_active = true
        AND uln.expires_at > NOW()
        AND uln.user_id != $2
        AND NOT EXISTS (
            SELECT 1 FROM mentor_matches mm
            WHERE mm.learning_need_id = uln.id
            AND mm.mentor_id = $2
            AND mm.status IN ('accepted', 'completed')
        )
        ORDER BY uln.urgency_level DESC, uln.created_at DESC
        LIMIT $3 OFFSET $4
    """
    return await db.fetch_all(query, mentor_skills, mentor_id, limit, skip)


async def get_popular_learning_needs(db: DatabaseAdapter, limit: int = 20) -> List[Dict]:
    """获取热门学习需求"""
    query = """
        SELECT s.name as skill_name, s.id as skill_id,
               COUNT(uln.id) as demand_count,
               AVG(uln.urgency_level) as avg_urgency,
               AVG(uln.budget_max) as avg_budget_max,
               sc.name as category_name
        FROM user_learning_needs uln
        JOIN skills s ON uln.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE uln.is_active = true
        AND uln.expires_at > NOW()
        GROUP BY s.id, s.name, sc.name
        ORDER BY demand_count DESC, avg_urgency DESC
        LIMIT $1
    """
    return await db.fetch_all(query, limit)


async def search_learning_needs(db: DatabaseAdapter, skill_name: Optional[str] = None, category_id: Optional[int] = None, urgency_min: Optional[int] = None, budget_max: Optional[float] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """搜索学习需求"""
    where_clause = "WHERE uln.is_active = true AND uln.expires_at > NOW()"
    params = []

    if skill_name:
        params.append(f"%{skill_name}%")
        where_clause += f" AND s.name ILIKE ${len(params)}"

    if category_id:
        params.append(category_id)
        where_clause += f" AND s.category_id = ${len(params)}"

    if urgency_min:
        params.append(urgency_min)
        where_clause += f" AND uln.urgency_level >= ${len(params)}"

    if budget_max:
        params.append(budget_max)
        where_clause += f" AND (uln.budget_max <= ${len(params)} OR uln.budget_max IS NULL)"

    query = f"""
        SELECT uln.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COUNT(mm.id) as matching_mentors_count
        FROM user_learning_needs uln
        JOIN users u ON uln.user_id = u.id
        LEFT JOIN skills s ON uln.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN mentor_matches mm ON uln.id = mm.learning_need_id AND mm.status IN ('suggested', 'contacted', 'accepted')
        {where_clause}
        GROUP BY uln.id, u.username, u.avatar_url, s.name, s.description, sc.name
        ORDER BY uln.urgency_level DESC, uln.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def get_learning_needs_stats(db: DatabaseAdapter) -> Dict[str, Any]:
    """获取学习需求统计"""
    query = """
        SELECT
            COUNT(*) as total_needs,
            COUNT(CASE WHEN is_active = true AND expires_at > NOW() THEN 1 END) as active_needs,
            COUNT(CASE WHEN expires_at <= NOW() THEN 1 END) as expired_needs,
            AVG(urgency_level) as avg_urgency,
            AVG(budget_max) as avg_budget_max,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT skill_id) as unique_skills
        FROM user_learning_needs
    """
    result = await db.fetch_one(query)
    return result or {}
