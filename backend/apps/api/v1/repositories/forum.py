"""
论坛中心 - 仓库层
提供帖子和评论的数据库操作
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.forum import (
    ForumPost as Post, ForumPostCreate as PostCreate, ForumPostUpdate as PostUpdate,
    PostReply as Comment, PostReplyCreate as CommentCreate, PostReplyUpdate as CommentUpdate
)
from libs.database.adapters import DatabaseAdapter


# ============ 帖子仓库操作 ============

async def get_posts(
    db: DatabaseAdapter,
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> List[Post]:
    """获取帖子列表"""
    offset = (page - 1) * page_size
    where_conditions = ["is_deleted = false"]
    params = []

    if category:
        where_conditions.append("category = $1")
        params.append(category)

    if search_query:
        where_conditions.append("(title ILIKE $1 OR content ILIKE $1)")
        params.append(f"%{search_query}%")

    where_clause = " AND ".join(where_conditions)

    query = f"""
        SELECT id, author_id, title, content, category, tags, view_count, like_count, comment_count, is_deleted, created_at, updated_at
        FROM posts
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([page_size, offset])

    rows = await db.fetch_all(query, *params)
    return [Post(**row) for row in rows]


async def get_post_by_id(db: DatabaseAdapter, post_id: UUID) -> Optional[Post]:
    """根据ID获取帖子"""
    query = """
        SELECT id, author_id, title, content, category, tags, view_count, like_count, comment_count, is_deleted, created_at, updated_at
        FROM posts
        WHERE id = $1 AND is_deleted = false
    """
    row = await db.fetch_one(query, post_id)
    return Post(**row) if row else None


async def create_post(
    db: DatabaseAdapter,
    post_data: PostCreate,
    author_id: UUID
) -> Optional[Post]:
    """创建帖子"""
    query = """
        INSERT INTO posts (author_id, title, content, category, tags)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, author_id, title, content, category, tags, view_count, like_count, comment_count, is_deleted, created_at, updated_at
    """
    values = (
        author_id,
        post_data.title,
        post_data.content,
        post_data.category,
        post_data.tags
    )
    row = await db.fetch_one(query, *values)
    return Post(**row) if row else None


async def update_post(
    db: DatabaseAdapter,
    post_id: UUID,
    author_id: UUID,
    post_data: PostUpdate
) -> Optional[Post]:
    """更新帖子"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if post_data.title is not None:
        set_parts.append(f"title = ${param_index}")
        values.append(post_data.title)
        param_index += 1

    if post_data.content is not None:
        set_parts.append(f"content = ${param_index}")
        values.append(post_data.content)
        param_index += 1

    if post_data.category is not None:
        set_parts.append(f"category = ${param_index}")
        values.append(post_data.category)
        param_index += 1

    if post_data.tags is not None:
        set_parts.append(f"tags = ${param_index}")
        values.append(post_data.tags)
        param_index += 1

    if not set_parts:
        return await get_post_by_id(db, post_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE posts
        SET {', '.join(set_parts)}
        WHERE id = ${param_index} AND author_id = ${param_index + 1} AND is_deleted = false
        RETURNING id, author_id, title, content, category, tags, view_count, like_count, comment_count, is_deleted, created_at, updated_at
    """
    values.extend([post_id, author_id])

    row = await db.fetch_one(query, *values)
    return Post(**row) if row else None


async def delete_post(db: DatabaseAdapter, post_id: UUID, author_id: UUID) -> bool:
    """软删除帖子"""
    query = """
        UPDATE posts
        SET is_deleted = true, updated_at = NOW()
        WHERE id = $1 AND author_id = $2 AND is_deleted = false
    """
    result = await db.execute(query, post_id, author_id)
    return result == "UPDATE 1"


async def get_posts_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Post]:
    """获取作者的帖子列表"""
    query = """
        SELECT id, author_id, title, content, category, tags, view_count, like_count, comment_count, is_deleted, created_at, updated_at
        FROM posts
        WHERE author_id = $1 AND is_deleted = false
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, author_id)
    return [Post(**row) for row in rows]


# ============ 评论仓库操作 ============

async def get_comments_by_post(
    db: DatabaseAdapter,
    post_id: UUID,
    page: int = 1,
    page_size: int = 50
) -> List[Comment]:
    """获取帖子的评论列表"""
    offset = (page - 1) * page_size
    query = """
        SELECT id, post_id, author_id, parent_id, content, like_count, is_deleted, created_at, updated_at
        FROM comments
        WHERE post_id = $1 AND is_deleted = false
        ORDER BY created_at ASC
        LIMIT $2 OFFSET $3
    """
    rows = await db.fetch_all(query, post_id, page_size, offset)
    return [Comment(**row) for row in rows]


async def create_comment(
    db: DatabaseAdapter,
    post_id: UUID,
    comment_data: CommentCreate,
    author_id: UUID
) -> Optional[Comment]:
    """创建评论"""
    query = """
        INSERT INTO comments (post_id, author_id, parent_id, content)
        VALUES ($1, $2, $3, $4)
        RETURNING id, post_id, author_id, parent_id, content, like_count, is_deleted, created_at, updated_at
    """
    values = (
        post_id,
        author_id,
        comment_data.parent_id,
        comment_data.content
    )
    row = await db.fetch_one(query, *values)
    if row:
        # 增加帖子评论数
        await increment_post_comment_count(db, post_id)
        return Comment(**row)
    return None


async def update_comment(
    db: DatabaseAdapter,
    comment_id: UUID,
    author_id: UUID,
    comment_data: CommentUpdate
) -> Optional[Comment]:
    """更新评论"""
    query = """
        UPDATE comments
        SET content = $1, updated_at = NOW()
        WHERE id = $2 AND author_id = $3 AND is_deleted = false
        RETURNING id, post_id, author_id, parent_id, content, like_count, is_deleted, created_at, updated_at
    """
    row = await db.fetch_one(query, comment_data.content, comment_id, author_id)
    return Comment(**row) if row else None


async def delete_comment(
    db: DatabaseAdapter,
    comment_id: UUID,
    author_id: UUID
) -> bool:
    """软删除评论"""
    query = """
        UPDATE comments
        SET is_deleted = true, updated_at = NOW()
        WHERE id = $1 AND author_id = $2 AND is_deleted = false
    """
    result = await db.execute(query, comment_id, author_id)
    if result == "UPDATE 1":
        # 减少帖子评论数
        await decrement_post_comment_count_by_comment(db, comment_id)
        return True
    return False


async def get_comments_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Comment]:
    """获取作者的评论列表"""
    query = """
        SELECT c.id, c.post_id, c.author_id, c.parent_id, c.content, c.like_count, c.is_deleted, c.created_at, c.updated_at,
               p.title as post_title
        FROM comments c
        JOIN posts p ON c.post_id = p.id
        WHERE c.author_id = $1 AND c.is_deleted = false
        ORDER BY c.created_at DESC
    """
    rows = await db.fetch_all(query, author_id)
    # 这里需要处理额外的 post_title 字段，可能需要调整
    return [Comment(**{k: v for k, v in row.items() if k in Comment.__annotations__}) for row in rows]


async def increment_post_comment_count(db: DatabaseAdapter, post_id: UUID) -> None:
    """增加帖子评论数"""
    query = """
        UPDATE posts
        SET comment_count = comment_count + 1
        WHERE id = $1
    """
    await db.execute(query, post_id)


async def decrement_post_comment_count_by_comment(
    db: DatabaseAdapter,
    comment_id: UUID
) -> None:
    """根据评论ID减少帖子评论数"""
    query = """
        UPDATE posts
        SET comment_count = comment_count - 1
        WHERE id = (
            SELECT post_id FROM comments WHERE id = $1
        ) AND comment_count > 0
    """
    await db.execute(query, comment_id)