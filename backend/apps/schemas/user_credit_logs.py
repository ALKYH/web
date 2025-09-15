"""
用户积分日志系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CreditType(str, Enum):
    """积分类型"""
    mentor_points = "mentor_points"
    learning_points = "learning_points"
    reputation_points = "reputation_points"
    bonus_points = "bonus_points"
    referral_points = "referral_points"


class CreditReason(str, Enum):
    """积分变动原因"""
    session_completed = "session_completed"
    review_received = "review_received"
    profile_completed = "profile_completed"
    referral_bonus = "referral_bonus"
    system_bonus = "system_bonus"
    purchase = "purchase"
    expiration = "expiration"


class UserCreditLogBase(BaseModel):
    """用户积分日志基础模型"""
    user_id: int = Field(..., description="用户ID")
    credit_type: CreditType = Field(..., description="积分类型")
    amount: int = Field(..., description="积分数量(正数为增加，负数为减少)")
    balance_after: int = Field(..., ge=0, description="变动后余额")
    reason: CreditReason = Field(..., description="变动原因")
    reference_id: Optional[int] = Field(None, description="关联ID")
    reference_type: Optional[str] = Field(None, description="关联类型")
    description: Optional[str] = Field(None, description="详细描述")


class UserCreditLogCreate(UserCreditLogBase):
    """创建用户积分日志"""
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class UserCreditLogRead(UserCreditLogBase):
    """用户积分日志读取模型"""
    id: int
    expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserCreditLogDetail(UserCreditLogRead):
    """用户积分日志详情"""
    username: Optional[str] = None


class UserCreditLogListResponse(BaseModel):
    """用户积分日志列表响应"""
    logs: List[UserCreditLogDetail]
    total: int
    has_next: bool


class CreditBalance(BaseModel):
    """积分余额"""
    mentor_points: int = 0
    learning_points: int = 0
    reputation_points: int = 0
    total_points: int = 0


class CreditTransaction(BaseModel):
    """积分交易"""
    credit_type: CreditType
    amount: int
    reason: CreditReason
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class CreditStats(BaseModel):
    """积分统计"""
    total_earned: int = 0
    total_spent: int = 0
    current_balance: CreditBalance
    expiring_soon: int = 0  # 即将过期的积分
