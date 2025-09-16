"""
论坛中心 - API 路由
包括帖子和评论管理的API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from apps.api.v1.deps import (
    get_current_user,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.forum import (
    ForumPost, ForumPostCreate, ForumPostUpdate,
    PostReply, PostReplyCreate, PostReplyUpdate,
    Like, LikeCreate,
    ForumPostDetail, ForumReplyDetail,
    ForumPostListResponse, ForumReplyListResponse
)
from apps.schemas.common import GeneralResponse, PaginatedResponse
from apps.api.v1.services import forum as forum_service

router = APIRouter()


# ============ 论坛帖子管理 ============

@router.get(
    "/posts",
    response_model=GeneralResponse[ForumPostListResponse],
    summary="获取帖子列表",
    description="获取论坛帖子列表，支持分页和筛选"
)
async def list_posts(
    category: Optional[str] = Query(None, description="帖子分类"),
    tag: Optional[str] = Query(None, description="标签筛选"),
    author_id: Optional[UUID] = Query(None, description="作者ID筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取帖子列表

    - **category**: 帖子分类筛选
    - **tag**: 标签筛选
    - **author_id**: 作者ID筛选
    - **limit**: 返回数量（1-100）
    - **offset**: 偏移量
    """
    result = await forum_service.get_posts(
        db, category, tag, author_id, limit, offset
    )
    return GeneralResponse(data=result)


@router.post(
    "/posts",
    response_model=GeneralResponse[ForumPost],
    status_code=status.HTTP_201_CREATED,
    summary="创建帖子",
    description="创建新的论坛帖子"
)
async def create_post(
    post_data: ForumPostCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建新帖子

    - **title**: 帖子标题
    - **content**: 帖子内容
    - **category**: 帖子分类
    - **tags**: 标签列表
    """
    post = await forum_service.create_post(db, post_data, current_user.id)
    return GeneralResponse(data=post)


@router.get(
    "/posts/{post_id}",
    response_model=GeneralResponse[ForumPostDetail],
    summary="获取帖子详情",
    description="获取指定帖子的详细信息，包括作者信息和统计数据"
)
async def get_post(
    post_id: UUID,
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取帖子详情

    - **post_id**: 帖子ID
    """
    post = await forum_service.get_post_detail(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return GeneralResponse(data=post)


@router.put(
    "/posts/{post_id}",
    response_model=GeneralResponse[ForumPost],
    summary="更新帖子",
    description="更新指定帖子的信息"
)
async def update_post(
    post_id: UUID,
    post_data: ForumPostUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新帖子

    - **post_id**: 帖子ID
    - **title**: 新标题（可选）
    - **content**: 新内容（可选）
    - **category**: 新分类（可选）
    - **tags**: 新标签列表（可选）
    """
    post = await forum_service.update_post(db, post_id, post_data, current_user.id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在或无权限")
    return GeneralResponse(data=post)


@router.delete(
    "/posts/{post_id}",
    response_model=GeneralResponse[dict],
    summary="删除帖子",
    description="删除指定的帖子"
)
async def delete_post(
    post_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除帖子

    - **post_id**: 帖子ID
    """
    success = await forum_service.delete_post(db, post_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="帖子不存在或无权限")
    return GeneralResponse(data={"message": "帖子删除成功"})


# ============ 帖子回复管理 ============

@router.get(
    "/posts/{post_id}/replies",
    response_model=GeneralResponse[ForumReplyListResponse],
    summary="获取帖子回复",
    description="获取指定帖子的所有回复"
)
async def list_post_replies(
    post_id: UUID,
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取帖子回复列表

    - **post_id**: 帖子ID
    - **limit**: 返回数量（1-100）
    - **offset**: 偏移量
    """
    result = await forum_service.get_post_replies(db, post_id, limit, offset)
    return GeneralResponse(data=result)


@router.post(
    "/posts/{post_id}/replies",
    response_model=GeneralResponse[PostReply],
    status_code=status.HTTP_201_CREATED,
    summary="回复帖子",
    description="对指定帖子发表回复"
)
async def create_reply(
    post_id: UUID,
    reply_data: PostReplyCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建帖子回复

    - **post_id**: 帖子ID
    - **content**: 回复内容
    - **parent_reply_id**: 父回复ID（用于嵌套回复，可选）
    """
    reply = await forum_service.create_reply(db, post_id, reply_data, current_user.id)
    return GeneralResponse(data=reply)


@router.put(
    "/replies/{reply_id}",
    response_model=GeneralResponse[PostReply],
    summary="更新回复",
    description="更新指定的回复内容"
)
async def update_reply(
    reply_id: UUID,
    reply_data: PostReplyUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新回复

    - **reply_id**: 回复ID
    - **content**: 新回复内容
    """
    reply = await forum_service.update_reply(db, reply_id, reply_data, current_user.id)
    if not reply:
        raise HTTPException(status_code=404, detail="回复不存在或无权限")
    return GeneralResponse(data=reply)


@router.delete(
    "/replies/{reply_id}",
    response_model=GeneralResponse[dict],
    summary="删除回复",
    description="删除指定的回复"
)
async def delete_reply(
    reply_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除回复

    - **reply_id**: 回复ID
    """
    success = await forum_service.delete_reply(db, reply_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="回复不存在或无权限")
    return GeneralResponse(data={"message": "回复删除成功"})


# ============ 点赞管理 ============

@router.post(
    "/posts/{post_id}/like",
    response_model=GeneralResponse[Like],
    status_code=status.HTTP_201_CREATED,
    summary="点赞帖子",
    description="对指定帖子进行点赞"
)
async def like_post(
    post_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    点赞帖子

    - **post_id**: 帖子ID
    """
    like = await forum_service.like_post(db, post_id, current_user.id)
    return GeneralResponse(data=like)


@router.post(
    "/replies/{reply_id}/like",
    response_model=GeneralResponse[Like],
    status_code=status.HTTP_201_CREATED,
    summary="点赞回复",
    description="对指定回复进行点赞"
)
async def like_reply(
    reply_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    点赞回复

    - **reply_id**: 回复ID
    """
    like = await forum_service.like_reply(db, reply_id, current_user.id)
    return GeneralResponse(data=like)


@router.delete(
    "/likes/posts/{post_id}",
    response_model=GeneralResponse[dict],
    summary="取消帖子点赞",
    description="取消对指定帖子的点赞"
)
async def unlike_post(
    post_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    取消帖子点赞

    - **post_id**: 帖子ID
    """
    success = await forum_service.unlike_post(db, post_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="点赞不存在")
    return GeneralResponse(data={"message": "取消点赞成功"})


@router.delete(
    "/likes/replies/{reply_id}",
    response_model=GeneralResponse[dict],
    summary="取消回复点赞",
    description="取消对指定回复的点赞"
)
async def unlike_reply(
    reply_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    取消回复点赞

    - **reply_id**: 回复ID
    """
    success = await forum_service.unlike_reply(db, reply_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="点赞不存在")
    return GeneralResponse(data={"message": "取消点赞成功"})
