"""
消息相关的服务层
包括消息发送、获取、对话管理等业务逻辑
"""
from typing import List, Dict
from fastapi import HTTPException, status

from apps.schemas.message import MessageCreate
from apps.api.v1.repositories import message as message_repo
from libs.database.adapters import DatabaseAdapter


async def get_messages(db: DatabaseAdapter, user_id: int, limit: int, offset: int) -> List[Dict]:
    """获取用户消息列表"""
    try:
        messages = await message_repo.get_messages_by_user(db, user_id, limit, offset)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息列表失败: {str(e)}"
        )


async def send_message(db: DatabaseAdapter, user_id: int, message_data: MessageCreate) -> Dict:
    """发送消息"""
    message = await message_repo.create(db, message_data)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="发送消息失败"
        )
    return message


async def get_message_detail(db: DatabaseAdapter, message_id: int, user_id: int) -> Dict:
    """获取消息详情"""
    # 这里应该检查用户权限，确保只能查看自己相关的消息
    message = await message_repo.get_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或无权限访问"
        )
    return message


async def mark_message_as_read(db: DatabaseAdapter, message_id: int, user_id: int) -> bool:
    """标记消息为已读"""
    success = await message_repo.mark_message_as_read(db, message_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="消息不存在或已经是已读状态"
        )
    return success


async def get_conversations(db: DatabaseAdapter, user_id: int, limit: int) -> List[Dict]:
    """获取用户对话列表"""
    try:
        conversations = await message_repo.get_conversations_by_user(db, user_id, limit)
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话列表失败: {str(e)}"
        )


async def get_conversation_messages(db: DatabaseAdapter, conversation_id: int, user_id: int, limit: int, offset: int) -> List[Dict]:
    """获取对话消息"""
    try:
        # 这里应该验证用户是否有权限访问该对话
        messages = await message_repo.get_conversation_messages(db, conversation_id, user_id, limit, offset)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话消息失败: {str(e)}"
        )
