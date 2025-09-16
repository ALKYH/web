"""
交易 & 金融 - API 路由
包括订单、钱包和交易管理的API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from apps.api.v1.deps import (
    get_current_user,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.transaction import (
    Order, OrderCreate, OrderUpdate,
    UserWallet, UserWalletCreate, UserWalletUpdate,
    WalletTransaction, WalletTransactionCreate
)
from apps.schemas.common import GeneralResponse, PaginatedResponse
from apps.api.v1.services import transaction as transaction_service

router = APIRouter()


# ============ 订单管理 ============

@router.get(
    "/orders",
    response_model=GeneralResponse[List[Order]],
    summary="获取订单列表",
    description="获取当前用户的订单列表"
)
async def list_orders(
    status_filter: Optional[str] = Query(None, description="订单状态筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取订单列表

    - **status_filter**: 订单状态筛选（可选）
    - **limit**: 返回数量（1-100）
    - **offset**: 偏移量
    """
    orders = await transaction_service.get_orders_by_user(db, current_user.id)
    return GeneralResponse(data=orders)


@router.post(
    "/orders",
    response_model=GeneralResponse[Order],
    status_code=status.HTTP_201_CREATED,
    summary="创建订单",
    description="创建新的订单"
)
async def create_order(
    order_data: OrderCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建订单

    - **service_id**: 服务ID
    - **amount**: 订单金额
    """
    order = await transaction_service.create_order(db, order_data, current_user.id)
    return GeneralResponse(data=order)


@router.get(
    "/orders/{order_id}",
    response_model=GeneralResponse[Order],
    summary="获取订单详情",
    description="获取指定订单的详细信息"
)
async def get_order(
    order_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取订单详情

    - **order_id**: 订单ID
    """
    order = await transaction_service.get_order_by_id(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return GeneralResponse(data=order)


@router.put(
    "/orders/{order_id}",
    response_model=GeneralResponse[Order],
    summary="更新订单",
    description="更新指定订单的信息"
)
async def update_order(
    order_id: UUID,
    order_data: OrderUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新订单

    - **order_id**: 订单ID
    - **status**: 新状态（可选）
    """
    order = await transaction_service.update_order(db, order_id, order_data, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return GeneralResponse(data=order)


@router.delete(
    "/orders/{order_id}",
    response_model=GeneralResponse[dict],
    summary="取消订单",
    description="取消指定的订单"
)
async def cancel_order(
    order_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    取消订单

    - **order_id**: 订单ID
    """
    success = await transaction_service.cancel_order(db, order_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="订单不存在")
    return GeneralResponse(data={"message": "订单取消成功"})


# ============ 钱包管理 ============

@router.get(
    "/wallet",
    response_model=GeneralResponse[UserWallet],
    summary="获取用户钱包",
    description="获取当前用户的钱包信息"
)
async def get_user_wallet(
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取用户钱包信息"""
    wallet = await transaction_service.get_user_wallet(db, current_user.id)
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    return GeneralResponse(data=wallet)


@router.post(
    "/wallet",
    response_model=GeneralResponse[UserWallet],
    status_code=status.HTTP_201_CREATED,
    summary="创建用户钱包",
    description="为当前用户创建钱包"
)
async def create_user_wallet(
    wallet_data: UserWalletCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建用户钱包

    - **currency**: 货币类型
    - **initial_balance**: 初始余额（可选）
    """
    wallet = await transaction_service.create_user_wallet(db, wallet_data, current_user.id)
    return GeneralResponse(data=wallet)


@router.put(
    "/wallet",
    response_model=GeneralResponse[UserWallet],
    summary="更新用户钱包",
    description="更新当前用户的钱包信息"
)
async def update_user_wallet(
    wallet_data: UserWalletUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新用户钱包

    - **balance**: 新余额（可选）
    - **is_active**: 是否激活（可选）
    """
    wallet = await transaction_service.update_user_wallet(db, wallet_data, current_user.id)
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")
    return GeneralResponse(data=wallet)


# ============ 交易记录管理 ============

@router.get(
    "",
    response_model=GeneralResponse[List[WalletTransaction]],
    summary="获取交易记录",
    description="获取当前用户的交易记录"
)
async def list_transactions(
    transaction_type: Optional[str] = Query(None, description="交易类型筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取交易记录

    - **transaction_type**: 交易类型筛选（可选）
    - **limit**: 返回数量（1-100）
    - **offset**: 偏移量
    """
    transactions = await transaction_service.get_wallet_transactions(db, current_user.id, 1, limit)
    return GeneralResponse(data=transactions)


@router.post(
    "/transactions",
    response_model=GeneralResponse[WalletTransaction],
    status_code=status.HTTP_201_CREATED,
    summary="创建交易",
    description="创建新的钱包交易"
)
async def create_transaction(
    transaction_data: WalletTransactionCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建交易

    - **amount**: 交易金额
    - **transaction_type**: 交易类型
    - **description**: 交易描述
    """
    transaction = await transaction_service.create_wallet_transaction(db, transaction_data, current_user.id)
    return GeneralResponse(data=transaction)


@router.get(
    "/transactions/{transaction_id}",
    response_model=GeneralResponse[WalletTransaction],
    summary="获取交易详情",
    description="获取指定交易的详细信息"
)
async def get_transaction(
    transaction_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    获取交易详情

    - **transaction_id**: 交易ID
    """
    transaction = await transaction_service.get_wallet_transaction(db, transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="交易记录不存在")
    return GeneralResponse(data=transaction)


# ============ 支付相关 ============

@router.post(
    "/orders/{order_id}/pay",
    response_model=GeneralResponse[dict],
    summary="支付订单",
    description="使用钱包余额支付指定订单"
)
async def pay_order(
    order_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    支付订单

    - **order_id**: 订单ID
    """
    success, message = await transaction_service.pay_order(db, order_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return GeneralResponse(data={"message": message})


@router.post(
    "/wallet/recharge",
    response_model=GeneralResponse[WalletTransaction],
    summary="充值钱包",
    description="为用户钱包充值"
)
async def recharge_wallet(
    amount: Decimal = Query(..., gt=0, description="充值金额"),
    payment_method: str = Query(..., description="支付方式"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    充值钱包

    - **amount**: 充值金额（必须大于0）
    - **payment_method**: 支付方式
    """
    transaction = await transaction_service.recharge_wallet(db, amount, payment_method, current_user.id)
    return GeneralResponse(data=transaction)


@router.post(
    "/wallet/withdraw",
    response_model=GeneralResponse[WalletTransaction],
    summary="提现",
    description="从钱包提现到外部账户"
)
async def withdraw_wallet(
    amount: Decimal = Query(..., gt=0, description="提现金额"),
    account_info: str = Query(..., description="账户信息"),
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    提现钱包

    - **amount**: 提现金额（必须大于0）
    - **account_info**: 账户信息（银行卡号等）
    """
    transaction = await transaction_service.withdraw_wallet(db, amount, account_info, current_user.id)
    return GeneralResponse(data=transaction)


# ============ 财务统计 ============

@router.get(
    "/stats",
    response_model=GeneralResponse[dict],
    summary="获取财务统计",
    description="获取用户的财务统计信息"
)
async def get_financial_stats(
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取财务统计信息"""
    stats = await transaction_service.get_financial_stats(db, current_user.id)
    return GeneralResponse(data=stats)
