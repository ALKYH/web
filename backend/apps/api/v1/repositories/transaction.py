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
        SELECT id, user_id, service_id, total_price as amount, status, created_at, updated_at
        FROM orders
        WHERE user_id = $1
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
        SELECT id, user_id, service_id, total_price as amount, status, created_at, updated_at
        FROM orders
        WHERE id = $1 AND user_id = $2
    """
    row = await db.fetch_one(query, order_id, user_id)
    return Order(**row) if row else None


async def create_order(db: DatabaseAdapter, order_data: OrderCreate) -> Optional[Order]:
    """创建订单"""
    query = """
        INSERT INTO orders (user_id, service_id, total_price, status)
        VALUES ($1, $2, $3, $4)
        RETURNING id, user_id, service_id, total_price as amount, status, created_at, updated_at
    """
    values = (
        order_data.user_id,
        order_data.service_id,
        order_data.total_price,
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

    if not set_parts:
        return await get_order_by_id(db, order_id, user_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE orders
        SET {', '.join(set_parts)}
        WHERE id = ${param_index} AND user_id = ${param_index + 1}
        RETURNING id, user_id, service_id, total_price as amount, status, created_at, updated_at
    """
    values.extend([order_id, user_id])

    row = await db.fetch_one(query, *values)
    return Order(**row) if row else None


# ============ 钱包仓库操作 ============

async def get_user_wallet(db: DatabaseAdapter, user_id: UUID) -> Optional[UserWallet]:
    """获取用户钱包"""
    query = """
        SELECT id, user_id, balance, created_at, updated_at
        FROM user_wallets
        WHERE user_id = $1
    """
    row = await db.fetch_one(query, user_id)
    return UserWallet(**row) if row else None


async def create_user_wallet(
    db: DatabaseAdapter,
    wallet_data: UserWalletCreate
) -> Optional[UserWallet]:
    """创建用户钱包"""
    query = """
        INSERT INTO user_wallets (user_id, balance)
        VALUES ($1, $2)
        RETURNING id, user_id, balance, created_at, updated_at
    """
    values = (
        wallet_data.user_id,
        wallet_data.balance
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
        WHERE user_id = $2
        RETURNING id, user_id, balance, created_at, updated_at
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
        WHERE id = $2
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


async def cancel_order(
    db: DatabaseAdapter,
    order_id: UUID,
    user_id: UUID
) -> bool:
    """取消订单"""
    query = """
        UPDATE orders
        SET status = 'cancelled', updated_at = NOW()
        WHERE id = $1 AND user_id = $2 AND status = 'pending'
    """
    result = await db.execute(query, order_id, user_id)
    return result == "UPDATE 1"


async def update_user_wallet(
    db: DatabaseAdapter,
    wallet_data: UserWalletUpdate,
    user_id: UUID
) -> Optional[UserWallet]:
    """更新用户钱包"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if wallet_data.balance is not None:
        set_parts.append(f"balance = ${param_index}")
        values.append(wallet_data.balance)
        param_index += 1

    if not set_parts:
        return await get_user_wallet(db, user_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE user_wallets
        SET {', '.join(set_parts)}
        WHERE user_id = $%d
        RETURNING id, user_id, balance, created_at, updated_at
    """ % param_index
    values.append(user_id)

    row = await db.fetch_one(query, *values)
    return UserWallet(**row) if row else None


async def get_financial_stats(db: DatabaseAdapter, user_id: UUID) -> dict:
    """获取财务统计信息"""
    # 获取总收入（作为导师的服务被购买）
    income_query = """
        SELECT COALESCE(SUM(o.total_price), 0) as total_income
        FROM orders o
        JOIN services s ON o.service_id = s.id
        WHERE s.mentor_id = $1 AND o.status = 'completed'
    """
    income_row = await db.fetch_one(income_query, user_id)
    total_income = income_row['total_income'] if income_row else 0

    # 获取总支出（作为买家购买服务）
    expense_query = """
        SELECT COALESCE(SUM(total_price), 0) as total_expense
        FROM orders
        WHERE user_id = $1 AND status = 'completed'
    """
    expense_row = await db.fetch_one(expense_query, user_id)
    total_expense = expense_row['total_expense'] if expense_row else 0

    # 获取钱包余额
    wallet = await get_user_wallet(db, user_id)
    balance = wallet.balance if wallet else 0

    # 获取交易统计
    transaction_stats_query = """
        SELECT
            COUNT(*) as total_transactions,
            COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as total_deposits,
            COALESCE(SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END), 0) as total_withdrawals
        FROM wallet_transactions wt
        JOIN user_wallets uw ON wt.wallet_id = uw.id
        WHERE uw.user_id = $1
    """
    stats_row = await db.fetch_one(transaction_stats_query, user_id)
    transaction_stats = stats_row if stats_row else {
        'total_transactions': 0,
        'total_deposits': 0,
        'total_withdrawals': 0
    }

    return {
        'balance': float(balance),
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'net_income': float(total_income - total_expense),
        'total_transactions': transaction_stats['total_transactions'],
        'total_deposits': float(transaction_stats['total_deposits']),
        'total_withdrawals': float(transaction_stats['total_withdrawals'])
    }


async def pay_order(
    db: DatabaseAdapter,
    order_id: UUID,
    user_id: UUID
) -> tuple[bool, str]:
    """支付订单"""
    # 获取订单信息和导师ID
    order_query = """
        SELECT o.id, o.user_id, o.total_price, o.status, s.mentor_id
        FROM orders o
        JOIN services s ON o.service_id = s.id
        WHERE o.id = $1 AND o.user_id = $2
    """
    order_row = await db.fetch_one(order_query, order_id, user_id)
    if not order_row:
        return False, "订单不存在"

    if order_row['status'] != 'pending':
        return False, f"订单状态为 {order_row['status']}，无法支付"

    order_amount = order_row['total_price']
    mentor_id = order_row['mentor_id']

    # 获取用户钱包
    wallet = await get_user_wallet(db, user_id)
    if not wallet:
        return False, "用户钱包不存在"

    if wallet.balance < order_amount:
        return False, f"钱包余额不足，当前余额: {wallet.balance}"

    # 开始事务处理
    try:
        # 扣除买家钱包余额
        await update_wallet_balance(db, user_id, -order_amount)

        # 增加导师钱包余额
        await update_wallet_balance(db, mentor_id, order_amount)

        # 更新订单状态
        update_order_query = """
            UPDATE orders
            SET status = 'completed', updated_at = NOW()
            WHERE id = $1
        """
        await db.execute(update_order_query, order_id)

        # 创建交易记录（买家支出）
        buyer_transaction = WalletTransactionCreate(
            wallet_id=wallet.id,
            amount=-order_amount,
            transaction_type="payment",
            description=f"支付订单 {order_id}"
        )
        await create_wallet_transaction(db, buyer_transaction)

        # 创建交易记录（导师收入）
        mentor_wallet = await get_user_wallet(db, mentor_id)
        if mentor_wallet:
            mentor_transaction = WalletTransactionCreate(
                wallet_id=mentor_wallet.id,
                amount=order_amount,
                transaction_type="income",
                description=f"收到订单 {order_id} 付款"
            )
            await create_wallet_transaction(db, mentor_transaction)

        return True, "支付成功"

    except Exception as e:
        # 回滚事务的逻辑应该在数据库层面处理，这里简化处理
        return False, f"支付失败: {str(e)}"


async def recharge_wallet(
    db: DatabaseAdapter,
    amount: Decimal,
    payment_method: str,
    user_id: UUID
) -> Optional[WalletTransaction]:
    """充值钱包"""
    wallet = await get_user_wallet(db, user_id)
    if not wallet:
        return None

    # 更新钱包余额
    await update_wallet_balance(db, user_id, amount)

    # 创建充值交易记录
    transaction_data = WalletTransactionCreate(
        wallet_id=wallet.id,
        amount=amount,
        transaction_type="deposit",
        description=f"充值 ({payment_method})"
    )

    return await create_wallet_transaction(db, transaction_data)


async def withdraw_wallet(
    db: DatabaseAdapter,
    amount: Decimal,
    account_info: str,
    user_id: UUID
) -> Optional[WalletTransaction]:
    """提现钱包"""
    wallet = await get_user_wallet(db, user_id)
    if not wallet:
        return None

    if wallet.balance < amount:
        return None

    # 更新钱包余额
    await update_wallet_balance(db, user_id, -amount)

    # 创建提现交易记录
    transaction_data = WalletTransactionCreate(
        wallet_id=wallet.id,
        amount=-amount,
        transaction_type="withdraw",
        description=f"提现到 {account_info}"
    )

    return await create_wallet_transaction(db, transaction_data)
