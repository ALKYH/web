"""
通信中心 - API 路由
包括对话和消息管理的API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from apps.api.v1.deps import (
    get_current_user,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.communication import (
    Conversation, ConversationCreate, ConversationUpdate,
    ConversationParticipant, ConversationParticipantCreate,
    Message, MessageCreate, MessageUpdate
)
from apps.schemas.common import GeneralResponse, PaginatedResponse
from apps.api.v1.services import communication as communication_service

router = APIRouter()


# ============ 对话管理 ============

@router.get(
    "/conversations",
    response_model=GeneralResponse[List[Conversation]],
    summary="获取用户对话列表",
    description="获取当前用户的所有对话"
)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取用户的对话列表

    - **limit**: 返回数量（1-100）
    - **offset**: 偏移量
    """
    conversations = await communication_service.get_conversations_by_user(
        db, current_user.id
    )
    return GeneralResponse(data=conversations)


@router.post(
    "/conversations",
    response_model=GeneralResponse[Conversation],
    status_code=status.HTTP_201_CREATED,
    summary="创建对话",
    description="创建新的对话"
)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建新对话

    - **title**: 对话标题
    - **description**: 对话描述（可选）
    - **conversation_type**: 对话类型
    """
    conversation = await communication_service.create_conversation(
        db, conversation_data, current_user.id
    )
    return GeneralResponse(data=conversation)


@router.get(
    "/conversations/{conversation_id}",
    response_model=GeneralResponse[Conversation],
    summary="获取对话详情",
    description="获取指定对话的详细信息"
)
async def get_conversation(
    conversation_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取对话详情

    - **conversation_id**: 对话ID
    """
    conversation = await communication_service.get_conversation_by_id(
        db, conversation_id, current_user.id
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return GeneralResponse(data=conversation)


@router.put(
    "/conversations/{conversation_id}",
    response_model=GeneralResponse[Conversation],
    summary="更新对话",
    description="更新对话信息"
)
async def update_conversation(
    conversation_id: UUID,
    conversation_data: ConversationUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新对话信息

    - **conversation_id**: 对话ID
    - **title**: 新标题（可选）
    - **description**: 新描述（可选）
    """
    conversation = await communication_service.update_conversation(
        db, conversation_id, current_user.id, conversation_data
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return GeneralResponse(data=conversation)


@router.delete(
    "/conversations/{conversation_id}",
    response_model=GeneralResponse[dict],
    summary="删除对话",
    description="删除指定的对话"
)
async def delete_conversation(
    conversation_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除对话

    - **conversation_id**: 对话ID
    """
    success = await communication_service.delete_conversation(
        db, conversation_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return GeneralResponse(data={"message": "对话删除成功"})


# ============ 对话参与者管理 ============

@router.get(
    "/conversations/{conversation_id}/participants",
    response_model=GeneralResponse[List[ConversationParticipant]],
    summary="获取对话参与者",
    description="获取指定对话的所有参与者"
)
async def list_conversation_participants(
    conversation_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取对话参与者列表

    - **conversation_id**: 对话ID
    """
    participants = await communication_service.get_conversation_participants(
        db, conversation_id, current_user.id
    )
    return GeneralResponse(data=participants)


@router.post(
    "/conversations/{conversation_id}/participants",
    response_model=GeneralResponse[ConversationParticipant],
    status_code=status.HTTP_201_CREATED,
    summary="添加对话参与者",
    description="向对话添加新参与者"
)
async def add_conversation_participant(
    conversation_id: UUID,
    participant_data: ConversationParticipantCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    添加对话参与者

    - **conversation_id**: 对话ID
    - **user_id**: 参与者用户ID
    """
    participant = await communication_service.add_conversation_participant(
        db, conversation_id, participant_data, current_user.id
    )
    return GeneralResponse(data=participant)


@router.delete(
    "/conversations/{conversation_id}/participants/{user_id}",
    response_model=GeneralResponse[dict],
    summary="移除对话参与者",
    description="从对话中移除指定参与者"
)
async def remove_conversation_participant(
    conversation_id: UUID,
    user_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    移除对话参与者

    - **conversation_id**: 对话ID
    - **user_id**: 参与者用户ID
    """
    success = await communication_service.remove_conversation_participant(
        db, conversation_id, user_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="参与者不存在")
    return GeneralResponse(data={"message": "参与者移除成功"})


# ============ 对话消息管理 ============

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=GeneralResponse[List[Message]],
    summary="获取对话消息",
    description="获取指定对话的所有消息"
)
async def list_conversation_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取对话消息列表

    - **conversation_id**: 对话ID
    - **limit**: 返回数量（1-200）
    - **offset**: 偏移量
    """
    messages = await communication_service.get_conversation_messages(
        db, conversation_id, current_user.id, limit, offset
    )
    return GeneralResponse(data=messages)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=GeneralResponse[Message],
    status_code=status.HTTP_201_CREATED,
    summary="发送消息",
    description="在对话中发送新消息"
)
async def send_message(
    conversation_id: UUID,
    message_data: dict,  # 使用dict避免Pydantic验证问题
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    发送消息

    - **conversation_id**: 对话ID
    - **content**: 消息内容
    """
    # 创建MessageCreate对象，conversation_id从路径参数获取
    from apps.schemas.communication import MessageCreate
    create_data = MessageCreate(
        conversation_id=conversation_id,
        content=message_data.get("content", "")
    )

    message = await communication_service.send_message(
        db, conversation_id, create_data, current_user.id
    )
    if not message:
        raise HTTPException(status_code=403, detail="发送消息失败，可能不是对话参与者")
    return GeneralResponse(data=message)


@router.put(
    "/messages/{message_id}",
    response_model=GeneralResponse[Message],
    summary="更新消息",
    description="更新指定消息的内容"
)
async def update_message(
    message_id: UUID,
    update_data: MessageUpdate,  # 改名为 update_data 避免与路径参数冲突
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新消息

    - **message_id**: 消息ID
    - **content**: 新消息内容（可选）
    - **is_read**: 阅读状态（可选）
    """
    message = await communication_service.update_message(
        db, message_id, current_user.id, update_data
    )
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    return GeneralResponse(data=message)


@router.delete(
    "/messages/{message_id}",
    response_model=GeneralResponse[dict],
    summary="删除消息",
    description="删除指定的消息"
)
async def delete_message(
    message_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除消息

    - **message_id**: 消息ID
    """
    success = await communication_service.delete_message(
        db, message_id, current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")
    return GeneralResponse(data={"message": "消息删除成功"})


# ============ 用户消息入口（合并自 messages.py） ============

@router.get(
    "/messages",
    response_model=GeneralResponse[List[Message]],
    summary="获取消息列表",
    description="获取当前用户的所有消息。支持分页。"
)
async def list_messages(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取用户的消息列表

    - **limit**: 返回数量（1-100）
    - **offset**: 偏移量
    """
    messages = await communication_service.get_messages(db, current_user.id, limit, offset)
    return GeneralResponse(data=messages)


@router.get(
    "/messages/{message_id}",
    response_model=GeneralResponse[Message],
    summary="获取消息详情",
    description="获取指定消息的详细信息"
)
async def get_message_detail(
    message_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取消息详情

    - **message_id**: 消息ID
    """
    message = await communication_service.get_message_detail(db, message_id, current_user.id)
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    return GeneralResponse(data=message)


@router.put(
    "/messages/{message_id}/read",
    response_model=GeneralResponse[dict],
    summary="标记消息为已读",
    description="将指定消息标记为已读"
)
async def mark_message_as_read(
    message_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    标记消息为已读

    - **message_id**: 消息ID
    """
    success = await communication_service.mark_message_as_read(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")
    return GeneralResponse(data={"message": "消息已标记为已读", "message_id": message_id})
