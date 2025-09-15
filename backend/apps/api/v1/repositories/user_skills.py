"""
用户技能系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_skills import UserSkillCreate, UserSkillUpdate, SkillEndorsement
from libs.database.adapters import DatabaseAdapter


async def get_user_skill_by_id(db: DatabaseAdapter, user_skill_id: int) -> Optional[Dict]:
    """根据ID获取用户技能"""
    query = """
        SELECT us.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COALESCE(usv.verified_by_username, '') as verified_by_username
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN users usv ON us.verified_by = usv.id
        WHERE us.id = $1
    """
    return await db.fetch_one(query, user_skill_id)


async def get_user_skills(db: DatabaseAdapter, user_id: int, can_mentor: Optional[bool] = None, is_active: Optional[bool] = None, verified: Optional[bool] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的技能列表"""
    where_clause = "WHERE us.user_id = $1"
    params = [user_id]

    if can_mentor is not None:
        params.append(can_mentor)
        where_clause += f" AND us.can_mentor = ${len(params)}"

    if is_active is not None:
        params.append(is_active)
        where_clause += f" AND us.is_active = ${len(params)}"

    if verified is not None:
        params.append(verified)
        where_clause += f" AND us.verified = ${len(params)}"

    query = f"""
        SELECT us.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COALESCE(usv.verified_by_username, '') as verified_by_username,
               COUNT(use2.id) as endorsement_count
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN users usv ON us.verified_by = usv.id
        LEFT JOIN user_skill_endorsements use2 ON us.id = use2.user_skill_id
        {where_clause}
        GROUP BY us.id, u.username, u.avatar_url, s.name, s.description, sc.name, usv.username
        ORDER BY us.proficiency_level DESC, us.years_experience DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def get_user_skill_by_skill_id(db: DatabaseAdapter, user_id: int, skill_id: int) -> Optional[Dict]:
    """获取用户特定技能"""
    query = """
        SELECT us.*, u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COALESCE(usv.verified_by_username, '') as verified_by_username
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN users usv ON us.verified_by = usv.id
        WHERE us.user_id = $1 AND us.skill_id = $2 AND us.is_active = true
    """
    return await db.fetch_one(query, user_id, skill_id)


async def create_user_skill(db: DatabaseAdapter, user_skill: UserSkillCreate) -> Optional[Dict]:
    """创建用户技能"""
    # 检查是否已存在相同技能
    existing = await get_user_skill_by_skill_id(db, user_skill.user_id, user_skill.skill_id)
    if existing:
        return None  # 或更新现有技能

    query = """
        INSERT INTO user_skills (
            user_id, skill_id, proficiency_level, years_experience, can_mentor,
            hourly_rate, currency, description, verified, verified_by, verified_at, is_active,
            created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW(), NOW())
        RETURNING *
    """
    values = (
        user_skill.user_id, user_skill.skill_id, user_skill.proficiency_level,
        user_skill.years_experience, user_skill.can_mentor, user_skill.hourly_rate,
        user_skill.currency, user_skill.description, user_skill.verified,
        user_skill.verified_by, user_skill.verified_at, user_skill.is_active
    )
    return await db.fetch_one(query, *values)


async def update_user_skill(db: DatabaseAdapter, user_skill_id: int, user_skill: UserSkillUpdate) -> Optional[Dict]:
    """更新用户技能"""
    update_data = user_skill.model_dump(exclude_unset=True)
    if not update_data:
        return await get_user_skill_by_id(db, user_skill_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_skills SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, user_skill_id, *update_data.values())


async def delete_user_skill(db: DatabaseAdapter, user_skill_id: int) -> bool:
    """删除用户技能"""
    query = "DELETE FROM user_skills WHERE id = $1"
    result = await db.execute(query, user_skill_id)
    return result == "DELETE 1"


async def verify_user_skill(db: DatabaseAdapter, user_skill_id: int, verified_by: int) -> Optional[Dict]:
    """验证用户技能"""
    query = """
        UPDATE user_skills
        SET verified = true, verified_by = $1, verified_at = NOW(), updated_at = NOW()
        WHERE id = $2
        RETURNING *
    """
    return await db.fetch_one(query, verified_by, user_skill_id)


async def get_skill_mentors(db: DatabaseAdapter, skill_id: int, min_proficiency: int = 3, verified_only: bool = False, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取技能的导师列表"""
    where_clause = "WHERE us.skill_id = $1 AND us.can_mentor = true AND us.is_active = true"
    params = [skill_id]

    if min_proficiency > 1:
        params.append(min_proficiency)
        where_clause += f" AND us.proficiency_level >= ${len(params)}"

    if verified_only:
        where_clause += " AND us.verified = true"

    query = f"""
        SELECT us.*, u.username, u.avatar_url, u.role,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COUNT(use2.id) as endorsement_count,
               AVG(use2.rating) as avg_endorsement_rating
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN user_skill_endorsements use2 ON us.id = use2.user_skill_id
        {where_clause}
        GROUP BY us.id, u.username, u.avatar_url, u.role, s.name, s.description, sc.name
        ORDER BY us.proficiency_level DESC, us.years_experience DESC, endorsement_count DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def add_skill_endorsement(db: DatabaseAdapter, user_skill_id: int, endorser_id: int, rating: Optional[int] = None, comment: Optional[str] = None) -> Optional[Dict]:
    """添加技能认可"""
    # 检查是否已认可过
    existing_query = """
        SELECT id FROM user_skill_endorsements
        WHERE user_skill_id = $1 AND endorser_id = $2
    """
    existing = await db.fetch_one(existing_query, user_skill_id, endorser_id)
    if existing:
        return None  # 已认可过

    query = """
        INSERT INTO user_skill_endorsements (
            user_skill_id, endorser_id, rating, comment, created_at
        )
        VALUES ($1, $2, $3, $4, NOW())
        RETURNING *
    """
    result = await db.fetch_one(query, user_skill_id, endorser_id, rating, comment)

    # 更新用户技能的认可统计
    if result:
        await db.execute("""
            UPDATE user_skills
            SET endorsement_count = endorsement_count + 1,
                avg_endorsement_rating = (
                    SELECT AVG(rating) FROM user_skill_endorsements
                    WHERE user_skill_id = $1 AND rating IS NOT NULL
                ),
                updated_at = NOW()
            WHERE id = $1
        """, user_skill_id)

    return result


async def get_skill_endorsements(db: DatabaseAdapter, user_skill_id: int, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取技能认可列表"""
    query = """
        SELECT use.*, u.username as endorser_username, u.avatar_url as endorser_avatar
        FROM user_skill_endorsements use
        JOIN users u ON use.endorser_id = u.id
        WHERE use.user_skill_id = $1
        ORDER BY use.created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_all(query, user_skill_id, limit, skip)


async def get_popular_skills_by_users(db: DatabaseAdapter, limit: int = 20) -> List[Dict]:
    """获取用户中最受欢迎的技能"""
    query = """
        SELECT s.name as skill_name, s.id as skill_id,
               COUNT(us.id) as user_count,
               AVG(us.proficiency_level) as avg_proficiency,
               COUNT(CASE WHEN us.can_mentor = true THEN 1 END) as mentor_count,
               AVG(us.hourly_rate) as avg_hourly_rate,
               sc.name as category_name
        FROM user_skills us
        JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE us.is_active = true
        GROUP BY s.id, s.name, sc.name
        ORDER BY user_count DESC, mentor_count DESC
        LIMIT $1
    """
    return await db.fetch_all(query, limit)


async def search_user_skills(db: DatabaseAdapter, skill_name: Optional[str] = None, category_id: Optional[int] = None, min_proficiency: Optional[int] = None, can_mentor: Optional[bool] = None, verified_only: Optional[bool] = None, location: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """搜索用户技能"""
    where_clause = "WHERE us.is_active = true"
    params = []

    if skill_name:
        params.append(f"%{skill_name}%")
        where_clause += f" AND s.name ILIKE ${len(params)}"

    if category_id:
        params.append(category_id)
        where_clause += f" AND s.category_id = ${len(params)}"

    if min_proficiency:
        params.append(min_proficiency)
        where_clause += f" AND us.proficiency_level >= ${len(params)}"

    if can_mentor is not None:
        params.append(can_mentor)
        where_clause += f" AND us.can_mentor = ${len(params)}"

    if verified_only:
        where_clause += " AND us.verified = true"

    if location:
        params.append(f"%{location}%")
        where_clause += f" AND p.location ILIKE ${len(params)}"

    query = f"""
        SELECT us.*, u.username, u.avatar_url, u.role,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               p.location,
               COUNT(use2.id) as endorsement_count,
               COALESCE(usv.verified_by_username, '') as verified_by_username
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN profiles p ON u.id = p.user_id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN users usv ON us.verified_by = usv.id
        LEFT JOIN user_skill_endorsements use2 ON us.id = use2.user_skill_id
        {where_clause}
        GROUP BY us.id, u.username, u.avatar_url, u.role, s.name, s.description, sc.name, p.location, usv.username
        ORDER BY us.proficiency_level DESC, us.years_experience DESC, endorsement_count DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def get_user_skill_stats(db: DatabaseAdapter, user_id: int) -> Dict[str, Any]:
    """获取用户技能统计"""
    query = """
        SELECT
            COUNT(*) as total_skills,
            COUNT(CASE WHEN can_mentor = true THEN 1 END) as mentoring_skills,
            COUNT(CASE WHEN verified = true THEN 1 END) as verified_skills,
            AVG(proficiency_level) as avg_proficiency,
            MAX(years_experience) as max_experience,
            AVG(hourly_rate) as avg_hourly_rate,
            SUM(CASE WHEN can_mentor = true THEN 1 ELSE 0 END) as total_endorsements
        FROM user_skills
        WHERE user_id = $1 AND is_active = true
    """
    result = await db.fetch_one(query, user_id)
    return result or {}
