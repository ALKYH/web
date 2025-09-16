"""
积分日志仓库层
提供用户积分日志系统的数据库操作
统一管理所有积分相关的数据访问操作
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from apps.schemas.user_credit_logs import (
    UserCreditLog, UserCreditLogCreate, CreditTransaction, CreditTransactionCreate,
    CreditBalance, CreditStats
)
from libs.database.adapters import DatabaseAdapter
from datetime import datetime


# ============ 积分日志管理 ============

async def get_credit_log_by_id(db: DatabaseAdapter, log_id: int) -> Optional[UserCreditLog]:
    """根据ID获取积分日志"""
    query = """
        SELECT id, user_id, credit_type, amount, balance_after, reason,
               reference_id, reference_type, description, expires_at, created_at, updated_at
        FROM user_credit_logs
        WHERE id = $1
    """
    row = await db.fetch_one(query, log_id)
    return UserCreditLog(**row) if row else None


async def get_user_credit_logs(db: DatabaseAdapter, user_id: UUID, credit_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[UserCreditLog]:
    """获取用户的积分日志"""
    where_clause = "WHERE user_id = $1"
    params = [user_id]

    if credit_type:
        params.append(credit_type)
        where_clause += f" AND credit_type = ${len(params)}"

    query = f"""
        SELECT id, user_id, credit_type, amount, balance_after, reason,
               reference_id, reference_type, description, expires_at, created_at, updated_at
        FROM user_credit_logs
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    rows = await db.fetch_all(query, *params)
    return [UserCreditLog(**row) for row in rows]


async def create_credit_log(db: DatabaseAdapter, log: UserCreditLogCreate) -> Optional[UserCreditLog]:
    """创建积分日志"""
    query = """
        INSERT INTO user_credit_logs (
            user_id, credit_type, amount, balance_after, reason,
            reference_id, reference_type, description, expires_at, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        RETURNING id, user_id, credit_type, amount, balance_after, reason,
                  reference_id, reference_type, description, expires_at, created_at, updated_at
    """
    values = (
        log.user_id, log.credit_type, log.amount, log.balance_after,
        log.reason, log.reference_id, log.reference_type, log.description, log.expires_at
    )
    row = await db.fetch_one(query, *values)
    return UserCreditLog(**row) if row else None


async def create_credit_transaction(db: DatabaseAdapter, transaction: CreditTransactionCreate) -> Optional[UserCreditLog]:
    """创建积分交易（同时更新用户钱包）"""
    # 获取当前余额
    wallet_query = """
        SELECT mentor_points, learning_points, reputation_points
        FROM user_wallets
        WHERE user_id = $1
    """
    wallet = await db.fetch_one(wallet_query, transaction.user_id)

    if not wallet:
        # 如果没有钱包记录，创建默认钱包
        await db.execute("""
            INSERT INTO user_wallets (user_id, created_at, updated_at)
            VALUES ($1, NOW(), NOW())
        """, transaction.user_id)
        wallet = {'mentor_points': 0, 'learning_points': 0, 'reputation_points': 0}

    # 计算新余额
    credit_type_field = f"{transaction.credit_type}s"  # mentor_points, learning_points, reputation_points
    new_balance = wallet[credit_type_field] + transaction.amount

    # 更新钱包
    update_wallet_query = f"""
        UPDATE user_wallets
        SET {credit_type_field} = {credit_type_field} + $1, updated_at = NOW()
        WHERE user_id = $2
    """
    await db.execute(update_wallet_query, transaction.amount, transaction.user_id)

    # 创建日志
    log_data = UserCreditLogCreate(
        user_id=transaction.user_id,
        credit_type=transaction.credit_type,
        amount=transaction.amount,
        balance_after=new_balance,
        reason='system_transaction',
        description=transaction.description,
        reference_id=transaction.reference_id,
        reference_type=transaction.reference_type,
        expires_at=getattr(transaction, 'expires_at', None)
    )

    return await create_credit_log(db, log_data)


async def get_credit_balance(db: DatabaseAdapter, user_id: UUID) -> CreditBalance:
    """获取用户的积分余额"""
    query = """
        SELECT user_id, mentor_points, learning_points, reputation_points,
               mentor_points + learning_points + reputation_points as total_earned,
               updated_at as last_updated
        FROM user_wallets
        WHERE user_id = $1
    """
    result = await db.fetch_one(query, user_id)
    if not result:
        # 如果没有钱包记录，返回默认值
        return CreditBalance(
            user_id=user_id,
            total_earned=0,
            total_spent=0,
            current_balance=0,
            last_updated=datetime.now()
        )

    # 这里简化了，实际应该分别计算赚取和消费的积分
    return CreditBalance(
        user_id=result['user_id'],
        total_earned=result['total_earned'],
        total_spent=0,  # 简化处理
        current_balance=result['total_earned'],
        last_updated=result['last_updated']
    )


async def get_expiring_credits(db: DatabaseAdapter, user_id: UUID, days: int = 30) -> List[UserCreditLog]:
    """获取即将过期的积分"""
    query = f"""
        SELECT id, user_id, credit_type, amount, balance_after, reason,
               reference_id, reference_type, description, expires_at, created_at, updated_at
        FROM user_credit_logs
        WHERE user_id = $1
        AND amount > 0
        AND expires_at IS NOT NULL
        AND expires_at <= NOW() + INTERVAL '{days} days'
        AND expires_at > NOW()
        ORDER BY expires_at
    """
    rows = await db.fetch_all(query, user_id)
    return [UserCreditLog(**row) for row in rows]


async def expire_credits(db: DatabaseAdapter) -> int:
    """过期积分处理"""
    # 找到过期的积分日志
    expired_logs_query = """
        SELECT id, user_id, credit_type, amount
        FROM user_credit_logs
        WHERE expires_at IS NOT NULL
        AND expires_at <= NOW()
        AND amount > 0
    """
    expired_logs = await db.fetch_all(expired_logs_query)

    if not expired_logs:
        return 0

    # 批量处理过期积分
    for log in expired_logs:
        credit_type_field = f"{log['credit_type']}s"

        # 扣除过期积分
        update_wallet_query = f"""
            UPDATE user_wallets
            SET {credit_type_field} = GREATEST({credit_type_field} - $1, 0), updated_at = NOW()
            WHERE user_id = $2
        """
        await db.execute(update_wallet_query, log['amount'], log['user_id'])

        # 创建过期日志
        await create_credit_log(db, UserCreditLogCreate(
            user_id=log['user_id'],
            credit_type=log['credit_type'],
            amount=-log['amount'],
            balance_after=0,
            reason='expiration',
            reference_id=str(log['id']),
            reference_type='expired_log',
            description=f'积分过期：{log["amount"]} {log["credit_type"]}'
        ))

    # 标记原日志为已过期
    expired_ids = [log['id'] for log in expired_logs]
    for log_id in expired_ids:
        await db.execute("""
            UPDATE user_credit_logs
            SET amount = 0, description = description || ' (已过期)', updated_at = NOW()
            WHERE id = $1
        """, log_id)

    return len(expired_logs)


async def get_credit_stats(db: DatabaseAdapter, user_id: Optional[UUID] = None) -> CreditStats:
    """获取积分统计"""
    if user_id:
        # 用户个人统计
        query = """
            SELECT
                COUNT(CASE WHEN amount > 0 THEN 1 END) as total_earned,
                COUNT(CASE WHEN amount < 0 THEN 1 END) as total_spent,
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as total_earned_amount,
                COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) as total_spent_amount,
                COUNT(*) as transaction_count,
                MAX(created_at) as last_transaction_date
            FROM user_credit_logs
            WHERE user_id = $1
        """
        result = await db.fetch_one(query, user_id)
        balance = await get_credit_balance(db, user_id)

        if result:
            return CreditStats(
                user_id=user_id,
                total_earned=result['total_earned_amount'],
                total_spent=result['total_spent_amount'],
                total_bonus=0,  # 简化处理
                total_refund=0,  # 简化处理
                current_balance=balance.current_balance,
                transaction_count=result['transaction_count'],
                last_transaction_date=result['last_transaction_date']
            )
        else:
            return CreditStats(
                user_id=user_id,
                total_earned=0,
                total_spent=0,
                total_bonus=0,
                total_refund=0,
                current_balance=0,
                transaction_count=0,
                last_transaction_date=None
            )
    else:
        # 全局统计
        query = """
            SELECT
                COUNT(DISTINCT user_id) as active_users,
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as total_credits_issued,
                COUNT(*) as total_transactions
            FROM user_credit_logs
        """
        result = await db.fetch_one(query)
        # 返回简化版本的全局统计
        return CreditStats(
            user_id=UUID('00000000-0000-0000-0000-000000000000'),  # 虚拟用户ID用于全局统计
            total_earned=result['total_credits_issued'] if result else 0,
            total_spent=0,
            total_bonus=0,
            total_refund=0,
            current_balance=0,
            transaction_count=result['total_transactions'] if result else 0,
            last_transaction_date=None
        )
