"""
论坛中心 - 服务层
提供帖子和评论管理的业务逻辑
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.forum import (
    ForumPost as Post, ForumPostCreate as PostCreate, ForumPostUpdate as PostUpdate,
    PostReply as Comment, PostReplyCreate as CommentCreate, PostReplyUpdate as CommentUpdate
)
from apps.api.v1.repositories import forum as forum_repo
from libs.database.adapters import DatabaseAdapter


# ============ 帖子服务 ============

async def get_posts(
    db: DatabaseAdapter,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0
):
    """获取帖子列表"""
    from apps.schemas.forum import ForumPostListResponse

    posts = await forum_repo.get_posts(
        db=db,
        category=category,
        tag=tag,
        author_id=author_id,
        limit=limit,
        offset=offset
    )

    # 计算分页信息
    total = await forum_repo.count_posts(db, category, tag, author_id)
    page = (offset // limit) + 1
    page_size = len(posts)

    return ForumPostListResponse(
        posts=posts,
        total=total,
        page=page,
        page_size=page_size
    )


async def get_post_by_id(db: DatabaseAdapter, post_id: UUID) -> Optional[Post]:
    """根据ID获取帖子"""
    return await forum_repo.get_post_by_id(db, post_id)


async def create_post(
    db: DatabaseAdapter,
    post_data: PostCreate,
    author_id: UUID
) -> Optional[Post]:
    """创建帖子"""
    return await forum_repo.create_post(db, post_data, author_id)


async def update_post(
    db: DatabaseAdapter,
    post_id: UUID,
    post_data: PostUpdate,
    author_id: UUID
) -> Optional[Post]:
    """更新帖子"""
    return await forum_repo.update_post(db, post_id, post_data, author_id)


async def delete_post(db: DatabaseAdapter, post_id: UUID, author_id: UUID) -> bool:
    """删除帖子"""
    return await forum_repo.delete_post(db, post_id, author_id)


async def get_posts_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Post]:
    """获取作者的帖子列表"""
    return await forum_repo.get_posts_by_author(db, author_id)


# ============ 评论服务 ============

async def get_post_replies(
    db: DatabaseAdapter,
    post_id: UUID,
    limit: int = 20,
    offset: int = 0
):
    """获取帖子的回复列表"""
    from apps.schemas.forum import ForumReplyListResponse

    replies = await forum_repo.get_post_replies(
        db, post_id, limit, offset
    )

    # 计算分页信息
    total = await forum_repo.count_post_replies(db, post_id)
    page = (offset // limit) + 1
    page_size = len(replies)

    return ForumReplyListResponse(
        replies=replies,
        total=total,
        page=page,
        page_size=page_size
    )


async def create_reply(
    db: DatabaseAdapter,
    post_id: UUID,
    reply_data: CommentCreate,
    author_id: UUID
) -> Optional[Comment]:
    """创建回复"""
    return await forum_repo.create_reply(
        db, post_id, reply_data, author_id
    )


async def update_reply(
    db: DatabaseAdapter,
    reply_id: UUID,
    reply_data: CommentUpdate,
    author_id: UUID
) -> Optional[Comment]:
    """更新回复"""
    return await forum_repo.update_reply(
        db, reply_id, reply_data, author_id
    )


async def delete_reply(
    db: DatabaseAdapter,
    reply_id: UUID,
    author_id: UUID
) -> bool:
    """删除回复"""
    return await forum_repo.delete_reply(db, reply_id, author_id)


async def get_comments_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Comment]:
    """获取作者的评论列表"""
    return await forum_repo.get_comments_by_author(db, author_id)


# ============ 点赞服务 ============

async def like_post(db: DatabaseAdapter, post_id: UUID, user_id: UUID):
    """点赞帖子"""
    return await forum_repo.like_post(db, post_id, user_id)


async def unlike_post(db: DatabaseAdapter, post_id: UUID, user_id: UUID) -> bool:
    """取消点赞帖子"""
    return await forum_repo.unlike_post(db, post_id, user_id)


async def like_reply(db: DatabaseAdapter, reply_id: UUID, user_id: UUID):
    """点赞回复"""
    return await forum_repo.like_reply(db, reply_id, user_id)


async def unlike_reply(db: DatabaseAdapter, reply_id: UUID, user_id: UUID) -> bool:
    """取消点赞回复"""
    return await forum_repo.unlike_reply(db, reply_id, user_id)