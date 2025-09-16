"""
导师档案相关的数据访问操作
"""
from typing import Optional, List, Dict
from datetime import datetime

from apps.schemas.mentor import MentorProfileCreate, MentorProfileUpdate
from libs.database.adapters import DatabaseAdapter

TABLE_NAME = "mentor_profiles"

async def get_profile_by_user_id(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """根据用户ID获取导师档案"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id = $1"
    return await db.fetch_one(query, user_id)

async def get_profile_by_id(db: DatabaseAdapter, profile_id: int) -> Optional[Dict]:
    """根据档案ID获取导师档案"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    return await db.fetch_one(query, profile_id)

async def create_profile(db: DatabaseAdapter, user_id: int, profile_in: MentorProfileCreate) -> Optional[Dict]:
    """为指定用户创建导师档案"""
    
    # 构建插入数据
    create_data = profile_in.model_dump()
    create_data["user_id"] = user_id
    create_data["status"] = "active"
    create_data["sessions_completed"] = 0
    create_data["total_hours_spent"] = 0.0
    
    # 动态构建插入语句
    columns = ", ".join(create_data.keys())
    placeholders = ", ".join([f"${i+1}" for i in range(len(create_data))])
    
    query = f"""
        INSERT INTO {TABLE_NAME} ({columns})
        VALUES ({placeholders})
        RETURNING *
    """
    
    return await db.fetch_one(query, *create_data.values())

async def update_profile(db: DatabaseAdapter, user_id: int, profile_in: MentorProfileUpdate) -> Optional[Dict]:
    """更新指定用户的导师档案"""
    update_data = profile_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_profile_by_user_id(db, user_id)
        
    update_data["updated_at"] = datetime.now()

    # 动态构建更新语句
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    
    query = f"""
        UPDATE {TABLE_NAME}
        SET {set_clause}
        WHERE user_id = $1
        RETURNING *
    """
    
    return await db.fetch_one(query, user_id, *update_data.values())

async def delete_profile(db: DatabaseAdapter, user_id: int) -> bool:
    """删除指定用户的导师档案"""
    query = f"DELETE FROM {TABLE_NAME} WHERE user_id = $1"
    result = await db.execute(query, user_id)
    return "DELETE 1" in result

async def search_profiles(
    db: DatabaseAdapter,
    search_query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """搜索导师档案列表"""
    # 基础查询
    query = f"SELECT * FROM {TABLE_NAME} WHERE status = 'active'"
    params = []

    # 简单的文本搜索
    if search_query:
        query += " AND (title ILIKE $1 OR description ILIKE $1)"
        params.append(f"%{search_query}%")

    # 分页和排序
    query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])

    return await db.fetch_many(query, *params)
