"""
用户积分日志 - 数据模型
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from decimal import Decimal

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 积分类型枚举 ============
class CreditType(str, Enum):
    """积分类型"""
    EARNED = "earned"  # 赚取的积分
    SPENT = "spent"    # 消费的积分
    BONUS = "bonus"    # 奖励积分
    REFUND = "refund"  # 退还积分


# ============ 积分交易模型 ============
class CreditTransactionBase(BaseModel):
    """积分交易基础模型"""

    user_id: UUID = Field(..., description="用户ID")
    amount: Decimal = Field(..., ge=0, description="积分数量")
    credit_type: CreditType = Field(..., description="积分类型")
    description: str = Field(..., description="交易描述")
    reference_id: Optional[UUID] = Field(None, description="关联的交易ID")
    reference_type: Optional[str] = Field(None, description="关联的交易类型")


class CreditTransactionCreate(CreditTransactionBase):
    """积分交易创建模型"""
    pass


class CreditTransactionUpdate(BaseModel):
    """积分交易更新模型"""

    description: Optional[str] = None


class CreditTransaction(IDModel, TimestampModel, CreditTransactionBase):
    """积分交易完整模型"""

    class Config(IDModel.Config):
        from_attributes = True


class UserCreditLogCreate(CreditTransactionCreate):
    """用户积分日志创建模型（别名）"""
    pass


class UserCreditLog(CreditTransaction):
    """用户积分日志模型（别名）"""
    pass


# ============ 积分余额模型 ============
class CreditBalance(BaseModel):
    """用户积分余额"""

    user_id: UUID = Field(..., description="用户ID")
    total_earned: Decimal = Field(..., description="累计赚取积分")
    total_spent: Decimal = Field(..., description="累计消费积分")
    current_balance: Decimal = Field(..., description="当前余额")
    last_updated: datetime = Field(..., description="最后更新时间")


# ============ 积分统计模型 ============
class CreditStats(BaseModel):
    """积分统计信息"""

    user_id: UUID = Field(..., description="用户ID")
    total_earned: Decimal = Field(..., description="累计赚取积分")
    total_spent: Decimal = Field(..., description="累计消费积分")
    total_bonus: Decimal = Field(..., description="累计奖励积分")
    total_refund: Decimal = Field(..., description="累计退还积分")
    current_balance: Decimal = Field(..., description="当前余额")
    transaction_count: int = Field(..., description="交易总数")
    last_transaction_date: Optional[datetime] = Field(None, description="最后交易时间")
