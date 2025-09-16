"""
论坛中心 - 仓库层
提供帖子和评论的数据库操作
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.forum import (
    ForumPost as Post, ForumPostCreate as PostCreate, ForumPostUpdate as PostUpdate,
    PostReply as Comment, PostReplyCreate as CommentCreate, PostReplyUpdate as CommentUpdate,
    PostReplyWithCounts
)
from libs.database.adapters import DatabaseAdapter


# ============ 帖子仓库操作 ============

async def get_posts(
    db: DatabaseAdapter,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[UUID] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Post]:
    """获取帖子列表"""
    where_conditions = []
    params = []

    if category:
        where_conditions.append(f"category = ${len(params) + 1}")
        params.append(category)

    if tag:
        where_conditions.append(f"${len(params) + 1} = ANY(tags)")
        params.append(tag)

    if author_id:
        where_conditions.append(f"author_id = ${len(params) + 1}")
        params.append(author_id)

    where_clause = " AND ".join(where_conditions) if where_conditions else ""

    query = f"""
        SELECT id, author_id, title, content, category, tags, views_count, created_at, updated_at
        FROM forum_posts
        {"WHERE " + where_clause if where_clause else ""}
        ORDER BY created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, offset])

    rows = await db.fetch_all(query, *params)
    return [Post(**row) for row in rows]


async def get_post_by_id(db: DatabaseAdapter, post_id: UUID) -> Optional[Post]:
    """根据ID获取帖子"""
    query = """
        SELECT id, author_id, title, content, category, tags, views_count, created_at, updated_at
        FROM forum_posts
        WHERE id = $1
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
        INSERT INTO forum_posts (author_id, title, content, category, tags)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, author_id, title, content, category, tags, views_count, created_at, updated_at
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
    post_data: PostUpdate,
    author_id: UUID
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
        UPDATE forum_posts
        SET {', '.join(set_parts)}
        WHERE id = ${param_index} AND author_id = ${param_index + 1}
        RETURNING id, author_id, title, content, category, tags, views_count, created_at, updated_at
    """
    values.extend([post_id, author_id])

    row = await db.fetch_one(query, *values)
    return Post(**row) if row else None


async def delete_post(db: DatabaseAdapter, post_id: UUID, author_id: UUID) -> bool:
    """删除帖子"""
    query = """
        DELETE FROM forum_posts
        WHERE id = $1 AND author_id = $2
    """
    result = await db.execute(query, post_id, author_id)
    return result == "DELETE 1"


async def get_posts_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Post]:
    """获取作者的帖子列表"""
    query = """
        SELECT id, author_id, title, content, category, tags, views_count, created_at, updated_at
        FROM forum_posts
        WHERE author_id = $1
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, author_id)
    return [Post(**row) for row in rows]


async def count_posts(
    db: DatabaseAdapter,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[UUID] = None
) -> int:
    """统计帖子数量"""
    where_conditions = []
    params = []

    if category:
        where_conditions.append(f"category = ${len(params) + 1}")
        params.append(category)

    if tag:
        where_conditions.append(f"${len(params) + 1} = ANY(tags)")
        params.append(tag)

    if author_id:
        where_conditions.append(f"author_id = ${len(params) + 1}")
        params.append(author_id)

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

    query = f"""
        SELECT COUNT(*) as count
        FROM forum_posts
        WHERE {where_clause}
    """

    row = await db.fetch_one(query, *params)
    return row["count"] if row else 0


# ============ 评论仓库操作 ============

async def get_post_replies(
    db: DatabaseAdapter,
    post_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Comment]:
    """获取帖子的回复列表"""
    query = """
        SELECT pr.id, pr.post_id, pr.author_id, pr.parent_reply_id as parent_id, pr.content, pr.created_at, pr.updated_at,
               COALESCE(like_counts.like_count, 0) as like_count
        FROM post_replies pr
        LEFT JOIN (
            SELECT reply_id, COUNT(*) as like_count
            FROM likes
            WHERE reply_id IS NOT NULL
            GROUP BY reply_id
        ) like_counts ON pr.id = like_counts.reply_id
        WHERE pr.post_id = $1
        ORDER BY pr.created_at ASC
        LIMIT $2 OFFSET $3
    """
    rows = await db.fetch_all(query, post_id, limit, offset)
    return [Comment(**row) for row in rows]


async def count_post_replies(db: DatabaseAdapter, post_id: UUID) -> int:
    """统计帖子的回复数量"""
    query = """
        SELECT COUNT(*) as count
        FROM post_replies
        WHERE post_id = $1
    """
    row = await db.fetch_one(query, post_id)
    return row["count"] if row else 0


async def create_reply(
    db: DatabaseAdapter,
    post_id: UUID,
    reply_data: CommentCreate,
    author_id: UUID
) -> Optional[Comment]:
    """创建回复"""
    query = """
        INSERT INTO post_replies (post_id, author_id, parent_reply_id, content)
        VALUES ($1, $2, $3, $4)
        RETURNING id, post_id, author_id, parent_reply_id as parent_id, content, created_at, updated_at
    """
    values = (
        post_id,
        author_id,
        reply_data.parent_reply_id,
        reply_data.content
    )
    row = await db.fetch_one(query, *values)
    return Comment(**row) if row else None


async def update_reply(
    db: DatabaseAdapter,
    reply_id: UUID,
    reply_data: CommentUpdate,
    author_id: UUID
) -> Optional[Comment]:
    """更新回复"""
    query = """
        UPDATE post_replies
        SET content = $1, updated_at = NOW()
        WHERE id = $2 AND author_id = $3
        RETURNING id, post_id, author_id, parent_reply_id as parent_id, content, created_at, updated_at
    """
    row = await db.fetch_one(query, reply_data.content, reply_id, author_id)
    return Comment(**row) if row else None


async def delete_reply(
    db: DatabaseAdapter,
    reply_id: UUID,
    author_id: UUID
) -> bool:
    """删除回复"""
    query = """
        DELETE FROM post_replies
        WHERE id = $1 AND author_id = $2
    """
    result = await db.execute(query, reply_id, author_id)
    return result == "DELETE 1"


async def get_comments_by_author(db: DatabaseAdapter, author_id: UUID) -> List[Comment]:
    """获取作者的回复列表"""
    query = """
        SELECT c.id, c.post_id, c.author_id, c.parent_reply_id as parent_id, c.content, c.created_at, c.updated_at
        FROM post_replies c
        WHERE c.author_id = $1
        ORDER BY c.created_at DESC
    """
    rows = await db.fetch_all(query, author_id)
    return [Comment(**row) for row in rows]




# ============ 点赞仓库操作 ============

async def like_post(db: DatabaseAdapter, post_id: UUID, user_id: UUID):
    """点赞帖子"""
    # 先检查是否已经点赞
    check_query = """
        SELECT id FROM likes
        WHERE post_id = $1 AND user_id = $2
    """
    existing = await db.fetch_one(check_query, post_id, user_id)

    if existing:
        return existing

    # 创建点赞记录
    insert_query = """
        INSERT INTO likes (post_id, user_id)
        VALUES ($1, $2)
        RETURNING id, post_id, user_id, created_at
    """
    like_record = await db.fetch_one(insert_query, post_id, user_id)

    return like_record


async def unlike_post(db: DatabaseAdapter, post_id: UUID, user_id: UUID) -> bool:
    """取消点赞帖子"""
    delete_query = """
        DELETE FROM likes
        WHERE post_id = $1 AND user_id = $2
    """
    result = await db.execute(delete_query, post_id, user_id)
    return result == "DELETE 1"


async def like_reply(db: DatabaseAdapter, reply_id: UUID, user_id: UUID):
    """点赞回复"""
    # 先检查是否已经点赞
    check_query = """
        SELECT id FROM likes
        WHERE reply_id = $1 AND user_id = $2
    """
    existing = await db.fetch_one(check_query, reply_id, user_id)

    if existing:
        return existing

    # 创建点赞记录
    insert_query = """
        INSERT INTO likes (reply_id, user_id)
        VALUES ($1, $2)
        RETURNING id, reply_id, user_id, created_at
    """
    like_record = await db.fetch_one(insert_query, reply_id, user_id)

    return like_record


async def unlike_reply(db: DatabaseAdapter, reply_id: UUID, user_id: UUID) -> bool:
    """取消点赞回复"""
    delete_query = """
        DELETE FROM likes
        WHERE reply_id = $1 AND user_id = $2
    """
    result = await db.execute(delete_query, reply_id, user_id)
    return result == "DELETE 1"