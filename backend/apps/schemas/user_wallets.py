"""
用户钱包系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class WalletTransactionType(str, Enum):
    """钱包交易类型"""
    deposit = "deposit"  # 充值
    withdrawal = "withdrawal"  # 提现
    payment = "payment"  # 支付
    refund = "refund"  # 退款
    bonus = "bonus"  # 奖金
    fee = "fee"  # 手续费
    transfer = "transfer"  # 转账


class UserWalletBase(BaseModel):
    """用户钱包基础模型"""
    user_id: int = Field(..., description="用户ID")
    balance: Decimal = Field(default=Decimal('0'), ge=0, description="账户余额")
    frozen_balance: Decimal = Field(default=Decimal('0'), ge=0, description="冻结余额")
    currency: str = Field(default="CNY", description="货币类型")
    mentor_points: int = Field(default=0, ge=0, description="导师积分")
    learning_points: int = Field(default=0, ge=0, description="学习积分")
    reputation_points: int = Field(default=0, ge=0, description="声誉积分")


class UserWalletCreate(UserWalletBase):
    """创建用户钱包"""
    pass


class UserWalletUpdate(BaseModel):
    """更新用户钱包"""
    balance: Optional[Decimal] = None
    frozen_balance: Optional[Decimal] = None
    currency: Optional[str] = None
    mentor_points: Optional[int] = None
    learning_points: Optional[int] = None
    reputation_points: Optional[int] = None


class UserWalletRead(UserWalletBase):
    """用户钱包读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserWalletDetail(UserWalletRead):
    """用户钱包详情"""
    username: Optional[str] = None
    user_email: Optional[str] = None
    available_balance: Decimal = Field(default=Decimal('0'), description="可用余额")


class WalletTransaction(BaseModel):
    """钱包交易"""
    wallet_id: int = Field(..., description="钱包ID")
    transaction_type: WalletTransactionType = Field(..., description="交易类型")
    amount: Decimal = Field(..., description="交易金额")
    balance_before: Decimal = Field(..., description="交易前余额")
    balance_after: Decimal = Field(..., description="交易后余额")
    description: Optional[str] = Field(None, description="交易描述")
    reference_id: Optional[int] = Field(None, description="关联ID")
    reference_type: Optional[str] = Field(None, description="关联类型")
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class WalletTransactionCreate(BaseModel):
    """创建钱包交易"""
    transaction_type: WalletTransactionType
    amount: Decimal
    description: Optional[str] = None
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None


class WalletTransactionListResponse(BaseModel):
    """钱包交易列表响应"""
    transactions: List[WalletTransaction]
    total: int
    has_next: bool


class WalletStats(BaseModel):
    """钱包统计"""
    total_balance: Decimal = Field(default=Decimal('0'))
    total_frozen: Decimal = Field(default=Decimal('0'))
    total_mentor_points: int = 0
    total_learning_points: int = 0
    total_reputation_points: int = 0
    monthly_transactions: int = 0
    monthly_volume: Decimal = Field(default=Decimal('0'))


class PaymentRequest(BaseModel):
    """支付请求"""
    amount: Decimal = Field(..., ge=0.01, description="支付金额")
    currency: str = Field(default="CNY", description="货币类型")
    description: str = Field(..., description="支付描述")
    reference_id: Optional[int] = Field(None, description="关联ID")
    reference_type: Optional[str] = Field(None, description="关联类型")


class PaymentResponse(BaseModel):
    """支付响应"""
    transaction_id: str
    payment_url: Optional[str] = None
    status: str


class WithdrawalRequest(BaseModel):
    """提现请求"""
    amount: Decimal = Field(..., ge=0.01, description="提现金额")
    bank_account: str = Field(..., description="银行账户")
    account_name: str = Field(..., description="账户姓名")
    description: Optional[str] = Field(None, description="提现说明")
