"""
交易 & 金融 - 数据模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from .common import IDModel, TimestampModel


# ============ 订单 (Order) ============
class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderBase(BaseModel):
    """订单基础模型"""
    user_id: UUID = Field(..., description="下单用户ID")
    service_id: UUID = Field(..., description="关联的服务ID")
    total_price: Decimal = Field(..., ge=0, description="订单总价")
    status: OrderStatus = Field(OrderStatus.PENDING, description="订单状态")


class OrderCreate(OrderBase):
    """订单创建模型"""
    pass


class OrderUpdate(BaseModel):
    """订单更新模型"""
    status: Optional[OrderStatus] = None


class Order(IDModel, TimestampModel, OrderBase):
    """订单完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 用户钱包 (UserWallet) ============
class UserWalletBase(BaseModel):
    """用户钱包基础模型"""
    user_id: UUID = Field(..., description="用户ID")
    balance: Decimal = Field(Decimal('0'), ge=0, description="账户余额 (CNY)")


class UserWalletCreate(UserWalletBase):
    """用户钱包创建模型"""
    pass


class UserWalletUpdate(BaseModel):
    """用户钱包更新模型"""
    balance: Optional[Decimal] = Field(None, ge=0)


class UserWallet(IDModel, TimestampModel, UserWalletBase):
    """用户钱包完整模型"""
    class Config(IDModel.Config):
        from_attributes = True


# ============ 钱包交易日志 (WalletTransaction) ============
class WalletTransactionType(str, Enum):
    """钱包交易类型"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"


class WalletTransactionBase(BaseModel):
    """钱包交易日志基础模型"""
    wallet_id: UUID = Field(..., description="钱包ID")
    transaction_type: WalletTransactionType = Field(..., description="交易类型")
    amount: Decimal = Field(..., description="交易金额 (正数表示增加, 负数表示减少)")
    order_id: Optional[UUID] = Field(None, description="关联的订单ID")


class WalletTransactionCreate(WalletTransactionBase):
    """钱包交易日志创建模型"""
    pass


class WalletTransaction(IDModel, TimestampModel, WalletTransactionBase):
    """钱包交易日志完整模型"""
    balance_after: Decimal = Field(..., description="交易后余额")

    class Config(IDModel.Config):
        from_attributes = True
