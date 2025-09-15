"""
技能系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.skills import SkillCategoryCreate, SkillCategoryUpdate, SkillCreate, SkillUpdate
from libs.database.adapters import DatabaseAdapter


# 技能分类相关操作

async def get_skill_category_by_id(db: DatabaseAdapter, category_id: int) -> Optional[Dict]:
    """根据ID获取技能分类"""
    query = "SELECT * FROM skill_categories WHERE id = $1"
    return await db.fetch_one(query, category_id)


async def get_skill_categories(db: DatabaseAdapter, is_active: Optional[bool] = True, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取技能分类列表"""
    where_clause = "WHERE 1=1"
    params = []

    if is_active is not None:
        where_clause += " AND is_active = $1"
        params.append(is_active)

    query = f"""
        SELECT * FROM skill_categories
        {where_clause}
        ORDER BY sort_order, name
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_skill_category(db: DatabaseAdapter, category: SkillCategoryCreate) -> Optional[Dict]:
    """创建技能分类"""
    query = """
        INSERT INTO skill_categories (
            name, name_en, description, icon_url, sort_order, is_active, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        RETURNING *
    """
    values = (
        category.name, category.name_en, category.description,
        category.icon_url, category.sort_order, category.is_active
    )
    return await db.fetch_one(query, *values)


async def update_skill_category(db: DatabaseAdapter, category_id: int, category: SkillCategoryUpdate) -> Optional[Dict]:
    """更新技能分类"""
    update_data = category.model_dump(exclude_unset=True)
    if not update_data:
        return await get_skill_category_by_id(db, category_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE skill_categories SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, category_id, *update_data.values())


async def delete_skill_category(db: DatabaseAdapter, category_id: int) -> bool:
    """删除技能分类"""
    query = "DELETE FROM skill_categories WHERE id = $1"
    result = await db.execute(query, category_id)
    return result == "DELETE 1"


# 技能相关操作

async def get_skill_by_id(db: DatabaseAdapter, skill_id: int) -> Optional[Dict]:
    """根据ID获取技能"""
    query = """
        SELECT s.*, sc.name as category_name, sc.name_en as category_name_en
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        WHERE s.id = $1
    """
    return await db.fetch_one(query, skill_id)


async def get_skills_by_category(db: DatabaseAdapter, category_id: int, is_active: Optional[bool] = True, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取分类下的技能列表"""
    where_clause = "WHERE category_id = $1"
    params = [category_id]

    if is_active is not None:
        where_clause += " AND s.is_active = $2"
        params.append(is_active)

    query = f"""
        SELECT s.*, sc.name as category_name, sc.name_en as category_name_en
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        {where_clause}
        ORDER BY s.sort_order, s.name
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def get_all_skills(db: DatabaseAdapter, is_active: Optional[bool] = True, skip: int = 0, limit: int = 100) -> List[Dict]:
    """获取所有技能"""
    where_clause = "WHERE 1=1"
    params = []

    if is_active is not None:
        where_clause += " AND s.is_active = $1"
        params.append(is_active)

    query = f"""
        SELECT s.*, sc.name as category_name, sc.name_en as category_name_en,
               COUNT(us.id) as mentor_count
        FROM skills s
        LEFT JOIN skill_categories sc ON s.category_id = sc.id
        LEFT JOIN user_skills us ON s.id = us.skill_id AND us.can_mentor = true AND us.is_active = true
        {where_clause}
        GROUP BY s.id, sc.name, sc.name_en
        ORDER BY s.sort_order, s.name
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_skill(db: DatabaseAdapter, skill: SkillCreate) -> Optional[Dict]:
    """创建技能"""
    query = """
        INSERT INTO skills (
            category_id, name, name_en, description, difficulty_level,
            sort_order, is_active, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        RETURNING *
    """
    values = (
        skill.category_id, skill.name, skill.name_en, skill.description,
        skill.difficulty_level, skill.sort_order, skill.is_active
    )
    return await db.fetch_one(query, *values)


async def update_skill(db: DatabaseAdapter, skill_id: int, skill: SkillUpdate) -> Optional[Dict]:
    """更新技能"""
    update_data = skill.model_dump(exclude_unset=True)
    if not update_data:
        return await get_skill_by_id(db, skill_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE skills SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, skill_id, *update_data.values())


async def delete_skill(db: DatabaseAdapter, skill_id: int) -> bool:
    """删除技能"""
    query = "DELETE FROM skills WHERE id = $1"
    result = await db.execute(query, skill_id)
    return result == "DELETE 1"


async def search_skills(db: DatabaseAdapter, query_str: str, limit: int = 20) -> List[Dict]:
    """搜索技能"""
    search_query = f"%{query_str}%"
    query = """
        SELECT s.*, sc.name as category_name, sc.name_en as category_name_en,
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
    return await db.fetch_all(query, search_query, limit)
