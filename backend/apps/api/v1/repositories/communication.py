"""
通信系统仓库层
提供对话、消息和参与者的数据库操作
统一管理所有通信相关的数据访问操作
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.communication import (
    Conversation, ConversationCreate, ConversationUpdate,
    ConversationParticipant, ConversationParticipantCreate,
    Message, MessageCreate, MessageUpdate
)
from apps.schemas.message import MessageCreate as LegacyMessageCreate, MessageUpdate as LegacyMessageUpdate
from libs.database.adapters import DatabaseAdapter


# ============ 对话仓库操作 ============

async def get_conversations_by_user(db: DatabaseAdapter, user_id: UUID) -> List[Conversation]:
    """获取用户参与的对话列表"""
    query = """
        SELECT c.id, c.title, c.description, c.conversation_type, c.created_at, c.updated_at
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = $1 AND cp.is_active = true
        ORDER BY c.updated_at DESC
    """
    rows = await db.fetch_all(query, user_id)
    return [Conversation(**row) for row in rows]


async def get_conversation_by_id(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
    """获取对话详情"""
    query = """
        SELECT c.id, c.title, c.description, c.conversation_type, c.created_at, c.updated_at
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE c.id = $1 AND cp.user_id = $2 AND cp.is_active = true
    """
    row = await db.fetch_one(query, conversation_id, user_id)
    return Conversation(**row) if row else None


async def create_conversation(db: DatabaseAdapter, conversation_data: ConversationCreate, creator_id: UUID) -> Optional[Conversation]:
    """创建对话"""
    query = """
        INSERT INTO conversations (title, description, conversation_type)
        VALUES ($1, $2, $3)
        RETURNING id, title, description, conversation_type, created_at, updated_at
    """
    values = (
        conversation_data.title,
        conversation_data.description,
        conversation_data.conversation_type.value if hasattr(conversation_data.conversation_type, 'value') else conversation_data.conversation_type
    )
    row = await db.fetch_one(query, *values)
    if not row:
        return None

    conversation = Conversation(**row)

    # 添加创建者为参与者
    await add_conversation_participant(
        db,
        conversation.id,
        ConversationParticipantCreate(user_id=creator_id, role="admin")
    )

    return conversation


async def update_conversation(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID, conversation_data: ConversationUpdate) -> Optional[Conversation]:
    """更新对话"""
    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, user_id):
        return None

    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if conversation_data.title is not None:
        set_parts.append(f"title = ${param_index}")
        values.append(conversation_data.title)
        param_index += 1

    if conversation_data.description is not None:
        set_parts.append(f"description = ${param_index}")
        values.append(conversation_data.description)
        param_index += 1

    if conversation_data.conversation_type is not None:
        set_parts.append(f"conversation_type = ${param_index}")
        values.append(conversation_data.conversation_type.value if hasattr(conversation_data.conversation_type, 'value') else conversation_data.conversation_type)
        param_index += 1

    if not set_parts:
        return await get_conversation_by_id(db, conversation_id, user_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE conversations
        SET {', '.join(set_parts)}
        WHERE id = ${param_index}
        RETURNING id, title, description, conversation_type, created_at, updated_at
    """
    values.append(conversation_id)

    row = await db.fetch_one(query, *values)
    return Conversation(**row) if row else None


async def delete_conversation(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> bool:
    """删除对话"""
    # 验证用户是否为对话参与者且为管理员
    participant_query = """
        SELECT role FROM conversation_participants
        WHERE conversation_id = $1 AND user_id = $2 AND is_active = true
    """
    participant = await db.fetch_one(participant_query, conversation_id, user_id)
    if not participant or participant['role'] != 'admin':
        return False

    # 软删除对话 - 将所有参与者标记为非活跃
    await db.execute("""
        UPDATE conversation_participants
        SET is_active = false, left_at = NOW()
        WHERE conversation_id = $1
    """, conversation_id)

    return True


# ============ 消息仓库操作 ============

async def get_messages_by_conversation(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID, page: int = 1, page_size: int = 50) -> List[Message]:
    """获取对话的消息列表"""
    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, user_id):
        return []

    offset = (page - 1) * page_size
    query = """
        SELECT id, conversation_id, sender_id, content, message_type, is_edited, created_at, updated_at
        FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    rows = await db.fetch_all(query, conversation_id, page_size, offset)
    return [Message(**row) for row in rows]


async def get_message_by_id(db: DatabaseAdapter, message_id: UUID, user_id: UUID) -> Optional[Message]:
    """根据ID获取消息"""
    query = """
        SELECT m.id, m.conversation_id, m.sender_id, m.content, m.message_type, m.is_edited, m.created_at, m.updated_at
        FROM messages m
        JOIN conversation_participants cp ON m.conversation_id = cp.conversation_id
        WHERE m.id = $1 AND cp.user_id = $2 AND cp.is_active = true
    """
    row = await db.fetch_one(query, message_id, user_id)
    return Message(**row) if row else None


async def create_message(db: DatabaseAdapter, conversation_id: UUID, message_data: MessageCreate, sender_id: UUID) -> Optional[Message]:
    """创建消息"""
    # 验证发送者是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, sender_id):
        return None

    query = """
        INSERT INTO messages (conversation_id, sender_id, content, message_type)
        VALUES ($1, $2, $3, $4)
        RETURNING id, conversation_id, sender_id, content, message_type, is_edited, created_at, updated_at
    """
    values = (
        conversation_id,
        sender_id,
        message_data.content,
        message_data.message_type.value if hasattr(message_data.message_type, 'value') else message_data.message_type
    )
    row = await db.fetch_one(query, *values)
    if row:
        # 更新对话的最后活动时间
        await update_conversation_timestamp(db, conversation_id)
        return Message(**row)
    return None


async def update_message(db: DatabaseAdapter, message_id: UUID, sender_id: UUID, message_data: MessageUpdate) -> Optional[Message]:
    """更新消息"""
    query = """
        UPDATE messages
        SET content = $1, is_edited = true, updated_at = NOW()
        WHERE id = $2 AND sender_id = $3
        RETURNING id, conversation_id, sender_id, content, message_type, is_edited, created_at, updated_at
    """
    row = await db.fetch_one(query, message_data.content, message_id, sender_id)
    return Message(**row) if row else None


async def delete_message(db: DatabaseAdapter, message_id: UUID, sender_id: UUID) -> bool:
    """删除消息"""
    query = """
        DELETE FROM messages
        WHERE id = $1 AND sender_id = $2
    """
    result = await db.execute(query, message_id, sender_id)
    return result == "DELETE 1"


# ============ 参与者仓库操作 ============

async def is_conversation_participant(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> bool:
    """检查用户是否为对话参与者"""
    query = """
        SELECT 1 FROM conversation_participants
        WHERE conversation_id = $1 AND user_id = $2 AND is_active = true
    """
    row = await db.fetch_one(query, conversation_id, user_id)
    return row is not None


async def add_conversation_participant(db: DatabaseAdapter, conversation_id: UUID, participant_data: ConversationParticipantCreate) -> Optional[ConversationParticipant]:
    """添加对话参与者"""
    query = """
        INSERT INTO conversation_participants (conversation_id, user_id, role, is_active)
        VALUES ($1, $2, $3, $4)
        RETURNING id, conversation_id, user_id, role, joined_at, is_active
    """
    values = (
        conversation_id,
        participant_data.user_id,
        participant_data.role.value if hasattr(participant_data.role, 'value') else participant_data.role,
        True
    )
    row = await db.fetch_one(query, *values)
    return ConversationParticipant(**row) if row else None


async def remove_conversation_participant(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> bool:
    """移除对话参与者"""
    query = """
        UPDATE conversation_participants
        SET is_active = false, left_at = NOW()
        WHERE conversation_id = $1 AND user_id = $2 AND is_active = true
    """
    result = await db.execute(query, conversation_id, user_id)
    return result == "UPDATE 1"


async def get_conversation_participants(db: DatabaseAdapter, conversation_id: UUID) -> List[ConversationParticipant]:
    """获取对话参与者列表"""
    query = """
        SELECT id, conversation_id, user_id, role, joined_at, left_at, is_active
        FROM conversation_participants
        WHERE conversation_id = $1 AND is_active = true
        ORDER BY joined_at
    """
    rows = await db.fetch_all(query, conversation_id)
    return [ConversationParticipant(**row) for row in rows]


async def update_participant_role(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID, new_role: str, requester_id: UUID) -> bool:
    """更新参与者角色（需要管理员权限）"""
    # 验证请求者是否为管理员
    requester_query = """
        SELECT role FROM conversation_participants
        WHERE conversation_id = $1 AND user_id = $2 AND is_active = true
    """
    requester = await db.fetch_one(requester_query, conversation_id, requester_id)
    if not requester or requester['role'] != 'admin':
        return False

    query = """
        UPDATE conversation_participants
        SET role = $1, updated_at = NOW()
        WHERE conversation_id = $2 AND user_id = $3 AND is_active = true
    """
    result = await db.execute(query, new_role, conversation_id, user_id)
    return result == "UPDATE 1"


# ============ 辅助函数 ============

async def update_conversation_timestamp(db: DatabaseAdapter, conversation_id: UUID) -> None:
    """更新对话时间戳"""
    query = """
        UPDATE conversations
        SET updated_at = NOW()
        WHERE id = $1
    """
    await db.execute(query, conversation_id)


# ============ 兼容性函数（向后兼容） ============

async def get_by_id(db: DatabaseAdapter, message_id: int) -> Optional[dict]:
    """根据ID获取消息（兼容旧接口，返回字典）"""
    query = f"SELECT * FROM messages WHERE id = $1"
    return await db.fetch_one(query, message_id)


async def get_by_conversation(db: DatabaseAdapter, conversation_id: int, limit: int = 50, offset: int = 0) -> List[dict]:
    """获取对话中的消息列表（兼容旧接口，返回字典列表）"""
    query = f"""
        SELECT * FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_many(query, conversation_id, limit, offset)


async def create(db: DatabaseAdapter, message_in: LegacyMessageCreate) -> Optional[dict]:
    """创建新消息（兼容旧接口）"""

    # 构建插入数据
    create_data = message_in.model_dump()
    create_data["status"] = "sent"
    create_data["is_read"] = False

    # 动态构建插入语句
    columns = ", ".join(create_data.keys())
    placeholders = ", ".join([f"${i+1}" for i in range(len(create_data))])

    query = f"""
        INSERT INTO messages ({columns})
        VALUES ({placeholders})
        RETURNING *
    """

    return await db.fetch_one(query, *create_data.values())


async def mark_as_read(db: DatabaseAdapter, message_id: int, user_id: int) -> bool:
    """标记消息为已读（兼容旧接口）"""
    query = f"""
        UPDATE messages
        SET is_read = true, read_at = NOW()
        WHERE id = $1 AND recipient_id = $2
    """
    result = await db.execute(query, message_id, user_id)
    return "UPDATE 1" in result


async def get_messages_by_user(db: DatabaseAdapter, user_id: int, limit: int = 20, offset: int = 0) -> List[dict]:
    """获取用户的消息列表（兼容旧接口）"""
    query = f"""
        SELECT * FROM messages
        WHERE sender_id = $1 OR recipient_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_many(query, user_id, limit, offset)


async def get_conversations_by_user_legacy(db: DatabaseAdapter, user_id: int, limit: int = 20) -> List[dict]:
    """获取用户的对话列表（兼容旧接口）"""
    query = f"""
        SELECT DISTINCT conversation_id,
               MAX(created_at) as last_message_time,
               COUNT(*) as message_count
        FROM messages
        WHERE sender_id = $1 OR recipient_id = $1
        GROUP BY conversation_id
        ORDER BY last_message_time DESC
        LIMIT $2
    """
    return await db.fetch_many(query, user_id, limit)
