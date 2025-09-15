"""
论坛相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.forum import ForumPostCreate, ForumPostUpdate, ForumReplyCreate, ForumReplyUpdate
from libs.database.adapters import DatabaseAdapter


# 论坛帖子相关操作

async def get_post_by_id(db: DatabaseAdapter, post_id: int) -> Optional[Dict]:
    """根据ID获取帖子"""
    query = """
        SELECT p.*, u.username as author_username, u.avatar_url as author_avatar
        FROM forum_posts p
        JOIN users u ON p.author_id = u.id
        WHERE p.id = $1
    """
    return await db.fetch_one(query, post_id)


async def get_posts(db: DatabaseAdapter, category: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取帖子列表"""
    where_clause = "WHERE 1=1"
    params = []
    param_count = 0

    if category:
        param_count += 1
        where_clause += f" AND p.category = ${param_count}"
        params.append(category)

    query = f"""
        SELECT p.*, u.username as author_username, u.avatar_url as author_avatar
        FROM forum_posts p
        JOIN users u ON p.author_id = u.id
        {where_clause}
        ORDER BY p.is_pinned DESC, p.last_activity DESC
        LIMIT ${param_count + 1} OFFSET ${param_count + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_post(db: DatabaseAdapter, post: ForumPostCreate, author_id: int) -> Optional[Dict]:
    """创建帖子"""
    query = """
        INSERT INTO forum_posts (
            title, content, author_id, category, tags, replies_count,
            likes_count, views_count, is_pinned, is_hot, created_at, updated_at, last_activity
        )
        VALUES ($1, $2, $3, $4, $5, 0, 0, 0, $6, $7, NOW(), NOW(), NOW())
        RETURNING *
    """
    values = (
        post.title, post.content, author_id, post.category,
        post.tags or [], post.is_anonymous or False, post.is_hot or False
    )
    return await db.fetch_one(query, *values)


async def update_post(db: DatabaseAdapter, post_id: int, post: ForumPostUpdate) -> Optional[Dict]:
    """更新帖子"""
    update_data = post.model_dump(exclude_unset=True)
    if not update_data:
        return await get_post_by_id(db, post_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE forum_posts SET {set_clause}, updated_at = NOW(), last_activity = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, post_id, *update_data.values())


async def delete_post(db: DatabaseAdapter, post_id: int) -> bool:
    """删除帖子"""
    query = "DELETE FROM forum_posts WHERE id = $1"
    result = await db.execute(query, post_id)
    return result == "DELETE 1"


async def increment_post_views(db: DatabaseAdapter, post_id: int) -> bool:
    """增加帖子浏览数"""
    query = "UPDATE forum_posts SET views_count = views_count + 1 WHERE id = $1"
    result = await db.execute(query, post_id)
    return result == "UPDATE 1"


# 论坛回复相关操作

async def get_reply_by_id(db: DatabaseAdapter, reply_id: int) -> Optional[Dict]:
    """根据ID获取回复"""
    query = """
        SELECT r.*, u.username as author_username, u.avatar_url as author_avatar
        FROM forum_replies r
        JOIN users u ON r.author_id = u.id
        WHERE r.id = $1
    """
    return await db.fetch_one(query, reply_id)


async def get_replies_by_post(db: DatabaseAdapter, post_id: int, parent_id: Optional[int] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取帖子的回复列表"""
    where_clause = "WHERE r.post_id = $1"
    params = [post_id]

    if parent_id is not None:
        where_clause += " AND r.parent_id = $2"
        params.append(parent_id)

    query = f"""
        SELECT r.*, u.username as author_username, u.avatar_url as author_avatar
        FROM forum_replies r
        JOIN users u ON r.author_id = u.id
        {where_clause}
        ORDER BY r.created_at
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_reply(db: DatabaseAdapter, reply: ForumReplyCreate, author_id: int) -> Optional[Dict]:
    """创建回复"""
    query = """
        INSERT INTO forum_replies (
            post_id, content, author_id, parent_id, parent_reply_id,
            likes_count, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, 0, NOW(), NOW())
        RETURNING *
    """
    values = (
        reply.post_id, reply.content, author_id,
        reply.parent_id, reply.parent_reply_id
    )
    result = await db.fetch_one(query, *values)

    # 更新帖子回复数和最后活动时间
    if result:
        await db.execute("""
            UPDATE forum_posts
            SET replies_count = replies_count + 1, last_activity = NOW()
            WHERE id = $1
        """, reply.post_id)

    return result


async def update_reply(db: DatabaseAdapter, reply_id: int, reply: ForumReplyUpdate) -> Optional[Dict]:
    """更新回复"""
    update_data = reply.model_dump(exclude_unset=True)
    if not update_data:
        return await get_reply_by_id(db, reply_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE forum_replies SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, reply_id, *update_data.values())


async def delete_reply(db: DatabaseAdapter, reply_id: int) -> bool:
    """删除回复"""
    # 先获取回复信息
    reply = await get_reply_by_id(db, reply_id)
    if not reply:
        return False

    query = "DELETE FROM forum_replies WHERE id = $1"
    result = await db.execute(query, reply_id)

    # 更新帖子回复数
    if result == "DELETE 1":
        await db.execute("""
            UPDATE forum_posts
            SET replies_count = GREATEST(replies_count - 1, 0)
            WHERE id = $1
        """, reply['post_id'])

    return result == "DELETE 1"


# 点赞相关操作

async def add_post_like(db: DatabaseAdapter, user_id: int, post_id: int) -> Optional[Dict]:
    """添加帖子点赞"""
    query = """
        INSERT INTO forum_likes (user_id, post_id, created_at)
        VALUES ($1, $2, NOW())
        RETURNING *
    """
    result = await db.fetch_one(query, user_id, post_id)

    # 更新帖子点赞数
    if result:
        await db.execute("""
            UPDATE forum_posts
            SET likes_count = likes_count + 1
            WHERE id = $1
        """, post_id)

    return result


async def remove_post_like(db: DatabaseAdapter, user_id: int, post_id: int) -> bool:
    """移除帖子点赞"""
    query = "DELETE FROM forum_likes WHERE user_id = $1 AND post_id = $2"
    result = await db.execute(query, user_id, post_id)

    # 更新帖子点赞数
    if result == "DELETE 1":
        await db.execute("""
            UPDATE forum_posts
            SET likes_count = GREATEST(likes_count - 1, 0)
            WHERE id = $1
        """, post_id)

    return result == "DELETE 1"


async def add_reply_like(db: DatabaseAdapter, user_id: int, reply_id: int) -> Optional[Dict]:
    """添加回复点赞"""
    query = """
        INSERT INTO forum_reply_likes (reply_id, user_id, created_at)
        VALUES ($1, $2, NOW())
        RETURNING *
    """
    result = await db.fetch_one(query, reply_id, user_id)

    # 更新回复点赞数
    if result:
        await db.execute("""
            UPDATE forum_replies
            SET likes_count = likes_count + 1
            WHERE id = $1
        """, reply_id)

    return result


async def remove_reply_like(db: DatabaseAdapter, user_id: int, reply_id: int) -> bool:
    """移除回复点赞"""
    query = "DELETE FROM forum_reply_likes WHERE user_id = $1 AND reply_id = $2"
    result = await db.execute(query, user_id, reply_id)

    # 更新回复点赞数
    if result == "DELETE 1":
        await db.execute("""
            UPDATE forum_replies
            SET likes_count = GREATEST(likes_count - 1, 0)
            WHERE id = $1
        """, reply_id)

    return result == "DELETE 1"


async def has_user_liked_post(db: DatabaseAdapter, user_id: int, post_id: int) -> bool:
    """检查用户是否点赞了帖子"""
    query = "SELECT 1 FROM forum_likes WHERE user_id = $1 AND post_id = $2"
    result = await db.fetch_one(query, user_id, post_id)
    return result is not None


async def has_user_liked_reply(db: DatabaseAdapter, user_id: int, reply_id: int) -> bool:
    """检查用户是否点赞了回复"""
    query = "SELECT 1 FROM forum_reply_likes WHERE user_id = $1 AND reply_id = $2"
    result = await db.fetch_one(query, user_id, reply_id)
    return result is not None
