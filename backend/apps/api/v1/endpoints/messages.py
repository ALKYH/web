"""
消息相关的 API 路由
包括消息发送、获取、对话管理等功能
"""
from fastapi import APIRouter, Depends, status, Query
from typing import List

from apps.api.v1.deps import get_current_user, get_database
from apps.api.v1.deps import AuthenticatedUser
from apps.schemas.communication import (
    MessageCreate, Message, ConversationListItem
)
from apps.schemas.common import GeneralResponse
from apps.api.v1.services import message as message_service
from libs.database.adapters import DatabaseAdapter

router = APIRouter()


@router.get(
    "",
    response_model=GeneralResponse[List[Message]],
    summary="获取消息列表",
    description="获取用户的消息列表"
)
async def get_messages(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取消息列表"""
    messages = await message_service.get_messages(db, current_user.id, limit, offset)
    return GeneralResponse(data=messages)


@router.post(
    "",
    response_model=GeneralResponse[Message],
    status_code=status.HTTP_201_CREATED,
    summary="发送消息",
    description="发送新消息"
)
async def send_message(
    message_data: MessageCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """发送消息"""
    message = await message_service.send_message(db, current_user.id, message_data)
    return GeneralResponse(data=message)


@router.get(
    "/{message_id}",
    response_model=GeneralResponse[Message],
    summary="获取消息详情",
    description="获取指定消息的详情"
)
async def get_message_detail(
    message_id: int,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取消息详情"""
    message = await message_service.get_message_detail(db, message_id, current_user.id)
    return GeneralResponse(data=message)


@router.put(
    "/{message_id}/read",
    response_model=GeneralResponse[dict],
    summary="标记消息为已读",
    description="将消息标记为已读状态"
)
async def mark_message_as_read(
    message_id: int,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """标记消息为已读"""
    await message_service.mark_message_as_read(db, message_id, current_user.id)
    return GeneralResponse(data={"message": "消息已标记为已读", "message_id": message_id})


@router.get(
    "/conversations/list",
    response_model=GeneralResponse[List[ConversationListItem]],
    summary="获取对话列表",
    description="获取用户的所有对话"
)
async def get_conversations(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取对话列表"""
    conversations = await message_service.get_conversations(db, current_user.id, limit)
    return GeneralResponse(data=conversations)


@router.get(
    "/conversations/{conversation_id}",
    response_model=GeneralResponse[List[Message]],
    summary="获取对话消息",
    description="获取指定对话的所有消息"
)
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取对话消息"""
    messages = await message_service.get_conversation_messages(db, conversation_id, current_user.id, limit, offset)
    return GeneralResponse(data=messages)