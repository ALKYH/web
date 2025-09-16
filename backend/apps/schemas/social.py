"""
社交中心 - 数据模型
"""
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 好友关系 (Friendship) ============
class FriendshipStatus(str, Enum):
    """好友关系状态"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class FriendshipBase(BaseModel):
    """好友关系基础模型"""
    user_id: UUID = Field(..., description="发起请求的用户ID")
    friend_id: UUID = Field(..., description="被请求的用户ID")
    status: FriendshipStatus = Field(FriendshipStatus.PENDING, description="关系状态")


class FriendshipCreate(FriendshipBase):
    """好友关系创建模型"""
    pass


class FriendshipUpdate(BaseModel):
    """好友关系更新模型"""
    status: Optional[FriendshipStatus] = None


class Friendship(IDModel, TimestampModel, FriendshipBase):
    """好友关系完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 用户声誉 (UserReputation) ============
class UserReputationBase(BaseModel):
    """用户声誉基础模型"""
    user_id: UUID = Field(..., description="用户ID")
    mentor_rating_avg: Decimal = Field(Decimal('0'), ge=0, le=5, description="作为导师的平均评分")
    mentor_rating_count: int = Field(0, ge=0, description="作为导师获得的评分次数")
    mentee_rating_avg: Decimal = Field(Decimal('0'), ge=0, le=5, description="作为学员的平均评分")
    mentee_rating_count: int = Field(0, ge=0, description="作为学员获得的评分次数")
    reputation_score: int = Field(0, description="综合声誉分")


class UserReputationCreate(UserReputationBase):
    """用户声誉创建模型"""
    pass


class UserReputationUpdate(BaseModel):
    """用户声誉更新模型"""
    mentor_rating_avg: Optional[Decimal] = None
    mentor_rating_count: Optional[int] = None
    mentee_rating_avg: Optional[Decimal] = None
    mentee_rating_count: Optional[int] = None
    reputation_score: Optional[int] = None


class UserReputation(IDModel, TimestampModel, UserReputationBase):
    """用户声誉完整模型"""
    class Config(IDModel.Config):
        from_attributes = True
