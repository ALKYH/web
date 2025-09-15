"""
会话系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationParticipantBase(BaseModel):
    """会话参与者基础模型"""
    conversation_id: int = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")


class ConversationParticipantCreate(ConversationParticipantBase):
    """创建会话参与者"""
    pass


class ConversationParticipantRead(ConversationParticipantBase):
    """会话参与者读取模型"""
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConversationBase(BaseModel):
    """会话基础模型"""
    pass  # conversations表只有id, created_at, updated_at, last_message_id


class ConversationCreate(ConversationBase):
    """创建会话"""
    pass


class ConversationRead(ConversationBase):
    """会话读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_message_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class ConversationDetail(ConversationRead):
    """会话详情"""
    participants: List[ConversationParticipantRead] = []
    participant_count: int = 0
    last_message_content: Optional[str] = None
    last_message_time: Optional[datetime] = None


class ConversationListResponse(BaseModel):
    """会话列表响应"""
    conversations: List[ConversationDetail]
    total: int
