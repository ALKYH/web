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
    search_query: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> List[Post]:
    """获取帖子列表"""
    return await forum_repo.get_posts(
        db=db,
        category=category,
        search_query=search_query,
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
    author_id: UUID,
    post_data: PostUpdate
) -> Optional[Post]:
    """更新帖子"""
    return await forum_repo.update_post(db, post_id, author_id, post_data)


async def delete_post(db: DatabaseAdapter, post_id: UUID, author_id: UUID) -> bool:
    """删除帖子"""
    return await forum_repo.delete_post(db, post_id, author_id)


async def get_posts_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Post]:
    """获取作者的帖子列表"""
    return await forum_repo.get_posts_by_author(db, author_id)


# ============ 评论服务 ============

async def get_comments_by_post(
    db: DatabaseAdapter,
    post_id: UUID,
    page: int = 1,
    page_size: int = 50
) -> List[Comment]:
    """获取帖子的评论列表"""
    return await forum_repo.get_comments_by_post(
        db, post_id, page, page_size
    )


async def create_comment(
    db: DatabaseAdapter,
    post_id: UUID,
    comment_data: CommentCreate,
    author_id: UUID
) -> Optional[Comment]:
    """创建评论"""
    return await forum_repo.create_comment(
        db, post_id, comment_data, author_id
    )


async def update_comment(
    db: DatabaseAdapter,
    comment_id: UUID,
    author_id: UUID,
    comment_data: CommentUpdate
) -> Optional[Comment]:
    """更新评论"""
    return await forum_repo.update_comment(
        db, comment_id, author_id, comment_data
    )


async def delete_comment(
    db: DatabaseAdapter,
    comment_id: UUID,
    author_id: UUID
) -> bool:
    """删除评论"""
    return await forum_repo.delete_comment(db, comment_id, author_id)


async def get_comments_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Comment]:
    """获取作者的评论列表"""
    return await forum_repo.get_comments_by_author(db, author_id)