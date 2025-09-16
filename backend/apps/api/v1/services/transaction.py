"""
交易 & 金融 - 服务层
提供订单、钱包和交易管理的业务逻辑
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from apps.schemas.transaction import (
    Order, OrderCreate, OrderUpdate,
    UserWallet, UserWalletCreate, UserWalletUpdate,
    WalletTransaction, WalletTransactionCreate
)
from apps.api.v1.repositories import transaction as transaction_repo
from libs.database.adapters import DatabaseAdapter


# ============ 订单服务 ============

async def get_orders_by_user(db: DatabaseAdapter, user_id: UUID) -> List[Order]:
    """获取用户的订单列表"""
    return await transaction_repo.get_orders_by_user(db, user_id)


async def get_order_by_id(
    db: DatabaseAdapter,
    order_id: UUID,
    user_id: UUID
) -> Optional[Order]:
    """获取订单详情"""
    return await transaction_repo.get_order_by_id(db, order_id, user_id)


async def create_order(
    db: DatabaseAdapter,
    order_data: OrderCreate
) -> Optional[Order]:
    """创建订单"""
    return await transaction_repo.create_order(db, order_data)


async def update_order(
    db: DatabaseAdapter,
    order_id: UUID,
    user_id: UUID,
    order_data: OrderUpdate
) -> Optional[Order]:
    """更新订单"""
    return await transaction_repo.update_order(db, order_id, user_id, order_data)


# ============ 钱包服务 ============

async def get_user_wallet(db: DatabaseAdapter, user_id: UUID) -> Optional[UserWallet]:
    """获取用户钱包"""
    return await transaction_repo.get_user_wallet(db, user_id)


async def create_user_wallet(
    db: DatabaseAdapter,
    wallet_data: UserWalletCreate
) -> Optional[UserWallet]:
    """创建用户钱包"""
    return await transaction_repo.create_user_wallet(db, wallet_data)


async def update_wallet_balance(
    db: DatabaseAdapter,
    user_id: UUID,
    amount: Decimal
) -> Optional[UserWallet]:
    """更新钱包余额"""
    return await transaction_repo.update_wallet_balance(db, user_id, amount)


async def deposit(
    db: DatabaseAdapter,
    user_id: UUID,
    amount: Decimal
) -> Optional[WalletTransaction]:
    """充值"""
    # 创建充值交易记录
    transaction_data = WalletTransactionCreate(
        wallet_id=await get_wallet_id_by_user(db, user_id),
        amount=amount,
        transaction_type="deposit",
        description="充值"
    )
    return await create_wallet_transaction(db, transaction_data)


async def withdraw(
    db: DatabaseAdapter,
    user_id: UUID,
    amount: Decimal
) -> Optional[WalletTransaction]:
    """提现"""
    # 检查余额是否足够
    wallet = await get_user_wallet(db, user_id)
    if not wallet or wallet.balance < amount:
        return None

    # 创建提现交易记录
    transaction_data = WalletTransactionCreate(
        wallet_id=await get_wallet_id_by_user(db, user_id),
        amount=-amount,  # 提现为负数
        transaction_type="withdraw",
        description="提现"
    )
    return await create_wallet_transaction(db, transaction_data)


async def get_wallet_id_by_user(db: DatabaseAdapter, user_id: UUID) -> UUID:
    """根据用户ID获取钱包ID"""
    wallet = await get_user_wallet(db, user_id)
    return wallet.id if wallet else None


# ============ 交易记录服务 ============

async def get_wallet_transactions(
    db: DatabaseAdapter,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20
) -> List[WalletTransaction]:
    """获取钱包交易记录"""
    return await transaction_repo.get_wallet_transactions(
        db, user_id, page, page_size
    )


async def create_wallet_transaction(
    db: DatabaseAdapter,
    transaction_data: WalletTransactionCreate
) -> Optional[WalletTransaction]:
    """创建钱包交易记录"""
    # 更新钱包余额
    await update_wallet_balance_by_transaction(
        db, transaction_data.wallet_id, transaction_data.amount
    )

    return await transaction_repo.create_wallet_transaction(db, transaction_data)


async def update_wallet_balance_by_transaction(
    db: DatabaseAdapter,
    wallet_id: UUID,
    amount: Decimal
) -> bool:
    """根据交易金额更新钱包余额"""
    return await transaction_repo.update_wallet_balance_by_id(
        db, wallet_id, amount
    )
