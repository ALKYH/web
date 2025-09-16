"""
技能系统仓库层
提供技能分类、技能、用户技能和导师技能的数据库操作
统一管理所有技能相关的数据访问操作
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from apps.schemas.skill import (
    SkillCategory, SkillCategoryCreate, SkillCategoryUpdate,
    Skill, SkillCreate, SkillUpdate,
    UserSkill, UserSkillCreate, UserSkillUpdate,
    MentorSkill, MentorSkillCreate, MentorSkillUpdate,
    SkillEndorsement
)
from libs.database.adapters import DatabaseAdapter


# ============ 技能分类仓库操作 ============

async def get_skill_category_by_id(db: DatabaseAdapter, category_id: UUID) -> Optional[SkillCategory]:
    """根据ID获取技能分类"""
    query = """
        SELECT id, name, name_en, description, icon_url, sort_order, is_active, created_at, updated_at
        FROM skill_categories
        WHERE id = $1
    """
    row = await db.fetch_one(query, category_id)
    return SkillCategory(**row) if row else None


async def get_skill_categories(db: DatabaseAdapter, is_active: Optional[bool] = True, skip: int = 0, limit: int = 50) -> List[SkillCategory]:
    """获取技能分类列表"""
    where_clause = "WHERE 1=1"
    params = []

    if is_active is not None:
        where_clause += " AND is_active = $1"
        params.append(is_active)

    query = f"""
        SELECT id, name, name_en, description, icon_url, sort_order, is_active, created_at, updated_at
        FROM skill_categories
        {where_clause}
        ORDER BY sort_order, name
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    rows = await db.fetch_all(query, *params)
    return [SkillCategory(**row) for row in rows]


async def create_skill_category(db: DatabaseAdapter, category: SkillCategoryCreate) -> Optional[SkillCategory]:
    """创建技能分类"""
    query = """
        INSERT INTO skill_categories (
            name, name_en, description, icon_url, sort_order, is_active, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        RETURNING id, name, name_en, description, icon_url, sort_order, is_active, created_at, updated_at
    """
    values = (
        category.name, category.name_en, category.description,
        category.icon_url, category.sort_order, category.is_active
    )
    row = await db.fetch_one(query, *values)
    return SkillCategory(**row) if row else None


async def update_skill_category(db: DatabaseAdapter, category_id: UUID, category: SkillCategoryUpdate) -> Optional[SkillCategory]:
    """更新技能分类"""
    update_data = category.model_dump(exclude_unset=True)
    if not update_data:
        return await get_skill_category_by_id(db, category_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE skill_categories SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING id, name, name_en, description, icon_url, sort_order, is_active, created_at, updated_at
    """
    row = await db.fetch_one(query, category_id, *update_data.values())
    return SkillCategory(**row) if row else None


async def delete_skill_category(db: DatabaseAdapter, category_id: UUID) -> bool:
    """删除技能分类"""
    query = "DELETE FROM skill_categories WHERE id = $1"
    result = await db.execute(query, category_id)
    return result == "DELETE 1"


# ============ 技能仓库操作 ============

async def get_skill_by_id(db: DatabaseAdapter, skill_id: UUID) -> Optional[Skill]:
    """根据ID获取技能"""
    query = """
        SELECT s.id, s.category_id, s.name, s.name_en, s.description, s.difficulty_level,
               s.sort_order, s.is_active, s.created_at, s.updated_at,
               sc.name as category_name, sc.name_en as category_name_en
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE s.id = $1
    """
    row = await db.fetch_one(query, skill_id)
    return Skill(**row) if row else None


async def get_skills_by_category(db: DatabaseAdapter, category_id: UUID, is_active: Optional[bool] = True, skip: int = 0, limit: int = 50) -> List[Skill]:
    """获取分类下的技能列表"""
    where_clause = "WHERE s.category_id = $1"
    params = [category_id]

    if is_active is not None:
        where_clause += " AND s.is_active = $2"
        params.append(is_active)

    query = f"""
        SELECT s.id, s.category_id, s.name, s.name_en, s.description, s.difficulty_level,
               s.sort_order, s.is_active, s.created_at, s.updated_at,
               sc.name as category_name, sc.name_en as category_name_en
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        {where_clause}
        ORDER BY s.sort_order, s.name
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    rows = await db.fetch_all(query, *params)
    return [Skill(**row) for row in rows]


async def get_all_skills(db: DatabaseAdapter, is_active: Optional[bool] = True, skip: int = 0, limit: int = 100) -> List[Skill]:
    """获取所有技能"""
    where_clause = "WHERE 1=1"
    params = []

    # Note: skills table doesn't have is_active field, so we skip this filter

    query = f"""
        SELECT s.id, s.category_id, s.name, NULL as name_en, NULL as description,
               NULL as difficulty_level, NULL as sort_order, NULL as is_active,
               s.created_at, s.updated_at,
               sc.name as category_name, NULL as category_name_en,
               COUNT(ms.id) as mentor_count
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN user_skills us ON s.id = us.skill_id
        LEFT JOIN mentor_skills ms ON ms.user_skill_id = us.id AND ms.can_mentor = true
        {where_clause}
        GROUP BY s.id, sc.name
        ORDER BY s.name
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    rows = await db.fetch_all(query, *params)
    return [Skill(**row) for row in rows]


async def create_skill(db: DatabaseAdapter, skill: SkillCreate) -> Optional[Skill]:
    """创建技能"""
    query = """
        INSERT INTO skills (
            category_id, name, name_en, description, difficulty_level,
            sort_order, is_active, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        RETURNING id, category_id, name, name_en, description, difficulty_level,
                  sort_order, is_active, created_at, updated_at
    """
    values = (
        skill.category_id, skill.name, skill.name_en, skill.description,
        skill.difficulty_level, skill.sort_order, skill.is_active
    )
    row = await db.fetch_one(query, *values)
    return Skill(**row) if row else None


async def update_skill(db: DatabaseAdapter, skill_id: UUID, skill: SkillUpdate) -> Optional[Skill]:
    """更新技能"""
    update_data = skill.model_dump(exclude_unset=True)
    if not update_data:
        return await get_skill_by_id(db, skill_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE skills SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING id, category_id, name, name_en, description, difficulty_level,
                  sort_order, is_active, created_at, updated_at
    """
    row = await db.fetch_one(query, skill_id, *update_data.values())
    return Skill(**row) if row else None


async def delete_skill(db: DatabaseAdapter, skill_id: UUID) -> bool:
    """删除技能"""
    query = "DELETE FROM skills WHERE id = $1"
    result = await db.execute(query, skill_id)
    return result == "DELETE 1"


async def search_skills(db: DatabaseAdapter, query_str: str, limit: int = 20) -> List[Skill]:
    """搜索技能"""
    search_query = f"%{query_str}%"
    query = """
        SELECT s.id, s.category_id, s.name, s.name_en, s.description, s.difficulty_level,
               s.sort_order, s.is_active, s.created_at, s.updated_at,
               sc.name as category_name, sc.name_en as category_name_en,
               COUNT(us.id) as mentor_count
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN user_skills us ON s.id = us.skill_id AND us.can_mentor = true AND us.is_active = true
        WHERE (s.name ILIKE $1 OR s.name_en ILIKE $1 OR s.description ILIKE $1)
        AND s.is_active = true
        GROUP BY s.id, sc.name, sc.name_en
        ORDER BY s.name
        LIMIT $2
    """
    rows = await db.fetch_all(query, search_query, limit)
    return [Skill(**row) for row in rows]


# ============ 用户技能仓库操作 ============

async def get_user_skill_by_id(db: DatabaseAdapter, user_skill_id: UUID) -> Optional[UserSkill]:
    """根据ID获取用户技能"""
    query = """
        SELECT us.id, us.user_id, us.skill_id, us.proficiency_level, us.years_experience,
               us.can_mentor, us.hourly_rate, us.currency, us.description, us.verified,
               us.verified_by, us.verified_at, us.is_active, us.created_at, us.updated_at,
               u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COALESCE(usv.username, '') as verified_by_username
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN users usv ON us.verified_by = usv.id
        WHERE us.id = $1
    """
    row = await db.fetch_one(query, user_skill_id)
    return UserSkill(**row) if row else None


async def get_user_skills(db: DatabaseAdapter, user_id: UUID, can_mentor: Optional[bool] = None, is_active: Optional[bool] = None, verified: Optional[bool] = None, skip: int = 0, limit: int = 50) -> List[UserSkill]:
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
        SELECT us.id, us.user_id, us.skill_id, us.proficiency_level, us.years_experience,
               us.can_mentor, us.hourly_rate, us.currency, us.description, us.verified,
               us.verified_by, us.verified_at, us.is_active, us.created_at, us.updated_at,
               u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COALESCE(usv.username, '') as verified_by_username,
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
    rows = await db.fetch_all(query, *params)
    return [UserSkill(**row) for row in rows]


async def get_user_skill_by_skill_id(db: DatabaseAdapter, user_id: UUID, skill_id: UUID) -> Optional[UserSkill]:
    """获取用户特定技能"""
    query = """
        SELECT us.id, us.user_id, us.skill_id, us.proficiency_level, us.years_experience,
               us.can_mentor, us.hourly_rate, us.currency, us.description, us.verified,
               us.verified_by, us.verified_at, us.is_active, us.created_at, us.updated_at,
               u.username as user_username, u.avatar_url as user_avatar,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               COALESCE(usv.username, '') as verified_by_username
        FROM user_skills us
        JOIN users u ON us.user_id = u.id
        LEFT JOIN skills s ON us.skill_id = s.id
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN users usv ON us.verified_by = usv.id
        WHERE us.user_id = $1 AND us.skill_id = $2 AND us.is_active = true
    """
    row = await db.fetch_one(query, user_id, skill_id)
    return UserSkill(**row) if row else None


async def create_user_skill(db: DatabaseAdapter, user_skill: UserSkillCreate) -> Optional[UserSkill]:
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
        RETURNING id, user_id, skill_id, proficiency_level, years_experience,
                  can_mentor, hourly_rate, currency, description, verified,
                  verified_by, verified_at, is_active, created_at, updated_at
    """
    values = (
        user_skill.user_id, user_skill.skill_id, user_skill.proficiency_level,
        user_skill.years_experience, user_skill.can_mentor, user_skill.hourly_rate,
        user_skill.currency, user_skill.description, user_skill.verified,
        user_skill.verified_by, user_skill.verified_at, user_skill.is_active
    )
    row = await db.fetch_one(query, *values)
    return UserSkill(**row) if row else None


async def update_user_skill(db: DatabaseAdapter, user_skill_id: UUID, user_skill: UserSkillUpdate) -> Optional[UserSkill]:
    """更新用户技能"""
    update_data = user_skill.model_dump(exclude_unset=True)
    if not update_data:
        return await get_user_skill_by_id(db, user_skill_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_skills SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING id, user_id, skill_id, proficiency_level, years_experience,
                  can_mentor, hourly_rate, currency, description, verified,
                  verified_by, verified_at, is_active, created_at, updated_at
    """
    row = await db.fetch_one(query, user_skill_id, *update_data.values())
    return UserSkill(**row) if row else None


async def delete_user_skill(db: DatabaseAdapter, user_skill_id: UUID) -> bool:
    """删除用户技能"""
    query = "DELETE FROM user_skills WHERE id = $1"
    result = await db.execute(query, user_skill_id)
    return result == "DELETE 1"


async def verify_user_skill(db: DatabaseAdapter, user_skill_id: UUID, verified_by: UUID) -> Optional[UserSkill]:
    """验证用户技能"""
    query = """
        UPDATE user_skills
        SET verified = true, verified_by = $1, verified_at = NOW(), updated_at = NOW()
        WHERE id = $2
        RETURNING id, user_id, skill_id, proficiency_level, years_experience,
                  can_mentor, hourly_rate, currency, description, verified,
                  verified_by, verified_at, is_active, created_at, updated_at
    """
    row = await db.fetch_one(query, verified_by, user_skill_id)
    return UserSkill(**row) if row else None


async def get_skill_mentors(db: DatabaseAdapter, skill_id: UUID, min_proficiency: int = 3, verified_only: bool = False, skip: int = 0, limit: int = 50) -> List[UserSkill]:
    """获取技能的导师列表"""
    where_clause = "WHERE us.skill_id = $1 AND us.can_mentor = true AND us.is_active = true"
    params = [skill_id]

    if min_proficiency > 1:
        params.append(min_proficiency)
        where_clause += f" AND us.proficiency_level >= ${len(params)}"

    if verified_only:
        where_clause += " AND us.verified = true"

    query = f"""
        SELECT us.id, us.user_id, us.skill_id, us.proficiency_level, us.years_experience,
               us.can_mentor, us.hourly_rate, us.currency, us.description, us.verified,
               us.verified_by, us.verified_at, us.is_active, us.created_at, us.updated_at,
               u.username, u.avatar_url, u.role,
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
    rows = await db.fetch_all(query, *params)
    return [UserSkill(**row) for row in rows]


# ============ 导师技能仓库操作 ============

async def get_mentor_skills_by_user(db: DatabaseAdapter, user_id: UUID) -> List[MentorSkill]:
    """获取用户的导师技能列表"""
    query = """
        SELECT ms.id, ms.user_skill_id, ms.can_mentor, ms.hourly_rate, ms.description, ms.is_active, ms.created_at, ms.updated_at
        FROM mentor_skills ms
        JOIN user_skills us ON ms.user_skill_id = us.id
        WHERE us.user_id = $1
        ORDER BY ms.created_at DESC
    """
    rows = await db.fetch_all(query, user_id)
    return [MentorSkill(**row) for row in rows]


async def get_mentor_skill_by_id(db: DatabaseAdapter, mentor_skill_id: UUID, user_id: UUID) -> Optional[MentorSkill]:
    """获取导师技能"""
    query = """
        SELECT ms.id, ms.user_skill_id, ms.can_mentor, ms.hourly_rate, ms.description, ms.is_active, ms.created_at, ms.updated_at
        FROM mentor_skills ms
        JOIN user_skills us ON ms.user_skill_id = us.id
        WHERE ms.id = $1 AND us.user_id = $2
    """
    row = await db.fetch_one(query, mentor_skill_id, user_id)
    return MentorSkill(**row) if row else None


async def get_mentor_skill_by_user_skill_id(db: DatabaseAdapter, user_skill_id: UUID) -> Optional[MentorSkill]:
    """根据用户技能ID获取导师技能"""
    query = """
        SELECT id, user_skill_id, can_mentor, hourly_rate, description, is_active, created_at, updated_at
        FROM mentor_skills
        WHERE user_skill_id = $1
    """
    row = await db.fetch_one(query, user_skill_id)
    return MentorSkill(**row) if row else None


async def create_mentor_skill(db: DatabaseAdapter, user_id: UUID, mentor_skill_data: MentorSkillCreate) -> Optional[MentorSkill]:
    """创建导师技能"""
    query = """
        INSERT INTO mentor_skills (user_skill_id, can_mentor, hourly_rate, description, is_active)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, user_skill_id, can_mentor, hourly_rate, description, is_active, created_at, updated_at
    """
    values = (
        mentor_skill_data.user_skill_id,
        mentor_skill_data.can_mentor,
        mentor_skill_data.hourly_rate,
        mentor_skill_data.description,
        mentor_skill_data.is_active
    )
    row = await db.fetch_one(query, *values)
    return MentorSkill(**row) if row else None


async def update_mentor_skill(db: DatabaseAdapter, mentor_skill_id: UUID, user_id: UUID, mentor_skill_data: MentorSkillUpdate) -> Optional[MentorSkill]:
    """更新导师技能"""
    update_data = mentor_skill_data.model_dump(exclude_unset=True)
    if not update_data:
        return await get_mentor_skill_by_id(db, mentor_skill_id, user_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE mentor_skills
        SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        AND user_skill_id IN (SELECT id FROM user_skills WHERE user_id = ${len(update_data) + 2})
        RETURNING id, user_skill_id, can_mentor, hourly_rate, description, is_active, created_at, updated_at
    """
    values = list(update_data.values()) + [mentor_skill_id, user_id]
    row = await db.fetch_one(query, *values)
    return MentorSkill(**row) if row else None


async def delete_mentor_skill(db: DatabaseAdapter, mentor_skill_id: UUID, user_id: UUID) -> bool:
    """删除导师技能"""
    query = """
        DELETE FROM mentor_skills
        WHERE id = $1
        AND user_skill_id IN (SELECT id FROM user_skills WHERE user_id = $2)
    """
    result = await db.execute(query, mentor_skill_id, user_id)
    return result == "DELETE 1"


# ============ 技能认可仓库操作 ============

async def add_skill_endorsement(db: DatabaseAdapter, user_skill_id: UUID, endorser_id: UUID, rating: Optional[int] = None, comment: Optional[str] = None) -> Optional[SkillEndorsement]:
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
        RETURNING id, user_skill_id, endorser_id, rating, comment, created_at
    """
    row = await db.fetch_one(query, user_skill_id, endorser_id, rating, comment)
    if row:
        endorsement = SkillEndorsement(**row)
        # 更新用户技能的认可统计
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
        return endorsement
    return None


async def get_skill_endorsements(db: DatabaseAdapter, user_skill_id: UUID, skip: int = 0, limit: int = 50) -> List[SkillEndorsement]:
    """获取技能认可列表"""
    query = """
        SELECT use.id, use.user_skill_id, use.endorser_id, use.rating, use.comment, use.created_at,
               u.username as endorser_username, u.avatar_url as endorser_avatar
        FROM user_skill_endorsements use
        JOIN users u ON use.endorser_id = u.id
        WHERE use.user_skill_id = $1
        ORDER BY use.created_at DESC
        LIMIT $2 OFFSET $3
    """
    rows = await db.fetch_all(query, user_skill_id, limit, skip)
    return [SkillEndorsement(**row) for row in rows]


# ============ 高级查询操作 ============

async def get_popular_skills_by_users(db: DatabaseAdapter, limit: int = 20) -> List[Dict[str, Any]]:
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


async def search_user_skills(db: DatabaseAdapter, skill_name: Optional[str] = None, category_id: Optional[UUID] = None, min_proficiency: Optional[int] = None, can_mentor: Optional[bool] = None, verified_only: Optional[bool] = None, location: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[UserSkill]:
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
        SELECT us.id, us.user_id, us.skill_id, us.proficiency_level, us.years_experience,
               us.can_mentor, us.hourly_rate, us.currency, us.description, us.verified,
               us.verified_by, us.verified_at, us.is_active, us.created_at, us.updated_at,
               u.username, u.avatar_url, u.role,
               s.name as skill_name, s.description as skill_description,
               sc.name as category_name,
               p.location,
               COUNT(use2.id) as endorsement_count,
               COALESCE(usv.username, '') as verified_by_username
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
    rows = await db.fetch_all(query, *params)
    return [UserSkill(**row) for row in rows]


async def get_user_skill_stats(db: DatabaseAdapter, user_id: UUID) -> Dict[str, Any]:
    """获取用户技能统计"""
    query = """
        SELECT
            COUNT(*) as total_skills,
            COUNT(CASE WHEN can_mentor = true THEN 1 END) as mentoring_skills,
            COUNT(CASE WHEN verified = true THEN 1 END) as verified_skills,
            AVG(proficiency_level) as avg_proficiency,
            MAX(years_experience) as max_experience,
            AVG(hourly_rate) as avg_hourly_rate,
            SUM(endorsement_count) as total_endorsements
        FROM user_skills
        WHERE user_id = $1 AND is_active = true
    """
    result = await db.fetch_one(query, user_id)
    return result or {}
