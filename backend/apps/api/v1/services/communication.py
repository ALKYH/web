"""
通信中心 - 服务层
提供对话和消息管理的业务逻辑
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.communication import (
    Conversation, ConversationCreate, ConversationUpdate,
    ConversationParticipant, ConversationParticipantCreate,
    Message, MessageCreate, MessageUpdate
)
from apps.api.v1.repositories.communication import (
    get_conversations_by_user, get_conversation_by_id, create_conversation, update_conversation,
    delete_conversation, get_messages_by_conversation, get_message_by_id, create_message,
    update_message, delete_message, is_conversation_participant, add_conversation_participant,
    remove_conversation_participant, get_conversation_participants, update_participant_role
)
from libs.database.adapters import DatabaseAdapter


# ============ 对话服务 ============

async def get_conversations_by_user(db: DatabaseAdapter, user_id: UUID) -> List[Conversation]:
    """获取用户参与的对话列表"""
    return await get_conversations_by_user(db, user_id)


async def get_conversation_by_id(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """获取对话详情"""
    return await get_conversation_by_id(db, conversation_id, user_id)


async def create_conversation(
    db: DatabaseAdapter,
    conversation_data: ConversationCreate,
    creator_id: UUID
) -> Optional[Conversation]:
    """创建对话"""
    return await create_conversation(db, conversation_data, creator_id)


async def update_conversation(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    conversation_data: ConversationUpdate
) -> Optional[Conversation]:
    """更新对话"""
    return await update_conversation(db, conversation_id, user_id, conversation_data)


# ============ 消息服务 ============

async def get_messages_by_conversation(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    page: int = 1,
    page_size: int = 50
) -> List[Message]:
    """获取对话的消息列表"""
    return await get_messages_by_conversation(db, conversation_id, user_id, page, page_size)


async def create_message(
    db: DatabaseAdapter,
    conversation_id: UUID,
    message_data: MessageCreate,
    sender_id: UUID
) -> Optional[Message]:
    """创建消息"""
    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, sender_id):
        return None

    return await create_message(db, conversation_id, message_data, sender_id)


async def update_message(
    db: DatabaseAdapter,
    message_id: UUID,
    sender_id: UUID,
    message_data: MessageUpdate
) -> Optional[Message]:
    """更新消息"""
    return await update_message(db, message_id, sender_id, message_data)


async def delete_message(
    db: DatabaseAdapter,
    message_id: UUID,
    sender_id: UUID
) -> bool:
    """删除消息"""
    return await delete_message(db, message_id, sender_id)


# ============ 参与者服务 ============

async def add_conversation_participant(
    db: DatabaseAdapter,
    conversation_id: UUID,
    participant_data: ConversationParticipantCreate,
    adder_id: UUID
) -> Optional[ConversationParticipant]:
    """添加对话参与者"""
    # 验证添加者是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, adder_id):
        return None

    # 检查用户是否已经是参与者
    if await is_conversation_participant(db, conversation_id, participant_data.user_id):
        return None

    return await add_conversation_participant(db, conversation_id, participant_data)


async def remove_conversation_participant(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    remover_id: UUID
) -> bool:
    """移除对话参与者"""
    # 验证移除者是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, remover_id):
        return False

    return await remove_conversation_participant(db, conversation_id, user_id)


async def get_conversation_participants(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID
) -> List[ConversationParticipant]:
    """获取对话参与者列表"""
    # 验证用户是否为对话参与者
    if not await is_conversation_participant(db, conversation_id, user_id):
        return []

    return await get_conversation_participants(db, conversation_id)
