"""
论坛服务层
处理论坛帖子、回复和点赞相关的业务逻辑
"""
from typing import List, Dict, Optional
from fastapi import HTTPException, status

from apps.schemas.forum import (
    ForumPostCreate, ForumPostUpdate, ForumReplyCreate, ForumReplyUpdate,
    ForumPostDetail, ForumReplyDetail, ForumPostListResponse, ForumReplyListResponse
)
from apps.api.v1.repositories import forum as forum_repo
from libs.database.adapters import DatabaseAdapter


async def create_post(db: DatabaseAdapter, post: ForumPostCreate, author_id: int) -> ForumPostDetail:
    """
    创建论坛帖子
    """
    # 创建帖子
    post_data = await forum_repo.create_post(db, post, author_id)
    if not post_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建帖子失败"
        )

    # 获取完整帖子详情
    return await get_post_detail(db, post_data['id'], author_id)


async def get_post_detail(db: DatabaseAdapter, post_id: int, user_id: Optional[int] = None) -> ForumPostDetail:
    """
    获取帖子详情
    """
    post = await forum_repo.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    # 检查是否已点赞
    is_liked = False
    if user_id:
        is_liked = await forum_repo.has_user_liked_post(db, user_id, post_id)

    return ForumPostDetail(
        **post,
        is_liked_by_user=is_liked
    )


async def get_posts(db: DatabaseAdapter, category: Optional[str] = None, skip: int = 0, limit: int = 50, user_id: Optional[int] = None) -> ForumPostListResponse:
    """
    获取帖子列表
    """
    posts = await forum_repo.get_posts(db, category, skip, limit)

    # 为每个帖子添加点赞状态
    post_details = []
    for post in posts:
        is_liked = False
        if user_id:
            is_liked = await forum_repo.has_user_liked_post(db, user_id, post['id'])

        post_details.append(ForumPostDetail(
            **post,
            is_liked_by_user=is_liked
        ))

    return ForumPostListResponse(
        posts=post_details,
        total=len(post_details),
        has_next=len(post_details) == limit
    )


async def update_post(db: DatabaseAdapter, post_id: int, post: ForumPostUpdate, user_id: int) -> ForumPostDetail:
    """
    更新帖子
    1. 检查权限
    2. 更新帖子
    """
    # 获取原帖子
    existing_post = await forum_repo.get_post_by_id(db, post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    # 检查权限
    if existing_post['author_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此帖子"
        )

    # 更新帖子
    updated = await forum_repo.update_post(db, post_id, post)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新帖子失败"
        )

    return await get_post_detail(db, post_id, user_id)


async def delete_post(db: DatabaseAdapter, post_id: int, user_id: int) -> bool:
    """
    删除帖子
    1. 检查权限
    2. 删除帖子
    """
    existing_post = await forum_repo.get_post_by_id(db, post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    if existing_post['author_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此帖子"
        )

    return await forum_repo.delete_post(db, post_id)


async def create_reply(db: DatabaseAdapter, reply: ForumReplyCreate, author_id: int) -> ForumReplyDetail:
    """
    创建回复
    """
    # 检查帖子是否存在
    post = await forum_repo.get_post_by_id(db, reply.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    # 如果是回复其他回复，检查父回复是否存在
    if reply.parent_id:
        parent_reply = await forum_repo.get_reply_by_id(db, reply.parent_id)
        if not parent_reply:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父回复不存在"
            )

    # 创建回复
    reply_data = await forum_repo.create_reply(db, reply, author_id)
    if not reply_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建回复失败"
        )

    return await get_reply_detail(db, reply_data['id'], author_id)


async def get_reply_detail(db: DatabaseAdapter, reply_id: int, user_id: Optional[int] = None) -> ForumReplyDetail:
    """
    获取回复详情
    """
    reply = await forum_repo.get_reply_by_id(db, reply_id)
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回复不存在"
        )

    # 检查是否已点赞
    is_liked = False
    if user_id:
        is_liked = await forum_repo.has_user_liked_reply(db, user_id, reply_id)

    return ForumReplyDetail(
        **reply,
        is_liked_by_user=is_liked,
        child_replies=[]  # 这里可以递归获取子回复
    )


async def get_replies_by_post(db: DatabaseAdapter, post_id: int, parent_id: Optional[int] = None, skip: int = 0, limit: int = 50, user_id: Optional[int] = None) -> ForumReplyListResponse:
    """
    获取帖子的回复列表
    """
    replies = await forum_repo.get_replies_by_post(db, post_id, parent_id, skip, limit)

    # 为每个回复添加点赞状态
    reply_details = []
    for reply in replies:
        is_liked = False
        if user_id:
            is_liked = await forum_repo.has_user_liked_reply(db, user_id, reply['id'])

        reply_details.append(ForumReplyDetail(
            **reply,
            is_liked_by_user=is_liked,
            child_replies=[]
        ))

    return ForumReplyListResponse(
        replies=reply_details,
        total=len(reply_details),
        has_next=len(reply_details) == limit
    )


async def toggle_post_like(db: DatabaseAdapter, post_id: int, user_id: int) -> bool:
    """
    切换帖子点赞状态
    """
    # 检查帖子是否存在
    post = await forum_repo.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="帖子不存在"
        )

    # 检查是否已点赞
    has_liked = await forum_repo.has_user_liked_post(db, user_id, post_id)

    if has_liked:
        # 取消点赞
        return await forum_repo.remove_post_like(db, user_id, post_id)
    else:
        # 添加点赞
        result = await forum_repo.add_post_like(db, user_id, post_id)
        return result is not None


async def toggle_reply_like(db: DatabaseAdapter, reply_id: int, user_id: int) -> bool:
    """
    切换回复点赞状态
    """
    # 检查回复是否存在
    reply = await forum_repo.get_reply_by_id(db, reply_id)
    if not reply:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回复不存在"
        )

    # 检查是否已点赞
    has_liked = await forum_repo.has_user_liked_reply(db, user_id, reply_id)

    if has_liked:
        # 取消点赞
        return await forum_repo.remove_reply_like(db, user_id, reply_id)
    else:
        # 添加点赞
        result = await forum_repo.add_reply_like(db, user_id, reply_id)
        return result is not None


async def increment_post_views(db: DatabaseAdapter, post_id: int) -> bool:
    """
    增加帖子浏览数
    """
    return await forum_repo.increment_post_views(db, post_id)
