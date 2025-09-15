"""
朋友关系服务层
处理朋友关系的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status

from apps.schemas.friends import FriendCreate, FriendDetail, FriendListResponse, FriendRequestListResponse
from apps.api.v1.repositories import friends as friends_repo
from libs.database.adapters import DatabaseAdapter


async def send_friend_request(db: DatabaseAdapter, requester_id: int, target_user_id: int) -> FriendDetail:
    """
    发送朋友请求
    1. 检查目标用户是否存在
    2. 检查是否已经是朋友
    3. 创建朋友请求
    """
    if requester_id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能添加自己为朋友"
        )

    # 检查是否已经是朋友
    existing = await friends_repo.get_friendship_between_users(db, requester_id, target_user_id)
    if existing:
        if existing['status'] == 'accepted':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已经是朋友关系"
            )
        elif existing['status'] == 'pending':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已经发送过朋友请求"
            )

    # 创建朋友请求
    friend_request = FriendCreate(user_id=requester_id, friend_id=target_user_id)
    result = await friends_repo.create_friend_request(db, friend_request)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送朋友请求失败"
        )

    # 获取完整的朋友关系详情
    friendship = await friends_repo.get_friendship_by_id(db, result['id'])
    return FriendDetail(**friendship)


async def accept_friend_request(db: DatabaseAdapter, friendship_id: int, user_id: int) -> FriendDetail:
    """
    接受朋友请求
    """
    result = await friends_repo.accept_friend_request(db, friendship_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="接受朋友请求失败"
        )

    friendship = await friends_repo.get_friendship_by_id(db, friendship_id)
    return FriendDetail(**friendship)


async def reject_friend_request(db: DatabaseAdapter, friendship_id: int, user_id: int) -> bool:
    """
    拒绝朋友请求
    """
    return await friends_repo.reject_friend_request(db, friendship_id, user_id)


async def remove_friend(db: DatabaseAdapter, user_id: int, friend_id: int) -> bool:
    """
    删除好友关系
    """
    return await friends_repo.remove_friend(db, user_id, friend_id)


async def get_friends(db: DatabaseAdapter, user_id: int, skip: int = 0, limit: int = 50) -> FriendListResponse:
    """
    获取用户的好友列表
    """
    friends = await friends_repo.get_user_friends(db, user_id, status="accepted", skip=skip, limit=limit)

    friend_details = [FriendDetail(**friend) for friend in friends]

    return FriendListResponse(
        friends=friend_details,
        total=len(friend_details)
    )


async def get_friend_requests(db: DatabaseAdapter, user_id: int, skip: int = 0, limit: int = 50) -> FriendRequestListResponse:
    """
    获取用户的朋友请求
    """
    requests = await friends_repo.get_friend_requests(db, user_id, skip, limit)

    request_details = [FriendDetail(**request) for request in requests]

    return FriendRequestListResponse(
        requests=request_details,
        total=len(request_details)
    )


async def get_friends_count(db: DatabaseAdapter, user_id: int) -> int:
    """
    获取用户好友数量
    """
    return await friends_repo.get_friends_count(db, user_id)


async def get_pending_requests_count(db: DatabaseAdapter, user_id: int) -> int:
    """
    获取用户待处理请求数量
    """
    return await friends_repo.get_pending_requests_count(db, user_id)
