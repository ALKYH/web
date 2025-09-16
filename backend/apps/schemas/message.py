"""
消息中心 - 数据模型别名文件
为了保持代码结构的一致性，此文件导入 communication.py 中的消息相关模型
"""
from .communication import (
    MessageBase,
    MessageCreate,
    MessageUpdate,
    Message,
    ConversationBase,
    ConversationCreate,
    ConversationUpdate,
    Conversation,
    ConversationListItem
)

# 导出别名以保持兼容性
__all__ = [
    "MessageBase",
    "MessageCreate",
    "MessageUpdate",
    "Message",
    "ConversationBase",
    "ConversationCreate",
    "ConversationUpdate",
    "Conversation",
    "ConversationListItem"
]
