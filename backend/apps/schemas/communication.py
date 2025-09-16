"""
通信中心 - 数据模型
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 会话 (Conversation) ============
class ConversationBase(BaseModel):
    """会话基础模型"""

    pass  # Currently, conversations are just containers for messages


class ConversationCreate(ConversationBase):
    """会话创建模型"""

    participant_ids: List[UUID] = Field(..., min_length=2, description="参与者User ID列表")


class ConversationUpdate(BaseModel):
    """会话更新模型"""

    pass  # 会话通常不需要更新，主要是通过消息来更新


class Conversation(IDModel, TimestampModel, ConversationBase):
    """会话完整模型"""

    last_message_id: Optional[UUID] = Field(None, description="最后一条消息的ID")

    class Config(IDModel.Config):
        from_attributes = True


# ============ 会话参与者 (ConversationParticipant) ============
class ConversationParticipantBase(BaseModel):
    """会话参与者基础模型"""

    conversation_id: UUID = Field(..., description="会话ID")
    user_id: UUID = Field(..., description="用户ID")


class ConversationParticipantCreate(ConversationParticipantBase):
    """会话参与者创建模型"""

    pass


class ConversationParticipant(IDModel, TimestampModel, ConversationParticipantBase):
    """会话参与者完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


# ============ 消息 (Message) ============
class MessageBase(BaseModel):
    """消息基础模型"""

    conversation_id: UUID = Field(..., description="所属会话ID")
    sender_id: UUID = Field(..., description="发送者User ID")
    content: str = Field(..., description="消息内容")


class MessageCreate(MessageBase):
    """消息创建模型"""

    pass


class MessageUpdate(BaseModel):
    """消息更新模型"""

    content: Optional[str] = None
    is_read: Optional[bool] = None


class Message(IDModel, TimestampModel, MessageBase):
    """消息完整模型"""

    is_read: bool = Field(False, description="是否已读")

    class Config(IDModel.Config):
        from_attributes = True


# ============ 会话列表项 (ConversationListItem) ============
class ConversationListItem(BaseModel):
    """会话列表显示项"""

    conversation_id: UUID = Field(..., description="会话ID")
    last_message: Optional[str] = Field(None, description="最后一条消息内容")
    last_message_time: Optional[datetime] = Field(None, description="最后一条消息时间")
    unread_count: int = Field(0, description="未读消息数量")
    participants: List[dict] = Field(default_factory=list, description="参与者信息")

    class Config:
        from_attributes = True
