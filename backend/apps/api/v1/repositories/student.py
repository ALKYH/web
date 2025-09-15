"""
学生档案（学习需求）相关的CRUD操作
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from apps.schemas.student import StudentCreate, StudentUpdate
from libs.database.adapters import DatabaseAdapter

TABLE_NAME = "student_profiles"

async def get_profile_by_user_id(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """根据用户ID获取学生档案"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id = $1"
    return await db.fetch_one(query, user_id)

async def get_profile_by_id(db: DatabaseAdapter, profile_id: int) -> Optional[Dict]:
    """根据档案ID获取学生档案"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    return await db.fetch_one(query, profile_id)

async def create_profile(db: DatabaseAdapter, user_id: int, profile_in: StudentCreate) -> Optional[Dict]:
    """为指定用户创建学生档案"""
    
    # 构建插入数据
    create_data = profile_in.model_dump()
    create_data["user_id"] = user_id
    
    # 动态构建插入语句
    columns = ", ".join(create_data.keys())
    placeholders = ", ".join([f"${i+1}" for i in range(len(create_data))])
    
    query = f"""
        INSERT INTO {TABLE_NAME} ({columns})
        VALUES ({placeholders})
        RETURNING *
    """
    
    return await db.fetch_one(query, *create_data.values())

async def update_profile(db: DatabaseAdapter, user_id: int, profile_in: StudentUpdate) -> Optional[Dict]:
    """更新指定用户的学生档案"""
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
    """删除指定用户的学生档案"""
    query = f"DELETE FROM {TABLE_NAME} WHERE user_id = $1"
    result = await db.execute(query, user_id)
    return "DELETE 1" in result

async def search_profiles(
    db: DatabaseAdapter,
    search_query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """搜索学生档案列表（可扩展搜索条件）"""
    # 基础查询
    query = f"SELECT * FROM {TABLE_NAME} WHERE is_active = true"
    params = []

    # 简单的文本搜索示例（可扩展为更复杂的逻辑）
    if search_query:
        query += " AND (description ILIKE $1 OR learning_goals ILIKE $1)"
        params.append(f"%{search_query}%")

    # 分页和排序
    query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])

    return await db.fetch_many(query, *params)
