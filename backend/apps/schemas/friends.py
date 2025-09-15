"""
朋友关系系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FriendStatus(str, Enum):
    """朋友关系状态"""
    pending = "pending"
    accepted = "accepted"
    blocked = "blocked"


class FriendBase(BaseModel):
    """朋友关系基础模型"""
    user_id: int = Field(..., description="用户ID")
    friend_id: int = Field(..., description="朋友ID")
    status: FriendStatus = Field(default=FriendStatus.pending, description="关系状态")


class FriendCreate(FriendBase):
    """创建朋友关系"""
    pass


class FriendUpdate(BaseModel):
    """更新朋友关系"""
    status: Optional[FriendStatus] = None


class FriendRead(FriendBase):
    """朋友关系读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class FriendDetail(FriendRead):
    """朋友关系详情"""
    user_username: Optional[str] = None
    user_avatar: Optional[str] = None
    friend_username: Optional[str] = None
    friend_avatar: Optional[str] = None


class FriendRequest(BaseModel):
    """朋友请求"""
    friend_id: int = Field(..., description="要添加为朋友的用户ID")


class FriendListResponse(BaseModel):
    """朋友列表响应"""
    friends: List[FriendDetail]
    total: int


class FriendRequestListResponse(BaseModel):
    """朋友请求列表响应"""
    requests: List[FriendDetail]
    total: int
