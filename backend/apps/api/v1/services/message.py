"""
消息服务 - 服务层
提供消息相关的业务逻辑，适配messages端点的需求
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.communication import (
    Message, MessageCreate, ConversationListItem
)
from apps.api.v1.services.communication import (
    get_messages_by_conversation,
    create_message,
    get_conversations_by_user,
    update_message
)
from apps.api.v1.repositories.communication import (
    get_messages_by_user,
    get_message_by_id,
    mark_as_read
)
from libs.database.adapters import DatabaseAdapter


async def get_messages(
    db: DatabaseAdapter,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Message]:
    """获取用户的消息列表"""
    return await get_messages_by_user(db, user_id, limit, offset)


async def send_message(
    db: DatabaseAdapter,
    user_id: UUID,
    message_data: MessageCreate
) -> Optional[Message]:
    """发送消息"""
    # 从message_data中获取对话ID和消息内容
    conversation_id = getattr(message_data, 'conversation_id', None)
    if not conversation_id:
        return None

    return await create_message(db, conversation_id, message_data, user_id)


async def get_message_detail(
    db: DatabaseAdapter,
    message_id: UUID,
    user_id: UUID
) -> Optional[Message]:
    """获取消息详情"""
    return await get_message_by_id(db, message_id, user_id)


async def mark_message_as_read(
    db: DatabaseAdapter,
    message_id: UUID,
    user_id: UUID
) -> bool:
    """标记消息为已读"""
    return await mark_as_read(db, message_id, user_id)


async def get_conversations(
    db: DatabaseAdapter,
    user_id: UUID,
    limit: int = 20
) -> List[ConversationListItem]:
    """获取用户的对话列表"""
    conversations = await get_conversations_by_user(db, user_id)

    # 转换为ConversationListItem格式
    # 使用repository中的函数获取更详细的对话信息
    from apps.api.v1.repositories.communication import get_conversations_by_user_legacy
    conversation_items = await get_conversations_by_user_legacy(db, user_id, limit)
    return conversation_items

    return conversation_items


async def get_conversation_messages(
    db: DatabaseAdapter,
    conversation_id: UUID,
    user_id: UUID,
    limit: int = 50,
    offset: int = 0
) -> List[Message]:
    """获取对话的消息列表"""
    # 计算页码
    page = (offset // limit) + 1
    return await get_messages_by_conversation(
        db, conversation_id, user_id, page, limit
    )
