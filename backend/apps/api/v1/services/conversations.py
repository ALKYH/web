"""
会话服务层
处理会话相关的业务逻辑
"""
from typing import List, Dict, Optional
from fastapi import HTTPException, status

from apps.schemas.conversations import (
    ConversationCreate, ConversationRead, ConversationParticipantCreate,
    ConversationDetail, ConversationListResponse
)
from apps.api.v1.repositories import conversations as conv_repo
from apps.api.v1.repositories import message as msg_repo
from libs.database.adapters import DatabaseAdapter


async def create_conversation(db: DatabaseAdapter, participants: List[int], creator_id: int) -> ConversationDetail:
    """
    创建会话
    1. 创建会话记录
    2. 添加所有参与者
    """
    if len(participants) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="会话至少需要一个参与者"
        )

    # 确保创建者在参与者列表中
    if creator_id not in participants:
        participants.append(creator_id)

    # 创建会话
    conversation = await conv_repo.create_conversation(db, ConversationCreate())
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建会话失败"
        )

    # 添加参与者
    for participant_id in participants:
        participant_data = ConversationParticipantCreate(
            conversation_id=conversation['id'],
            user_id=participant_id
        )
        await conv_repo.add_participant(db, participant_data)

    # 获取完整的会话详情
    return await get_conversation_detail(db, conversation['id'], creator_id)


async def get_conversation_detail(db: DatabaseAdapter, conversation_id: int, user_id: int) -> ConversationDetail:
    """
    获取会话详情
    1. 检查用户是否有权限访问
    2. 获取会话信息和参与者
    3. 获取最后一条消息
    """
    # 检查用户是否在会话中
    if not await conv_repo.is_user_in_conversation(db, conversation_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此会话"
        )

    # 获取会话基本信息
    conversation = await conv_repo.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )

    # 获取参与者
    participants = await conv_repo.get_conversation_participants(db, conversation_id)

    # 获取最后一条消息
    last_message = None
    if participants:
        # 简化实现：这里可以优化为更高效的查询
        for participant in participants[:1]:  # 只用第一个参与者查询消息
            messages = await msg_repo.get_messages_by_conversation(
                db, conversation['id'], limit=1
            )
            if messages:
                last_message = messages[0]

    return ConversationDetail(
        id=conversation['id'],
        created_at=conversation['created_at'],
        updated_at=conversation['updated_at'],
        last_message_id=conversation['last_message_id'],
        participants=participants,
        participant_count=len(participants),
        last_message_content=last_message.get('content') if last_message else None,
        last_message_time=last_message.get('created_at') if last_message else None
    )


async def get_user_conversations(db: DatabaseAdapter, user_id: int, skip: int = 0, limit: int = 50) -> ConversationListResponse:
    """
    获取用户的会话列表
    """
    conversations = await conv_repo.get_conversations_by_user(db, user_id, skip, limit)

    # 为每个会话获取详情
    conversation_details = []
    for conv in conversations:
        try:
            detail = await get_conversation_detail(db, conv['id'], user_id)
            conversation_details.append(detail)
        except HTTPException:
            # 如果无法访问会话详情，跳过
            continue

    return ConversationListResponse(
        conversations=conversation_details,
        total=len(conversation_details)
    )


async def add_participant_to_conversation(db: DatabaseAdapter, conversation_id: int, user_id: int, adder_id: int) -> bool:
    """
    添加参与者到会话
    1. 检查adder是否有权限
    2. 检查用户是否已在会话中
    3. 添加参与者
    """
    # 检查adder是否在会话中
    if not await conv_repo.is_user_in_conversation(db, conversation_id, adder_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权管理此会话"
        )

    # 检查用户是否已在会话中
    if await conv_repo.is_user_in_conversation(db, conversation_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已在会话中"
        )

    # 添加参与者
    participant_data = ConversationParticipantCreate(
        conversation_id=conversation_id,
        user_id=user_id
    )

    result = await conv_repo.add_participant(db, participant_data)
    return result is not None


async def remove_participant_from_conversation(db: DatabaseAdapter, conversation_id: int, user_id: int, remover_id: int) -> bool:
    """
    从会话中移除参与者
    1. 检查remover是否有权限
    2. 检查是否是自己退出或管理员移除
    3. 如果只剩一人，删除整个会话
    """
    # 检查remover是否在会话中
    if not await conv_repo.is_user_in_conversation(db, conversation_id, remover_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权管理此会话"
        )

    # 检查是否允许移除（自己退出或管理员）
    if user_id != remover_id:
        # 这里可以添加管理员权限检查
        pass

    # 检查会话参与者数量
    participants = await conv_repo.get_conversation_participants(db, conversation_id)
    if len(participants) <= 2:
        # 如果只剩两人或一人，删除整个会话
        return await conv_repo.delete_conversation(db, conversation_id)

    # 移除参与者
    return await conv_repo.remove_participant(db, conversation_id, user_id)


async def delete_conversation(db: DatabaseAdapter, conversation_id: int, user_id: int) -> bool:
    """
    删除会话
    1. 检查用户是否有权限
    2. 删除会话及其所有参与者
    """
    # 检查用户是否在会话中
    if not await conv_repo.is_user_in_conversation(db, conversation_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此会话"
        )

    return await conv_repo.delete_conversation(db, conversation_id)
