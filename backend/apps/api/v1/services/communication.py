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
from apps.api.v1.repositories import communication as communication_repo
from libs.database.adapters import DatabaseAdapter


# ============ 对话服务 ============

async def get_conversations_by_user(db: DatabaseAdapter, user_id: UUID) -> List[Conversation]:
    """获取用户参与的对话列表"""
    return await communication_repo.get_conversations_by_user(db, user_id)


async def get_conversation_by_id(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Conversation]:
    """获取对话详情"""
    return await communication_repo.get_conversation_by_id(db, conversation_id, user_id)


async def create_conversation(
    db: DatabaseAdapter,
    conversation_data: ConversationCreate,
    creator_id: UUID
) -> Conversation:
    """创建对话"""
    return await communication_repo.create_conversation(db, conversation_data, creator_id)


async def update_conversation(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    conversation_data: ConversationUpdate
) -> Optional[Conversation]:
    """更新对话"""
    return await communication_repo.update_conversation(db, conversation_id, user_id, conversation_data)


# ============ 消息服务 ============

async def get_messages_by_conversation(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    page: int = 1,
    page_size: int = 50
) -> List[Message]:
    """获取对话的消息列表"""
    return await communication_repo.get_messages_by_conversation(db, conversation_id, user_id, page, page_size)


# 别名函数，保持向后兼容性
async def get_conversation_messages(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 50,
    offset: int = 0
) -> List[Message]:
    """获取对话的消息列表（别名函数）"""
    page = (offset // limit) + 1
    page_size = limit
    return await get_messages_by_conversation(db, conversation_id, user_id, page, page_size)


async def create_message(
    db: DatabaseAdapter,
    conversation_id: UUID,
    message_data: MessageCreate,
    sender_id: UUID
) -> Optional[Message]:
    """创建消息"""
    # 验证用户是否为对话参与者
    if not await communication_repo.is_conversation_participant(db, conversation_id, sender_id):
        return None

    return await communication_repo.create_message(db, conversation_id, message_data, sender_id)


# 别名函数，保持向后兼容性
async def send_message(
    db: DatabaseAdapter,
    conversation_id: UUID,
    message_data: MessageCreate,
    sender_id: UUID
) -> Optional[Message]:
    """发送消息（别名函数）"""
    return await create_message(db, conversation_id, message_data, sender_id)


async def update_message(
    db: DatabaseAdapter,
    message_id: UUID,
    sender_id: UUID,
    update_data: MessageUpdate  # 改名为 update_data
) -> Optional[Message]:
    """更新消息"""
    return await communication_repo.update_message(db, message_id, sender_id, update_data)


async def delete_message(
    db: DatabaseAdapter,
    message_id: UUID,
    sender_id: UUID
) -> bool:
    """删除消息"""
    return await communication_repo.delete_message(db, message_id, sender_id)


# ============ 用户消息入口（合并自 messages.py） ==========

async def get_messages(
    db: DatabaseAdapter,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Message]:
    """获取用户的消息列表。

    Args:
        db: 数据库适配器
        user_id: 当前用户ID
        limit: 返回数量
        offset: 偏移量

    Returns:
        用户的消息列表
    """
    return await communication_repo.get_messages_by_user(db, user_id, limit, offset)


async def get_message_detail(
    db: DatabaseAdapter,
    message_id: UUID,
    user_id: UUID
) -> Optional[Message]:
    """获取消息详情。

    Args:
        db: 数据库适配器
        message_id: 消息ID
        user_id: 当前用户ID（用于权限校验）

    Returns:
        消息对象，若无权限或不存在返回None
    """
    return await communication_repo.get_message_by_id(db, message_id, user_id)


async def mark_message_as_read(
    db: DatabaseAdapter,
    message_id: UUID,
    user_id: UUID
) -> bool:
    """标记消息为已读。

    Args:
        db: 数据库适配器
        message_id: 消息ID
        user_id: 当前用户ID（用于权限校验）

    Returns:
        是否标记成功
    """
    return await communication_repo.mark_as_read(db, message_id, user_id)


# ============ 参与者服务 ============

async def add_conversation_participant(
    db: DatabaseAdapter,
    conversation_id: UUID,
    participant_data: ConversationParticipantCreate,
    adder_id: UUID
) -> Optional[ConversationParticipant]:
    """添加对话参与者"""
    # 验证添加者是否为对话参与者
    if not await communication_repo.is_conversation_participant(db, conversation_id, adder_id):
        return None

    # 检查用户是否已经是参与者
    if await communication_repo.is_conversation_participant(db, conversation_id, participant_data.user_id):
        return None

    return await communication_repo.add_conversation_participant(db, conversation_id, participant_data)


async def remove_conversation_participant(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    remover_id: UUID
) -> bool:
    """移除对话参与者"""
    # 验证移除者是否为对话参与者
    if not await communication_repo.is_conversation_participant(db, conversation_id, remover_id):
        return False

    return await communication_repo.remove_conversation_participant(db, conversation_id, user_id)


async def get_conversation_participants(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID
) -> List[ConversationParticipant]:
    """获取对话参与者列表"""
    # 验证用户是否为对话参与者
    if not await communication_repo.is_conversation_participant(db, conversation_id, user_id):
        return []

    return await communication_repo.get_conversation_participants(db, conversation_id)


async def delete_conversation(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID
) -> bool:
    """删除对话"""
    return await communication_repo.delete_conversation(db, conversation_id, user_id)
