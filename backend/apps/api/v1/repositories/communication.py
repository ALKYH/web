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
    Message, MessageCreate, MessageUpdate, ConversationListItem
)
from apps.schemas.message import MessageCreate as LegacyMessageCreate, MessageUpdate as LegacyMessageUpdate
from libs.database.adapters import DatabaseAdapter


# ============ 对话仓库操作 ============

async def get_conversations_by_user(db: DatabaseAdapter, user_id: UUID) -> List[Conversation]:
    """获取用户参与的对话列表"""
    query = """
        SELECT c.id, c.title, c.description, c.conversation_type, c.last_message_id, c.created_at, c.updated_at
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE cp.user_id = $1
        ORDER BY c.updated_at DESC
    """
    rows = await db.fetch_all(query, user_id)
    return [Conversation(**row) for row in rows]


async def get_conversation_by_id(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> Optional[Conversation]:
    """获取对话详情"""
    query = """
        SELECT c.id, c.title, c.description, c.conversation_type, c.last_message_id, c.created_at, c.updated_at
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        WHERE c.id = $1 AND cp.user_id = $2
    """
    row = await db.fetch_one(query, conversation_id, user_id)
    return Conversation(**row) if row else None


async def create_conversation(db: DatabaseAdapter, conversation_data: ConversationCreate, creator_id: UUID) -> Optional[Conversation]:
    """创建对话"""
    # 构建插入语句，支持可选字段
    columns = ["id"]
    values = ["uuid_generate_v7()"]
    params = []

    # 如果提供了标题
    if hasattr(conversation_data, 'title') and conversation_data.title:
        columns.append("title")
        values.append("$1")
        params.append(conversation_data.title)

    # 如果提供了描述
    if hasattr(conversation_data, 'description') and conversation_data.description:
        columns.append("description")
        values.append(f"${len(params) + 1}")
        params.append(conversation_data.description)

    # 如果提供了对话类型
    if hasattr(conversation_data, 'conversation_type') and conversation_data.conversation_type:
        columns.append("conversation_type")
        values.append(f"${len(params) + 1}")
        params.append(conversation_data.conversation_type)

    query = f"""
        INSERT INTO conversations ({', '.join(columns)})
        VALUES ({', '.join(values)})
        RETURNING id, title, description, conversation_type, last_message_id, created_at, updated_at
    """

    row = await db.fetch_one(query, *params)
    if not row:
        return None

    # 创建Conversation对象
    conversation = Conversation(**row)

    # 添加创建者为参与者
    await add_conversation_participant(
        db,
        conversation.id,
        ConversationParticipantCreate(conversation_id=conversation.id, user_id=creator_id)
    )

    # 添加其他参与者
    if hasattr(conversation_data, 'participant_ids') and conversation_data.participant_ids:
        for participant_id in conversation_data.participant_ids:
            if participant_id != creator_id:  # 避免重复添加创建者
                await add_conversation_participant(
                    db,
                    conversation.id,
                    ConversationParticipantCreate(conversation_id=conversation.id, user_id=participant_id)
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

    # 现在数据库中有title字段了
    if hasattr(conversation_data, 'title') and conversation_data.title is not None:
        set_parts.append("title = $1")
        values.append(conversation_data.title)

    if hasattr(conversation_data, 'description') and conversation_data.description is not None:
        param_num = len(values) + 1
        set_parts.append(f"description = ${param_num}")
        values.append(conversation_data.description)

    if hasattr(conversation_data, 'conversation_type') and conversation_data.conversation_type is not None:
        param_num = len(values) + 1
        set_parts.append(f"conversation_type = ${param_num}")
        values.append(conversation_data.conversation_type)

    # 如果没有要更新的字段，只更新时间戳
    if not set_parts:
        query = """
            UPDATE conversations
            SET updated_at = NOW()
            WHERE id = $1
            RETURNING id, title, description, conversation_type, last_message_id, created_at, updated_at
        """
        values = [conversation_id]
    else:
        set_parts.append("updated_at = NOW()")
        param_num = len(values) + 1
        query = f"""
            UPDATE conversations
            SET {', '.join(set_parts)}
            WHERE id = ${param_num}
            RETURNING id, title, description, conversation_type, last_message_id, created_at, updated_at
        """
        values.append(conversation_id)

    row = await db.fetch_one(query, *values)
    return Conversation(**row) if row else None


async def delete_conversation(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> bool:
    """删除对话"""
    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, user_id):
        return False

    # 硬删除对话 - 删除对话记录
    query = """
        DELETE FROM conversations
        WHERE id = $1
    """
    result = await db.execute(query, conversation_id)
    return result == "DELETE 1"

    return True


# ============ 消息仓库操作 ============

async def get_messages_by_conversation(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID, page: int = 1, page_size: int = 50) -> List[Message]:
    """获取对话的消息列表"""
    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, user_id):
        return []

    offset = (page - 1) * page_size
    query = """
        SELECT id, conversation_id, sender_id, content, is_read, created_at, updated_at
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
        SELECT m.id, m.conversation_id, m.sender_id, m.content, m.is_read, m.created_at, m.updated_at
        FROM messages m
        JOIN conversation_participants cp ON m.conversation_id = cp.conversation_id
        WHERE m.id = $1 AND cp.user_id = $2
    """
    row = await db.fetch_one(query, message_id, user_id)
    return Message(**row) if row else None


async def create_message(db: DatabaseAdapter, conversation_id: UUID, message_data: MessageCreate, sender_id: UUID) -> Optional[Message]:
    """创建消息"""
    # 验证发送者是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, sender_id):
        return None

    query = """
        INSERT INTO messages (conversation_id, sender_id, content)
        VALUES ($1, $2, $3)
        RETURNING id, conversation_id, sender_id, content, is_read, created_at, updated_at
    """
    values = (
        conversation_id,
        sender_id,
        message_data.content
    )
    row = await db.fetch_one(query, *values)
    if row:
        # 更新对话的最后活动时间
        await update_conversation_timestamp(db, conversation_id)
        return Message(**row)
    return None


async def update_message(db: DatabaseAdapter, message_id: UUID, sender_id: UUID, update_data: MessageUpdate) -> Optional[Message]:
    """更新消息"""
    query = """
        UPDATE messages
        SET content = $1, updated_at = NOW()
        WHERE id = $2 AND sender_id = $3
        RETURNING id, conversation_id, sender_id, content, is_read, created_at, updated_at
    """
    row = await db.fetch_one(query, update_data.content, message_id, sender_id)
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
        WHERE conversation_id = $1 AND user_id = $2
    """
    row = await db.fetch_one(query, conversation_id, user_id)
    return row is not None


async def add_conversation_participant(db: DatabaseAdapter, conversation_id: UUID, participant_data: ConversationParticipantCreate) -> Optional[ConversationParticipant]:
    """添加对话参与者"""
    query = """
        INSERT INTO conversation_participants (conversation_id, user_id)
        VALUES ($1, $2)
        RETURNING id, conversation_id, user_id, created_at, updated_at
    """
    values = (
        conversation_id,
        participant_data.user_id
    )
    row = await db.fetch_one(query, *values)
    if not row:
        return None

    # 创建ConversationParticipant对象
    return ConversationParticipant(
        id=row['id'],
        conversation_id=row['conversation_id'],
        user_id=row['user_id'],
        created_at=row['created_at'],
        updated_at=row['updated_at']
    )


async def remove_conversation_participant(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID) -> bool:
    """移除对话参与者"""
    query = """
        DELETE FROM conversation_participants
        WHERE conversation_id = $1 AND user_id = $2
    """
    result = await db.execute(query, conversation_id, user_id)
    return result == "DELETE 1"


async def get_conversation_participants(db: DatabaseAdapter, conversation_id: UUID) -> List[ConversationParticipant]:
    """获取对话参与者列表"""
    query = """
        SELECT id, conversation_id, user_id, created_at, updated_at
        FROM conversation_participants
        WHERE conversation_id = $1
        ORDER BY created_at
    """
    rows = await db.fetch_all(query, conversation_id)
    return [ConversationParticipant(**row) for row in rows]


async def update_participant_role(db: DatabaseAdapter, conversation_id: UUID, user_id: UUID, new_role: str, requester_id: UUID) -> bool:
    """更新参与者角色（简化实现，当前不支持角色管理）"""
    # 当前数据库schema不支持角色管理，总是返回False
    return False


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


async def mark_as_read(db: DatabaseAdapter, message_id: UUID, user_id: UUID) -> bool:
    """标记消息为已读"""
    # 验证用户是否能访问这条消息（是否为对话参与者）
    message_query = """
        SELECT conversation_id FROM messages WHERE id = $1
    """
    message_row = await db.fetch_one(message_query, message_id)
    if not message_row:
        return False

    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, message_row['conversation_id'], user_id):
        return False

    # 标记消息为已读
    query = """
        UPDATE messages
        SET is_read = true, updated_at = NOW()
        WHERE id = $1
    """
    result = await db.execute(query, message_id)
    return result == "UPDATE 1"


async def get_messages_by_user(db: DatabaseAdapter, user_id: UUID, limit: int = 20, offset: int = 0) -> List[Message]:
    """获取用户的消息列表"""
    query = """
        SELECT m.id, m.conversation_id, m.sender_id, m.content, m.is_read, m.created_at, m.updated_at
        FROM messages m
        JOIN conversation_participants cp ON m.conversation_id = cp.conversation_id
        WHERE cp.user_id = $1
        ORDER BY m.created_at DESC
        LIMIT $2 OFFSET $3
    """
    rows = await db.fetch_all(query, user_id, limit, offset)
    return [Message(**row) for row in rows]


async def get_conversations_by_user_legacy(db: DatabaseAdapter, user_id: UUID, limit: int = 20) -> List[ConversationListItem]:
    """获取用户的对话列表"""
    query = """
        SELECT
            c.id as conversation_id,
            m.content as last_message,
            m.created_at as last_message_time,
            0 as unread_count,
            c.created_at as created_at
        FROM conversations c
        JOIN conversation_participants cp ON c.id = cp.conversation_id
        LEFT JOIN messages m ON c.id = m.conversation_id
            AND m.created_at = (
                SELECT MAX(created_at) FROM messages
                WHERE conversation_id = c.id
            )
        WHERE cp.user_id = $1
        GROUP BY c.id, m.content, m.created_at, c.created_at
        ORDER BY COALESCE(m.created_at, c.created_at) DESC
        LIMIT $2
    """
    rows = await db.fetch_all(query, user_id, limit)

    # 转换数据格式以匹配ConversationListItem
    result = []
    for row in rows:
        # 将数据库行转换为字典
        data = dict(row)
        # participants字段需要是List[dict]，这里暂时设为空列表
        data['participants'] = []
        result.append(ConversationListItem(**data))

    return result
