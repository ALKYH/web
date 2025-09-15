"""
订单服务层
处理订单相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status

from apps.schemas.orders import OrderCreate, OrderUpdate, OrderDetail, OrderListResponse, OrderStats
from apps.api.v1.repositories import orders as orders_repo
from libs.database.adapters import DatabaseAdapter


async def create_order(db: DatabaseAdapter, order: OrderCreate, creator_id: int) -> OrderDetail:
    """
    创建订单
    1. 验证权限
    2. 创建订单
    """
    if creator_id != order.client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此用户创建订单"
        )

    result = await orders_repo.create_order(db, order)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败"
        )

    # 获取完整订单详情
    return await get_order_detail(db, result['id'], creator_id)


async def get_order_detail(db: DatabaseAdapter, order_id: int, user_id: int) -> OrderDetail:
    """
    获取订单详情
    1. 检查权限
    2. 返回订单详情
    """
    order = await orders_repo.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限
    if user_id not in [order['client_id'], order['navigator_id']]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此订单"
        )

    return OrderDetail(**order)


async def update_order_status(db: DatabaseAdapter, order_id: int, status: str, user_id: int) -> OrderDetail:
    """
    更新订单状态
    """
    order = await orders_repo.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限
    if user_id not in [order['client_id'], order['navigator_id']]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此订单"
        )

    update_data = OrderUpdate(status=status)
    result = await orders_repo.update_order(db, order_id, update_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新订单失败"
        )

    return await get_order_detail(db, order_id, user_id)


async def get_user_orders(db: DatabaseAdapter, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> OrderListResponse:
    """
    获取用户的订单列表
    """
    orders = await orders_repo.get_orders_for_user(db, user_id, status, skip, limit)

    order_details = [OrderDetail(**order) for order in orders]

    return OrderListResponse(
        orders=order_details,
        total=len(order_details),
        has_next=len(order_details) == limit
    )


async def get_order_stats(db: DatabaseAdapter, user_id: Optional[int] = None) -> OrderStats:
    """
    获取订单统计
    """
    stats = await orders_repo.get_order_stats(db, user_id)

    return OrderStats(**stats)
