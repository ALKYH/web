"""
用户积分日志系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_credit_logs import UserCreditLogCreate, CreditTransaction
from libs.database.adapters import DatabaseAdapter
from datetime import datetime


async def get_credit_log_by_id(db: DatabaseAdapter, log_id: int) -> Optional[Dict]:
    """根据ID获取积分日志"""
    query = """
        SELECT ucl.*, u.username as user_username, u.avatar_url as user_avatar
        FROM user_credit_logs ucl
        JOIN users u ON ucl.user_id = u.id
        WHERE ucl.id = $1
    """
    return await db.fetch_one(query, log_id)


async def get_user_credit_logs(db: DatabaseAdapter, user_id: int, credit_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的积分日志"""
    where_clause = "WHERE ucl.user_id = $1"
    params = [user_id]

    if credit_type:
        where_clause += " AND ucl.credit_type = $2"
        params.append(credit_type)

    query = f"""
        SELECT ucl.*, u.username as user_username, u.avatar_url as user_avatar
        FROM user_credit_logs ucl
        JOIN users u ON ucl.user_id = u.id
        {where_clause}
        ORDER BY ucl.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_credit_log(db: DatabaseAdapter, log: UserCreditLogCreate) -> Optional[Dict]:
    """创建积分日志"""
    query = """
        INSERT INTO user_credit_logs (
            user_id, credit_type, amount, balance_after, reason,
            reference_id, reference_type, description, expires_at, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
        RETURNING *
    """
    values = (
        log.user_id, log.credit_type, log.amount, log.balance_after,
        log.reason, log.reference_id, log.reference_type, log.description, log.expires_at
    )
    return await db.fetch_one(query, *values)


async def create_credit_transaction(db: DatabaseAdapter, transaction: CreditTransaction) -> Optional[Dict]:
    """创建积分交易（同时更新用户钱包）"""
    async with db.connection.transaction():
        # 获取当前余额
        wallet_query = """
            SELECT mentoring_points, learning_points, reputation_points
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
            wallet = {'mentoring_points': 0, 'learning_points': 0, 'reputation_points': 0}

        # 计算新余额
        if transaction.credit_type == 'mentoring_points':
            new_balance = wallet['mentoring_points'] + transaction.amount
        elif transaction.credit_type == 'learning_points':
            new_balance = wallet['learning_points'] + transaction.amount
        elif transaction.credit_type == 'reputation_points':
            new_balance = wallet['reputation_points'] + transaction.amount
        else:
            new_balance = 0

        # 更新钱包
        update_wallet_query = f"""
            UPDATE user_wallets
            SET {transaction.credit_type} = {transaction.credit_type} + $1, updated_at = NOW()
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
            expires_at=transaction.expires_at
        )

        return await create_credit_log(db, log_data)


async def get_credit_balance(db: DatabaseAdapter, user_id: int) -> Dict[str, Any]:
    """获取用户的积分余额"""
    query = """
        SELECT mentoring_points, learning_points, reputation_points,
               mentoring_points + learning_points + reputation_points as total_points
        FROM user_wallets
        WHERE user_id = $1
    """
    result = await db.fetch_one(query, user_id)
    if not result:
        return {
            'mentoring_points': 0,
            'learning_points': 0,
            'reputation_points': 0,
            'total_points': 0
        }
    return result


async def get_expiring_credits(db: DatabaseAdapter, user_id: int, days: int = 30) -> List[Dict]:
    """获取即将过期的积分"""
    query = """
        SELECT *
        FROM user_credit_logs
        WHERE user_id = $1
        AND amount > 0
        AND expires_at IS NOT NULL
        AND expires_at <= NOW() + INTERVAL '%s days'
        AND expires_at > NOW()
        ORDER BY expires_at
    """ % days
    return await db.fetch_all(query, user_id)


async def expire_credits(db: DatabaseAdapter) -> int:
    """过期积分处理"""
    async with db.connection.transaction():
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

        # 批量扣除过期积分
        for log in expired_logs:
            update_wallet_query = f"""
                UPDATE user_wallets
                SET {log['credit_type']} = GREATEST({log['credit_type']} - $1, 0), updated_at = NOW()
                WHERE user_id = $2
            """
            await db.execute(update_wallet_query, log['amount'], log['user_id'])

            # 创建过期日志
            await create_credit_log(db, UserCreditLogCreate(
                user_id=log['user_id'],
                credit_type=log['credit_type'],
                amount=-log['amount'],
                balance_after=0,  # 临时值，实际会在create_credit_log中重新计算
                reason='expiration',
                reference_id=log['id'],
                reference_type='expired_log',
                description=f'积分过期：{log["amount"]} {log["credit_type"]}'
            ))

        # 标记原日志为已过期
        expired_ids = [log['id'] for log in expired_logs]
        await db.execute_many("""
            UPDATE user_credit_logs
            SET amount = 0, description = description || ' (已过期)'
            WHERE id = $1
        """, [(log_id,) for log_id in expired_ids])

        return len(expired_logs)


async def get_credit_stats(db: DatabaseAdapter, user_id: Optional[int] = None) -> Dict[str, Any]:
    """获取积分统计"""
    if user_id:
        # 用户个人统计
        query = """
            SELECT
                COUNT(CASE WHEN amount > 0 THEN 1 END) as total_earned,
                COUNT(CASE WHEN amount < 0 THEN 1 END) as total_spent,
                COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) as total_earned_amount,
                COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) as total_spent_amount,
                MAX(created_at) as last_activity
            FROM user_credit_logs
            WHERE user_id = $1
        """
        result = await db.fetch_one(query, user_id)
        balance = await get_credit_balance(db, user_id)
        return {**result, **balance} if result else balance
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
        return result or {}
