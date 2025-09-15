"""
朋友关系相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.friends import FriendCreate, FriendUpdate
from libs.database.adapters import DatabaseAdapter


async def get_friendship_by_id(db: DatabaseAdapter, friendship_id: int) -> Optional[Dict]:
    """根据ID获取朋友关系"""
    query = """
        SELECT f.*, u1.username as user_username, u1.avatar_url as user_avatar,
               u2.username as friend_username, u2.avatar_url as friend_avatar
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        JOIN users u2 ON f.friend_id = u2.id
        WHERE f.id = $1
    """
    return await db.fetch_one(query, friendship_id)


async def get_friendship_between_users(db: DatabaseAdapter, user_id: int, friend_id: int) -> Optional[Dict]:
    """获取两个用户之间的朋友关系"""
    query = """
        SELECT f.*, u1.username as user_username, u1.avatar_url as user_avatar,
               u2.username as friend_username, u2.avatar_url as friend_avatar
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        JOIN users u2 ON f.friend_id = u2.id
        WHERE (f.user_id = $1 AND f.friend_id = $2) OR (f.user_id = $2 AND f.friend_id = $1)
    """
    return await db.fetch_one(query, user_id, friend_id)


async def get_user_friends(db: DatabaseAdapter, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的好友列表"""
    where_clause = "WHERE (f.user_id = $1 OR f.friend_id = $1) AND f.status = 'accepted'"
    params = [user_id]

    if status:
        where_clause = "WHERE (f.user_id = $1 OR f.friend_id = $1) AND f.status = $2"
        params = [user_id, status]

    query = f"""
        SELECT f.*,
               CASE WHEN f.user_id = $1 THEN u2.username ELSE u1.username END as friend_username,
               CASE WHEN f.user_id = $1 THEN u2.avatar_url ELSE u1.avatar_url END as friend_avatar,
               CASE WHEN f.user_id = $1 THEN u2.id ELSE u1.id END as friend_id
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        JOIN users u2 ON f.friend_id = u2.id
        {where_clause}
        ORDER BY f.updated_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def get_friend_requests(db: DatabaseAdapter, user_id: int, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的朋友请求"""
    query = """
        SELECT f.*, u1.username as requester_username, u1.avatar_url as requester_avatar
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        WHERE f.friend_id = $1 AND f.status = 'pending'
        ORDER BY f.created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_all(query, user_id, limit, skip)


async def create_friend_request(db: DatabaseAdapter, friend_request: FriendCreate) -> Optional[Dict]:
    """创建朋友请求"""
    # 检查是否已经存在关系
    existing = await get_friendship_between_users(db, friend_request.user_id, friend_request.friend_id)
    if existing:
        return None

    query = """
        INSERT INTO friends (user_id, friend_id, status, created_at, updated_at)
        VALUES ($1, $2, $3, NOW(), NOW())
        RETURNING *
    """
    return await db.fetch_one(query, friend_request.user_id, friend_request.friend_id, friend_request.status)


async def update_friendship(db: DatabaseAdapter, friendship_id: int, update_data: FriendUpdate) -> Optional[Dict]:
    """更新朋友关系"""
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        return await get_friendship_by_id(db, friendship_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(data.keys())])
    query = f"""
        UPDATE friends SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, friendship_id, *data.values())


async def accept_friend_request(db: DatabaseAdapter, friendship_id: int, user_id: int) -> Optional[Dict]:
    """接受朋友请求"""
    # 确保用户是请求的接收者
    friendship = await get_friendship_by_id(db, friendship_id)
    if not friendship or friendship['friend_id'] != user_id:
        return None

    return await update_friendship(db, friendship_id, FriendUpdate(status="accepted"))


async def reject_friend_request(db: DatabaseAdapter, friendship_id: int, user_id: int) -> bool:
    """拒绝朋友请求"""
    # 确保用户是请求的接收者
    friendship = await get_friendship_by_id(db, friendship_id)
    if not friendship or friendship['friend_id'] != user_id:
        return False

    query = "DELETE FROM friends WHERE id = $1"
    result = await db.execute(query, friendship_id)
    return result == "DELETE 1"


async def remove_friend(db: DatabaseAdapter, user_id: int, friend_id: int) -> bool:
    """删除好友关系"""
    query = """
        DELETE FROM friends
        WHERE (user_id = $1 AND friend_id = $2) OR (user_id = $2 AND friend_id = $1)
    """
    result = await db.execute(query, user_id, friend_id)
    return result in ["DELETE 1", "DELETE 2"]


async def get_friends_count(db: DatabaseAdapter, user_id: int) -> int:
    """获取用户好友数量"""
    query = """
        SELECT COUNT(*) as count
        FROM friends
        WHERE (user_id = $1 OR friend_id = $1) AND status = 'accepted'
    """
    result = await db.fetch_one(query, user_id)
    return result['count'] if result else 0


async def get_pending_requests_count(db: DatabaseAdapter, user_id: int) -> int:
    """获取用户待处理请求数量"""
    query = "SELECT COUNT(*) as count FROM friends WHERE friend_id = $1 AND status = 'pending'"
    result = await db.fetch_one(query, user_id)
    return result['count'] if result else 0
