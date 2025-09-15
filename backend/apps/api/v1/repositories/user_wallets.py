"""
用户钱包系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_wallets import UserWalletCreate, UserWalletUpdate, WalletTransactionCreate
from libs.database.adapters import DatabaseAdapter
from datetime import datetime


async def get_wallet_by_user_id(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """根据用户ID获取钱包"""
    query = """
        SELECT uw.*, u.username, u.email, u.avatar_url
        FROM user_wallets uw
        JOIN users u ON uw.user_id = u.id
        WHERE uw.user_id = $1
    """
    return await db.fetch_one(query, user_id)


async def create_wallet(db: DatabaseAdapter, wallet: UserWalletCreate) -> Optional[Dict]:
    """创建用户钱包"""
    query = """
        INSERT INTO user_wallets (
            user_id, balance, frozen_balance, currency, mentor_points,
            learning_points, reputation_points, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        RETURNING *
    """
    values = (
        wallet.user_id, wallet.balance, wallet.frozen_balance, wallet.currency,
        wallet.mentor_points, wallet.learning_points, wallet.reputation_points
    )
    return await db.fetch_one(query, *values)


async def update_wallet(db: DatabaseAdapter, user_id: int, wallet: UserWalletUpdate) -> Optional[Dict]:
    """更新用户钱包"""
    update_data = wallet.model_dump(exclude_unset=True)
    if not update_data:
        return await get_wallet_by_user_id(db, user_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_wallets SET {set_clause}, updated_at = NOW()
        WHERE user_id = $1
        RETURNING *
    """
    return await db.fetch_one(query, user_id, *update_data.values())


async def ensure_wallet_exists(db: DatabaseAdapter, user_id: int) -> Dict[str, Any]:
    """确保用户钱包存在，如果不存在则创建"""
    wallet = await get_wallet_by_user_id(db, user_id)
    if not wallet:
        default_wallet = UserWalletCreate(user_id=user_id)
        wallet = await create_wallet(db, default_wallet)
    return wallet


async def add_wallet_transaction(db: DatabaseAdapter, transaction: WalletTransactionCreate) -> Optional[Dict]:
    """添加钱包交易记录"""
    # 确保钱包存在
    await ensure_wallet_exists(db, transaction.user_id)

    async with db.connection.transaction():
        # 创建交易记录
        query = """
            INSERT INTO wallet_transactions (
                wallet_id, transaction_type, amount, balance_before, balance_after,
                description, reference_id, reference_type, created_at
            )
            SELECT uw.id, $2, $3, uw.balance, uw.balance + $3, $4, $5, $6, NOW()
            FROM user_wallets uw
            WHERE uw.user_id = $1
            RETURNING *
        """
        values = (
            transaction.user_id, transaction.transaction_type, transaction.amount,
            transaction.description, transaction.reference_id, transaction.reference_type
        )
        result = await db.fetch_one(query, *values)

        if result:
            # 更新钱包余额
            update_query = """
                UPDATE user_wallets
                SET balance = balance + $1, updated_at = NOW()
                WHERE user_id = $2
            """
            await db.execute(update_query, transaction.amount, transaction.user_id)

        return result


async def get_wallet_transactions(db: DatabaseAdapter, user_id: int, transaction_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取钱包交易记录"""
    where_clause = "WHERE uw.user_id = $1"
    params = [user_id]

    if transaction_type:
        params.append(transaction_type)
        where_clause += f" AND wt.transaction_type = ${len(params)}"

    query = f"""
        SELECT wt.*, uw.currency
        FROM wallet_transactions wt
        JOIN user_wallets uw ON wt.wallet_id = uw.id
        {where_clause}
        ORDER BY wt.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def update_wallet_balance(db: DatabaseAdapter, user_id: int, amount: float, description: str = "") -> Optional[Dict]:
    """更新钱包余额"""
    wallet = await ensure_wallet_exists(db, user_id)

    async with db.connection.transaction():
        # 创建交易记录
        transaction = WalletTransactionCreate(
            transaction_type="deposit" if amount > 0 else "withdrawal",
            amount=amount,
            description=description or f"余额{'增加' if amount > 0 else '减少'} {abs(amount)}"
        )
        await add_wallet_transaction(db, transaction)

        # 返回更新后的钱包
        return await get_wallet_by_user_id(db, user_id)


async def freeze_balance(db: DatabaseAdapter, user_id: int, amount: float, description: str = "") -> bool:
    """冻结余额"""
    wallet = await get_wallet_by_user_id(db, user_id)
    if not wallet or wallet['balance'] < amount:
        return False

    async with db.connection.transaction():
        # 减少可用余额
        await db.execute("""
            UPDATE user_wallets
            SET balance = balance - $1, frozen_balance = frozen_balance + $1, updated_at = NOW()
            WHERE user_id = $2 AND balance >= $1
        """, amount, user_id)

        # 记录冻结交易
        transaction = WalletTransactionCreate(
            transaction_type="freeze",
            amount=-amount,
            description=description or f"冻结金额 {amount}"
        )
        await add_wallet_transaction(db, transaction)

    return True


async def unfreeze_balance(db: DatabaseAdapter, user_id: int, amount: float, description: str = "") -> bool:
    """解冻余额"""
    wallet = await get_wallet_by_user_id(db, user_id)
    if not wallet or wallet['frozen_balance'] < amount:
        return False

    async with db.connection.transaction():
        # 增加可用余额
        await db.execute("""
            UPDATE user_wallets
            SET balance = balance + $1, frozen_balance = frozen_balance - $1, updated_at = NOW()
            WHERE user_id = $2 AND frozen_balance >= $1
        """, amount, user_id)

        # 记录解冻交易
        transaction = WalletTransactionCreate(
            transaction_type="unfreeze",
            amount=amount,
            description=description or f"解冻金额 {amount}"
        )
        await add_wallet_transaction(db, transaction)

    return True


async def transfer_balance(db: DatabaseAdapter, from_user_id: int, to_user_id: int, amount: float, description: str = "") -> bool:
    """转账"""
    from_wallet = await get_wallet_by_user_id(db, from_user_id)
    if not from_wallet or from_wallet['balance'] < amount:
        return False

    async with db.connection.transaction():
        # 确保目标用户钱包存在
        await ensure_wallet_exists(db, to_user_id)

        # 从源用户扣款
        transaction_out = WalletTransactionCreate(
            transaction_type="transfer",
            amount=-amount,
            description=description or f"转账给用户 {to_user_id}",
            reference_id=to_user_id,
            reference_type="transfer_out"
        )
        await add_wallet_transaction(db, transaction_out)

        # 给目标用户加款
        transaction_in = WalletTransactionCreate(
            transaction_type="transfer",
            amount=amount,
            description=description or f"收到来自用户 {from_user_id} 的转账",
            reference_id=from_user_id,
            reference_type="transfer_in"
        )
        await add_wallet_transaction(db, transaction_in)

    return True


async def get_wallet_stats(db: DatabaseAdapter, user_id: Optional[int] = None) -> Dict[str, Any]:
    """获取钱包统计"""
    if user_id:
        # 用户钱包统计
        query = """
            SELECT
                uw.balance, uw.frozen_balance, uw.mentor_points, uw.learning_points, uw.reputation_points,
                COUNT(wt.id) as total_transactions,
                COUNT(CASE WHEN wt.transaction_type = 'deposit' THEN 1 END) as deposit_count,
                COUNT(CASE WHEN wt.transaction_type = 'withdrawal' THEN 1 END) as withdrawal_count,
                COALESCE(SUM(CASE WHEN wt.transaction_type = 'deposit' THEN wt.amount ELSE 0 END), 0) as total_deposits,
                COALESCE(SUM(CASE WHEN wt.transaction_type = 'withdrawal' THEN -wt.amount ELSE 0 END), 0) as total_withdrawals
            FROM user_wallets uw
            LEFT JOIN wallet_transactions wt ON uw.id = wt.wallet_id
            WHERE uw.user_id = $1
            GROUP BY uw.id, uw.balance, uw.frozen_balance, uw.mentor_points, uw.learning_points, uw.reputation_points
        """
        result = await db.fetch_one(query, user_id)
    else:
        # 全局钱包统计
        query = """
            SELECT
                COUNT(*) as total_wallets,
                SUM(balance) as total_balance,
                SUM(frozen_balance) as total_frozen_balance,
                AVG(balance) as avg_balance,
                COUNT(CASE WHEN balance > 0 THEN 1 END) as wallets_with_balance,
                MAX(balance) as max_balance
            FROM user_wallets
        """
        result = await db.fetch_one(query)

    return result or {}


async def process_payment(db: DatabaseAdapter, from_user_id: int, to_user_id: int, amount: float, service_description: str = "", reference_id: Optional[int] = None) -> bool:
    """处理支付"""
    from_wallet = await get_wallet_by_user_id(db, from_user_id)
    if not from_wallet or from_wallet['balance'] < amount:
        return False

    async with db.connection.transaction():
        # 扣除付款方金额
        payment_transaction = WalletTransactionCreate(
            transaction_type="payment",
            amount=-amount,
            description=service_description or "服务支付",
            reference_id=reference_id,
            reference_type="service_payment"
        )
        await add_wallet_transaction(db, payment_transaction)

        # 增加收款方金额
        income_transaction = WalletTransactionCreate(
            transaction_type="income",
            amount=amount,
            description=service_description or "收到服务费",
            reference_id=reference_id,
            reference_type="service_income"
        )
        await add_wallet_transaction(db, income_transaction)

    return True
