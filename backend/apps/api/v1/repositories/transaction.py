"""
交易 & 金融 - 仓库层
提供订单、钱包和交易记录的数据库操作
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from apps.schemas.transaction import (
    Order, OrderCreate, OrderUpdate,
    UserWallet, UserWalletCreate, UserWalletUpdate,
    WalletTransaction, WalletTransactionCreate
)
from libs.database.adapters import DatabaseAdapter


# ============ 订单仓库操作 ============

async def get_orders_by_user(db: DatabaseAdapter, user_id: UUID) -> List[Order]:
    """获取用户的订单列表"""
    query = """
        SELECT id, buyer_id, seller_id, service_id, amount, status, created_at, updated_at
        FROM orders
        WHERE buyer_id = $1 OR seller_id = $1
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, user_id)
    return [Order(**row) for row in rows]


async def get_order_by_id(
    db: DatabaseAdapter,
    order_id: UUID,
    user_id: UUID
) -> Optional[Order]:
    """获取订单详情"""
    query = """
        SELECT id, buyer_id, seller_id, service_id, amount, status, created_at, updated_at
        FROM orders
        WHERE id = $1 AND (buyer_id = $2 OR seller_id = $2)
    """
    row = await db.fetch_one(query, order_id, user_id)
    return Order(**row) if row else None


async def create_order(db: DatabaseAdapter, order_data: OrderCreate) -> Optional[Order]:
    """创建订单"""
    query = """
        INSERT INTO orders (buyer_id, seller_id, service_id, amount, status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, buyer_id, seller_id, service_id, amount, status, created_at, updated_at
    """
    values = (
        order_data.buyer_id,
        order_data.seller_id,
        order_data.service_id,
        order_data.amount,
        order_data.status.value if hasattr(order_data.status, 'value') else order_data.status
    )
    row = await db.fetch_one(query, *values)
    return Order(**row) if row else None


async def update_order(
    db: DatabaseAdapter,
    order_id: UUID,
    user_id: UUID,
    order_data: OrderUpdate
) -> Optional[Order]:
    """更新订单"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if order_data.status is not None:
        set_parts.append(f"status = ${param_index}")
        values.append(order_data.status.value if hasattr(order_data.status, 'value') else order_data.status)
        param_index += 1

    if order_data.amount is not None:
        set_parts.append(f"amount = ${param_index}")
        values.append(order_data.amount)
        param_index += 1

    if not set_parts:
        return await get_order_by_id(db, order_id, user_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE orders
        SET {', '.join(set_parts)}
        WHERE id = ${param_index} AND (buyer_id = ${param_index + 1} OR seller_id = ${param_index + 1})
        RETURNING id, buyer_id, seller_id, service_id, amount, status, created_at, updated_at
    """
    values.extend([order_id, user_id])

    row = await db.fetch_one(query, *values)
    return Order(**row) if row else None


# ============ 钱包仓库操作 ============

async def get_user_wallet(db: DatabaseAdapter, user_id: UUID) -> Optional[UserWallet]:
    """获取用户钱包"""
    query = """
        SELECT id, user_id, balance, currency, is_active, created_at, updated_at
        FROM user_wallets
        WHERE user_id = $1 AND is_active = true
    """
    row = await db.fetch_one(query, user_id)
    return UserWallet(**row) if row else None


async def create_user_wallet(
    db: DatabaseAdapter,
    wallet_data: UserWalletCreate
) -> Optional[UserWallet]:
    """创建用户钱包"""
    query = """
        INSERT INTO user_wallets (user_id, balance, currency, is_active)
        VALUES ($1, $2, $3, $4)
        RETURNING id, user_id, balance, currency, is_active, created_at, updated_at
    """
    values = (
        wallet_data.user_id,
        wallet_data.balance,
        wallet_data.currency,
        wallet_data.is_active
    )
    row = await db.fetch_one(query, *values)
    return UserWallet(**row) if row else None


async def update_wallet_balance(
    db: DatabaseAdapter,
    user_id: UUID,
    amount: Decimal
) -> Optional[UserWallet]:
    """更新钱包余额"""
    query = """
        UPDATE user_wallets
        SET balance = balance + $1, updated_at = NOW()
        WHERE user_id = $2 AND is_active = true
        RETURNING id, user_id, balance, currency, is_active, created_at, updated_at
    """
    row = await db.fetch_one(query, amount, user_id)
    return UserWallet(**row) if row else None


async def update_wallet_balance_by_id(
    db: DatabaseAdapter,
    wallet_id: UUID,
    amount: Decimal
) -> bool:
    """根据钱包ID更新余额"""
    query = """
        UPDATE user_wallets
        SET balance = balance + $1, updated_at = NOW()
        WHERE id = $2 AND is_active = true
    """
    result = await db.execute(query, amount, wallet_id)
    return result == "UPDATE 1"


# ============ 交易记录仓库操作 ============

async def get_wallet_transactions(
    db: DatabaseAdapter,
    user_id: UUID,
    page: int = 1,
    page_size: int = 20
) -> List[WalletTransaction]:
    """获取钱包交易记录"""
    offset = (page - 1) * page_size
    query = """
        SELECT wt.id, wt.wallet_id, wt.amount, wt.transaction_type, wt.balance_after, wt.created_at, wt.updated_at
        FROM wallet_transactions wt
        JOIN user_wallets uw ON wt.wallet_id = uw.id
        WHERE uw.user_id = $1
        ORDER BY wt.created_at DESC
        LIMIT $2 OFFSET $3
    """
    rows = await db.fetch_all(query, user_id, page_size, offset)
    return [WalletTransaction(**row) for row in rows]


async def create_wallet_transaction(
    db: DatabaseAdapter,
    transaction_data: WalletTransactionCreate
) -> Optional[WalletTransaction]:
    """创建钱包交易记录"""
    query = """
        INSERT INTO wallet_transactions (wallet_id, amount, transaction_type, description)
        VALUES ($1, $2, $3, $4)
        RETURNING id, wallet_id, amount, transaction_type, description, created_at
    """
    values = (
        transaction_data.wallet_id,
        transaction_data.amount,
        transaction_data.transaction_type,
        transaction_data.description
    )
    row = await db.fetch_one(query, *values)
    return WalletTransaction(**row) if row else None
