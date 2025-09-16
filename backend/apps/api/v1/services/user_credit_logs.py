"""
用户积分日志服务层
处理用户积分相关的业务逻辑
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status

from apps.schemas.user_credit_logs import CreditTransaction, CreditBalance, CreditStats
from apps.api.v1.repositories import user_credit_logs as credit_repo
from libs.database.adapters import DatabaseAdapter


async def get_user_credit_balance(db: DatabaseAdapter, user_id: UUID) -> CreditBalance:
    """
    获取用户积分余额
    """
    balance = await credit_repo.get_credit_balance(db, user_id)
    return CreditBalance(**balance)


async def get_user_credit_logs(db: DatabaseAdapter, user_id: UUID, credit_type: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """
    获取用户积分日志
    """
    return await credit_repo.get_user_credit_logs(db, user_id, credit_type, skip, limit)


async def award_credits(db: DatabaseAdapter, transaction: CreditTransaction) -> bool:
    """
    奖励积分
    """
    result = await credit_repo.create_credit_transaction(db, transaction)
    return result is not None


async def get_credit_stats(db: DatabaseAdapter, user_id: Optional[UUID] = None) -> CreditStats:
    """
    获取积分统计
    """
    stats = await credit_repo.get_credit_stats(db, user_id)
    return CreditStats(**stats)
