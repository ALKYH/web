"""
用户声誉统计系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.user_reputation_stats import UserReputationStatsCreate, UserReputationStatsUpdate
from libs.database.adapters import DatabaseAdapter


async def get_reputation_stats_by_user_id(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """根据用户ID获取声誉统计"""
    query = """
        SELECT urs.*, u.username, u.avatar_url, u.role
        FROM user_reputation_stats urs
        JOIN users u ON urs.user_id = u.id
        WHERE urs.user_id = $1
    """
    return await db.fetch_one(query, user_id)


async def create_reputation_stats(db: DatabaseAdapter, stats: UserReputationStatsCreate) -> Optional[Dict]:
    """创建用户声誉统计"""
    query = """
        INSERT INTO user_reputation_stats (
            user_id, mentor_rating_avg, mentor_rating_count, mentor_relationships_total,
            mentor_relationships_completed, mentor_sessions_completed, mentor_hours_taught,
            mentor_success_rate, mentor_response_rate, mentor_punctuality_rate,
            mentee_rating_avg, mentee_rating_count, mentee_relationships_total,
            mentee_relationships_completed, mentee_sessions_attended, mentee_hours_learned,
            mentee_completion_rate, mentee_attendance_rate, reputation_score,
            trust_level, badges, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, NOW(), NOW())
        RETURNING *
    """
    values = (
        stats.user_id, stats.mentor_rating_avg, stats.mentor_rating_count,
        stats.mentor_relationships_total, stats.mentor_relationships_completed,
        stats.mentor_sessions_completed, stats.mentor_hours_taught,
        stats.mentor_success_rate, stats.mentor_response_rate, stats.mentor_punctuality_rate,
        stats.mentee_rating_avg, stats.mentee_rating_count, stats.mentee_relationships_total,
        stats.mentee_relationships_completed, stats.mentee_sessions_attended,
        stats.mentee_hours_learned, stats.mentee_completion_rate, stats.mentee_attendance_rate,
        stats.reputation_score, stats.trust_level, stats.badges or []
    )
    return await db.fetch_one(query, *values)


async def update_reputation_stats(db: DatabaseAdapter, user_id: int, stats: UserReputationStatsUpdate) -> Optional[Dict]:
    """更新用户声誉统计"""
    update_data = stats.model_dump(exclude_unset=True)
    if not update_data:
        return await get_reputation_stats_by_user_id(db, user_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
    query = f"""
        UPDATE user_reputation_stats SET {set_clause}, updated_at = NOW()
        WHERE user_id = $1
        RETURNING *
    """
    return await db.fetch_one(query, user_id, *update_data.values())


async def update_mentor_stats(db: DatabaseAdapter, user_id: int, relationship_completed: bool = False, session_completed: bool = False, hours_taught: float = 0, rating: Optional[float] = None) -> Optional[Dict]:
    """更新导师统计信息"""
    # 获取当前统计
    current_stats = await get_reputation_stats_by_user_id(db, user_id)
    if not current_stats:
        # 如果不存在，创建默认统计
        default_stats = UserReputationStatsCreate(user_id=user_id)
        current_stats = await create_reputation_stats(db, default_stats)
        if not current_stats:
            return None

    # 计算更新值
    updates = {}

    if relationship_completed:
        updates['mentor_relationships_completed'] = current_stats['mentor_relationships_completed'] + 1
        updates['mentor_relationships_total'] = current_stats['mentor_relationships_total'] + 1
    else:
        updates['mentor_relationships_total'] = current_stats['mentor_relationships_total'] + 1

    if session_completed:
        updates['mentor_sessions_completed'] = current_stats['mentor_sessions_completed'] + 1

    if hours_taught > 0:
        updates['mentor_hours_taught'] = current_stats['mentor_hours_taught'] + hours_taught

    if rating is not None:
        current_count = current_stats['mentor_rating_count']
        current_avg = current_stats['mentor_rating_avg']
        new_count = current_count + 1
        new_avg = (current_avg * current_count + rating) / new_count
        updates['mentor_rating_count'] = new_count
        updates['mentor_rating_avg'] = new_avg

    # 更新声誉分数（简化算法）
    if updates:
        current_score = current_stats['reputation_score']
        score_increase = len(updates) * 5  # 每次更新增加5分
        updates['reputation_score'] = current_score + score_increase

        # 更新最后活跃时间
        updates['last_active_as_mentor'] = 'NOW()'

    if updates:
        update_stats = UserReputationStatsUpdate(**updates)
        return await update_reputation_stats(db, user_id, update_stats)

    return current_stats


async def update_mentee_stats(db: DatabaseAdapter, user_id: int, relationship_completed: bool = False, session_attended: bool = False, hours_learned: float = 0, rating: Optional[float] = None) -> Optional[Dict]:
    """更新学员统计信息"""
    # 获取当前统计
    current_stats = await get_reputation_stats_by_user_id(db, user_id)
    if not current_stats:
        # 如果不存在，创建默认统计
        default_stats = UserReputationStatsCreate(user_id=user_id)
        current_stats = await create_reputation_stats(db, default_stats)
        if not current_stats:
            return None

    # 计算更新值
    updates = {}

    if relationship_completed:
        updates['mentee_relationships_completed'] = current_stats['mentee_relationships_completed'] + 1
        updates['mentee_relationships_total'] = current_stats['mentee_relationships_total'] + 1
    else:
        updates['mentee_relationships_total'] = current_stats['mentee_relationships_total'] + 1

    if session_attended:
        updates['mentee_sessions_attended'] = current_stats['mentee_sessions_attended'] + 1

    if hours_learned > 0:
        updates['mentee_hours_learned'] = current_stats['mentee_hours_learned'] + hours_learned

    if rating is not None:
        current_count = current_stats['mentee_rating_count']
        current_avg = current_stats['mentee_rating_avg']
        new_count = current_count + 1
        new_avg = (current_avg * current_count + rating) / new_count
        updates['mentee_rating_count'] = new_count
        updates['mentee_rating_avg'] = new_avg

    # 更新最后活跃时间
    if updates:
        updates['last_active_as_mentee'] = 'NOW()'

    if updates:
        update_stats = UserReputationStatsUpdate(**updates)
        return await update_reputation_stats(db, user_id, update_stats)

    return current_stats


async def get_top_mentors(db: DatabaseAdapter, limit: int = 10) -> List[Dict]:
    """获取顶级导师排行榜"""
    query = """
        SELECT urs.*, u.username, u.avatar_url, u.role
        FROM user_reputation_stats urs
        JOIN users u ON urs.user_id = u.id
        WHERE urs.mentor_rating_count > 0
        ORDER BY urs.reputation_score DESC, urs.mentor_rating_avg DESC, urs.mentor_sessions_completed DESC
        LIMIT $1
    """
    return await db.fetch_all(query, limit)


async def get_reputation_leaderboard(db: DatabaseAdapter, trust_level: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """获取声誉排行榜"""
    where_clause = "WHERE 1=1"
    params = []

    if trust_level:
        where_clause += " AND urs.trust_level = $1"
        params.append(trust_level)

    query = f"""
        SELECT urs.*, u.username, u.avatar_url, u.role,
               ROW_NUMBER() OVER (ORDER BY urs.reputation_score DESC) as rank
        FROM user_reputation_stats urs
        JOIN users u ON urs.user_id = u.id
        {where_clause}
        ORDER BY urs.reputation_score DESC, urs.mentor_rating_avg DESC
        LIMIT ${len(params) + 1}
    """
    params.append(limit)
    return await db.fetch_all(query, *params)


async def calculate_trust_level(db: DatabaseAdapter, user_id: int) -> Optional[str]:
    """计算用户信任等级"""
    stats = await get_reputation_stats_by_user_id(db, user_id)
    if not stats:
        return None

    score = stats['reputation_score']
    mentor_sessions = stats['mentor_sessions_completed']
    mentor_rating = stats['mentor_rating_avg']

    # 信任等级算法（可以根据业务需求调整）
    if score >= 1000 and mentor_sessions >= 50 and mentor_rating >= 4.5:
        return 'master'
    elif score >= 500 and mentor_sessions >= 20 and mentor_rating >= 4.0:
        return 'expert'
    elif score >= 200 and mentor_sessions >= 10 and mentor_rating >= 3.5:
        return 'mentor'
    elif score >= 50 and mentor_sessions >= 5:
        return 'contributor'
    elif score >= 10:
        return 'learner'
    else:
        return 'newcomer'


async def update_trust_level(db: DatabaseAdapter, user_id: int) -> Optional[Dict]:
    """更新用户信任等级"""
    new_level = await calculate_trust_level(db, user_id)
    if new_level:
        update_data = UserReputationStatsUpdate(trust_level=new_level)
        return await update_reputation_stats(db, user_id, update_data)
    return None


async def get_reputation_badges(db: DatabaseAdapter, user_id: int) -> List[Dict]:
    """获取用户的声誉徽章"""
    stats = await get_reputation_stats_by_user_id(db, user_id)
    if not stats or not stats.get('badges'):
        return []

    # 这里可以实现更复杂的徽章逻辑
    badges = []
    for badge_name in stats['badges']:
        badges.append({
            'name': badge_name,
            'earned_at': stats['created_at'],  # 简化处理
            'description': f'获得 {badge_name} 徽章'
        })

    return badges


async def get_reputation_stats_summary(db: DatabaseAdapter) -> Dict[str, Any]:
    """获取声誉统计摘要"""
    query = """
        SELECT
            COUNT(*) as total_users,
            AVG(reputation_score) as average_score,
            COUNT(CASE WHEN trust_level = 'master' THEN 1 END) as master_count,
            COUNT(CASE WHEN trust_level = 'expert' THEN 1 END) as expert_count,
            COUNT(CASE WHEN trust_level = 'mentor' THEN 1 END) as mentor_count,
            MAX(reputation_score) as highest_score,
            MIN(reputation_score) as lowest_score
        FROM user_reputation_stats
    """
    result = await db.fetch_one(query)
    return result or {}
