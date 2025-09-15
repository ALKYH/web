"""
会话相关的数据访问操作
"""
from typing import Optional, List, Dict
from datetime import datetime

from apps.schemas.session import SessionCreate, SessionUpdate
from libs.database.adapters import DatabaseAdapter

TABLE_NAME = "sessions"

async def get_by_id(db: DatabaseAdapter, session_id: int) -> Optional[Dict]:
    """根据ID获取会话"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    return await db.fetch_one(query, session_id)

async def get_by_user(db: DatabaseAdapter, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
    """获取用户的会话列表"""
    query = f"""
        SELECT * FROM {TABLE_NAME} 
        WHERE student_id = $1 OR mentor_id = $1
        ORDER BY created_at DESC 
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_many(query, user_id, limit, offset)

async def create(db: DatabaseAdapter, session_in: SessionCreate) -> Optional[Dict]:
    """创建新会话"""
    
    # 构建插入数据
    create_data = session_in.model_dump()
    create_data["status"] = "scheduled"
    
    # 动态构建插入语句
    columns = ", ".join(create_data.keys())
    placeholders = ", ".join([f"${i+1}" for i in range(len(create_data))])
    
    query = f"""
        INSERT INTO {TABLE_NAME} ({columns})
        VALUES ({placeholders})
        RETURNING *
    """
    
    return await db.fetch_one(query, *create_data.values())

async def update(db: DatabaseAdapter, session_id: int, session_in: SessionUpdate) -> Optional[Dict]:
    """更新会话"""
    update_data = session_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_by_id(db, session_id)
        
    update_data["updated_at"] = datetime.now()

    # 动态构建更新语句
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    
    query = f"""
        UPDATE {TABLE_NAME}
        SET {set_clause}
        WHERE id = $1
        RETURNING *
    """
    
    return await db.fetch_one(query, session_id, *update_data.values())

async def delete(db: DatabaseAdapter, session_id: int) -> bool:
    """删除会话"""
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    result = await db.execute(query, session_id)
    return "DELETE 1" in result