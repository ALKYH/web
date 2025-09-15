"""
用户钱包服务层
处理用户钱包相关的业务逻辑
"""
from typing import Optional, List
from fastapi import HTTPException, status

from apps.schemas.user_wallets import (
    UserWalletDetail, WalletTransactionCreate, PaymentRequest
)
from apps.api.v1.repositories import user_wallets as wallets_repo
from libs.database.adapters import DatabaseAdapter


async def get_user_wallet(db: DatabaseAdapter, user_id: int) -> UserWalletDetail:
    """
    获取用户钱包
    """
    wallet = await wallets_repo.get_wallet_by_user_id(db, user_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="钱包不存在"
        )

    return UserWalletDetail(**wallet)


async def update_wallet_balance(db: DatabaseAdapter, user_id: int, amount: float, description: str = "") -> UserWalletDetail:
    """
    更新钱包余额
    """
    result = await wallets_repo.update_wallet_balance(db, user_id, amount, description)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新钱包余额失败"
        )

    return UserWalletDetail(**result)


async def transfer_funds(db: DatabaseAdapter, from_user_id: int, to_user_id: int, amount: float, description: str = "") -> bool:
    """
    转账
    """
    return await wallets_repo.transfer_balance(db, from_user_id, to_user_id, amount, description)


async def process_payment(db: DatabaseAdapter, from_user_id: int, to_user_id: int, amount: float, description: str = "") -> bool:
    """
    处理支付
    """
    return await wallets_repo.process_payment(db, from_user_id, to_user_id, amount, description)
