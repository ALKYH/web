"""
会话相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.conversations import ConversationCreate, ConversationUpdate, ConversationParticipantCreate
from libs.database.adapters import DatabaseAdapter


async def get_conversation_by_id(db: DatabaseAdapter, conversation_id: int) -> Optional[Dict]:
    """根据ID获取会话"""
    query = "SELECT * FROM conversations WHERE id = $1"
    return await db.fetch_one(query, conversation_id)


async def get_conversations_by_user(db: DatabaseAdapter, user_id: int, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的会话列表"""
    query = """
        SELECT c.* FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = $1
        ORDER BY c.updated_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_all(query, user_id, limit, skip)


async def create_conversation(db: DatabaseAdapter, conversation: ConversationCreate) -> Optional[Dict]:
    """创建会话"""
    query = """
        INSERT INTO conversations (created_at, updated_at)
        VALUES (NOW(), NOW())
        RETURNING *
    """
    return await db.fetch_one(query)


async def update_conversation(db: DatabaseAdapter, conversation_id: int, conversation: ConversationUpdate) -> Optional[Dict]:
    """更新会话"""
    update_data = conversation.model_dump(exclude_unset=True)
    if not update_data:
        return await get_conversation_by_id(db, conversation_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE conversations SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, conversation_id, *update_data.values())


async def delete_conversation(db: DatabaseAdapter, conversation_id: int) -> bool:
    """删除会话"""
    query = "DELETE FROM conversations WHERE id = $1"
    result = await db.execute(query, conversation_id)
    return result == "DELETE 1"


# 会话参与者相关操作

async def add_participant(db: DatabaseAdapter, participant: ConversationParticipantCreate) -> Optional[Dict]:
    """添加会话参与者"""
    query = """
        INSERT INTO conversation_participants (conversation_id, user_id, created_at)
        VALUES ($1, $2, NOW())
        RETURNING *
    """
    return await db.fetch_one(query, participant.conversation_id, participant.user_id)


async def remove_participant(db: DatabaseAdapter, conversation_id: int, user_id: int) -> bool:
    """移除会话参与者"""
    query = "DELETE FROM conversation_participants WHERE conversation_id = $1 AND user_id = $2"
    result = await db.execute(query, conversation_id, user_id)
    return result == "DELETE 1"


async def get_conversation_participants(db: DatabaseAdapter, conversation_id: int) -> List[Dict]:
    """获取会话参与者"""
    query = """
        SELECT cp.*, u.username, u.avatar_url
        FROM conversation_participants cp
        JOIN users u ON cp.user_id = u.id
        WHERE cp.conversation_id = $1
        ORDER BY cp.created_at
    """
    return await db.fetch_all(query, conversation_id)


async def is_user_in_conversation(db: DatabaseAdapter, conversation_id: int, user_id: int) -> bool:
    """检查用户是否在会话中"""
    query = "SELECT 1 FROM conversation_participants WHERE conversation_id = $1 AND user_id = $2"
    result = await db.fetch_one(query, conversation_id, user_id)
    return result is not None
