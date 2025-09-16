"""
消息相关的数据访问操作
"""
from typing import Optional, List, Dict
from datetime import datetime

from apps.schemas.message import MessageCreate, MessageUpdate
from libs.database.adapters import DatabaseAdapter

TABLE_NAME = "messages"

async def get_by_id(db: DatabaseAdapter, message_id: int) -> Optional[Dict]:
    """根据ID获取消息"""
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = $1"
    return await db.fetch_one(query, message_id)

async def get_by_conversation(
    db: DatabaseAdapter, 
    conversation_id: int, 
    limit: int = 50, 
    offset: int = 0
) -> List[Dict]:
    """获取对话中的消息列表"""
    query = f"""
        SELECT * FROM {TABLE_NAME} 
        WHERE conversation_id = $1 
        ORDER BY created_at DESC 
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_many(query, conversation_id, limit, offset)

async def create(db: DatabaseAdapter, message_in: MessageCreate) -> Optional[Dict]:
    """创建新消息"""
    
    # 构建插入数据
    create_data = message_in.model_dump()
    create_data["status"] = "sent"
    create_data["is_read"] = False
    
    # 动态构建插入语句
    columns = ", ".join(create_data.keys())
    placeholders = ", ".join([f"${i+1}" for i in range(len(create_data))])
    
    query = f"""
        INSERT INTO {TABLE_NAME} ({columns})
        VALUES ({placeholders})
        RETURNING *
    """
    
    return await db.fetch_one(query, *create_data.values())

async def mark_as_read(db: DatabaseAdapter, message_id: int, user_id: int) -> bool:
    """标记消息为已读"""
    query = f"""
        UPDATE {TABLE_NAME} 
        SET is_read = true, read_at = NOW() 
        WHERE id = $1 AND recipient_id = $2
    """
    result = await db.execute(query, message_id, user_id)
    return "UPDATE 1" in result

async def get_messages_by_user(
    db: DatabaseAdapter,
    user_id: int,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """获取用户的消息列表"""
    query = f"""
        SELECT * FROM {TABLE_NAME}
        WHERE sender_id = $1 OR recipient_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_many(query, user_id, limit, offset)

async def get_conversations_by_user(
    db: DatabaseAdapter,
    user_id: int,
    limit: int = 20
) -> List[Dict]:
    """获取用户的对话列表"""
    query = f"""
        SELECT DISTINCT conversation_id,
               MAX(created_at) as last_message_time,
               COUNT(*) as message_count
        FROM {TABLE_NAME}
        WHERE sender_id = $1 OR recipient_id = $1
        GROUP BY conversation_id
        ORDER BY last_message_time DESC
        LIMIT $2
    """
    return await db.fetch_many(query, user_id, limit)
