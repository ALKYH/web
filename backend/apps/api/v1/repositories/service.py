"""
服务相关的数据访问操作
"""
from typing import Optional, List, Dict
from datetime import datetime

from apps.schemas.service import ServiceCreate, ServiceUpdate
from libs.database.adapters import DatabaseAdapter

TABLE_NAME = "services"

async def get_by_id(db: DatabaseAdapter, service_id: int) -> Optional[Dict]:
    """根据ID获取服务"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    return await db.fetch_one(query, service_id)

async def get_by_navigator_id(db: DatabaseAdapter, navigator_id: int) -> List[Dict]:
    """根据导师ID获取所有服务"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE navigator_id = $1 ORDER BY created_at DESC"
    return await db.fetch_many(query, navigator_id)

async def create(db: DatabaseAdapter, navigator_id: int, service_in: ServiceCreate) -> Optional[Dict]:
    """为指定导师创建服务"""
    
    # 构建插入数据
    create_data = service_in.model_dump()
    create_data["navigator_id"] = navigator_id
    create_data["status"] = "active"
    
    # 动态构建插入语句
    columns = ", ".join(create_data.keys())
    placeholders = ", ".join([f"${i+1}" for i in range(len(create_data))])
    
    query = f"""
        INSERT INTO {TABLE_NAME} ({columns})
        VALUES ({placeholders})
        RETURNING *
    """
    
    return await db.fetch_one(query, *create_data.values())

async def update(db: DatabaseAdapter, service_id: int, service_in: ServiceUpdate) -> Optional[Dict]:
    """更新指定服务"""
    update_data = service_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_by_id(db, service_id)
        
    update_data["updated_at"] = datetime.now()

    # 动态构建更新语句
    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    
    query = f"""
        UPDATE {TABLE_NAME}
        SET {set_clause}
        WHERE id = $1
        RETURNING *
    """
    
    return await db.fetch_one(query, service_id, *update_data.values())

async def delete(db: DatabaseAdapter, service_id: int) -> bool:
    """删除指定服务"""
    query = f"DELETE FROM {TABLE_NAME} WHERE id = $1"
    result = await db.execute(query, service_id)
    return "DELETE 1" in result

async def search(
    db: DatabaseAdapter,
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """搜索服务列表"""
    # 基础查询
    query = f"SELECT * FROM {TABLE_NAME} WHERE status = 'active'"
    params = []

    # 分类筛选
    if category:
        query += f" AND category = ${len(params) + 1}"
        params.append(category)

    # 文本搜索
    if search_query:
        query += f" AND (title ILIKE ${len(params) + 1} OR description ILIKE ${len(params) + 1})"
        params.append(f"%{search_query}%")

    # 分页和排序
    query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])

    return await db.fetch_many(query, *params)