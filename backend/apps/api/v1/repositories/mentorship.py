"""
导师系统相关的CRUD操作
"""
from typing import Optional, List, Dict, Any
from apps.schemas.mentorship import (
    MentorMatchCreate, MentorMatchUpdate,
    MentorshipRelationshipCreate, MentorshipRelationshipUpdate,
    MentorshipSessionCreate, MentorshipSessionUpdate,
    MentorshipReviewCreate, MentorshipReviewUpdate,
    MentorshipTransactionCreate, MentorshipTransactionUpdate
)
from libs.database.adapters import DatabaseAdapter


# 导师匹配相关操作

async def get_mentor_match_by_id(db: DatabaseAdapter, match_id: int) -> Optional[Dict]:
    """根据ID获取导师匹配"""
    query = "SELECT * FROM mentor_matches WHERE id = $1"
    return await db.fetch_one(query, match_id)


async def get_mentor_matches_for_user(db: DatabaseAdapter, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的导师匹配"""
    where_clause = "WHERE mentor_id = $1 OR mentee_id = $1"
    params = [user_id]

    if status:
        where_clause += " AND status = $2"
        params.append(status)

    query = f"""
        SELECT mm.*, u1.username as mentor_username, u2.username as mentee_username,
               s.name as skill_name
        FROM mentor_matches mm
        JOIN users u1 ON mm.mentor_id = u1.id
        JOIN users u2 ON mm.mentee_id = u2.id
        LEFT JOIN skills s ON mm.skill_id = s.id
        {where_clause}
        ORDER BY mm.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_mentor_match(db: DatabaseAdapter, match: MentorMatchCreate) -> Optional[Dict]:
    """创建导师匹配"""
    query = """
        INSERT INTO mentor_matches (
            mentor_id, mentee_id, skill_id, learning_need_id, mentor_skill_id,
            match_score, match_algorithm, match_factors, status, created_at, updated_at, expires_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW(), NOW() + INTERVAL '7 days')
        RETURNING *
    """
    values = (
        match.mentor_id, match.mentee_id, match.skill_id, match.learning_need_id,
        match.mentor_skill_id, match.match_score, match.match_algorithm,
        match.match_factors, match.status
    )
    return await db.fetch_one(query, *values)


async def update_mentor_match(db: DatabaseAdapter, match_id: int, update_data: MentorMatchUpdate) -> Optional[Dict]:
    """更新导师匹配"""
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        return await get_mentor_match_by_id(db, match_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(data.keys())])
    query = f"""
        UPDATE mentor_matches SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, match_id, *data.values())


# 导师关系相关操作

async def get_mentorship_relationship_by_id(db: DatabaseAdapter, relationship_id: int) -> Optional[Dict]:
    """根据ID获取导师关系"""
    query = """
        SELECT mr.*, u1.username as mentor_username, u2.username as mentee_username,
               s.name as skill_name
        FROM mentorship_relationships mr
        JOIN users u1 ON mr.mentor_id = u1.id
        JOIN users u2 ON mr.mentee_id = u2.id
        LEFT JOIN skills s ON mr.skill_id = s.id
        WHERE mr.id = $1
    """
    return await db.fetch_one(query, relationship_id)


async def get_mentorship_relationships_for_user(db: DatabaseAdapter, user_id: int, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取用户的导师关系"""
    where_clause = "WHERE mentor_id = $1 OR mentee_id = $1"
    params = [user_id]

    if status:
        where_clause += " AND status = $2"
        params.append(status)

    query = f"""
        SELECT mr.*, u1.username as mentor_username, u2.username as mentee_username,
               s.name as skill_name
        FROM mentorship_relationships mr
        JOIN users u1 ON mr.mentor_id = u1.id
        JOIN users u2 ON mr.mentee_id = u2.id
        LEFT JOIN skills s ON mr.skill_id = s.id
        {where_clause}
        ORDER BY mr.created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([limit, skip])
    return await db.fetch_all(query, *params)


async def create_mentorship_relationship(db: DatabaseAdapter, relationship: MentorshipRelationshipCreate) -> Optional[Dict]:
    """创建导师关系"""
    query = """
        INSERT INTO mentorship_relationships (
            mentor_id, mentee_id, skill_id, match_id, title, description,
            learning_goals, success_criteria, start_date, estimated_end_date,
            total_sessions_planned, session_duration_minutes, hourly_rate,
            currency, total_amount, payment_schedule, relationship_type,
            preferred_communication, meeting_frequency, timezone, status,
            created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, NOW(), NOW())
        RETURNING *
    """
    values = (
        relationship.mentor_id, relationship.mentee_id, relationship.skill_id,
        relationship.match_id, relationship.title, relationship.description,
        relationship.learning_goals, relationship.success_criteria,
        relationship.start_date, relationship.estimated_end_date,
        relationship.total_sessions_planned, relationship.session_duration_minutes,
        relationship.hourly_rate, relationship.currency, relationship.total_amount,
        relationship.payment_schedule, relationship.relationship_type,
        relationship.preferred_communication, relationship.meeting_frequency,
        relationship.timezone, relationship.status
    )
    return await db.fetch_one(query, *values)


async def update_mentorship_relationship(db: DatabaseAdapter, relationship_id: int, update_data: MentorshipRelationshipUpdate) -> Optional[Dict]:
    """更新导师关系"""
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        return await get_mentorship_relationship_by_id(db, relationship_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(data.keys())])
    query = f"""
        UPDATE mentorship_relationships SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, relationship_id, *data.values())


# 导师会话相关操作

async def get_mentorship_session_by_id(db: DatabaseAdapter, session_id: int) -> Optional[Dict]:
    """根据ID获取导师会话"""
    query = "SELECT * FROM mentorship_sessions WHERE id = $1"
    return await db.fetch_one(query, session_id)


async def get_sessions_for_relationship(db: DatabaseAdapter, relationship_id: int, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取关系的所有会话"""
    query = """
        SELECT * FROM mentorship_sessions
        WHERE relationship_id = $1
        ORDER BY session_number
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_all(query, relationship_id, limit, skip)


async def create_mentorship_session(db: DatabaseAdapter, session: MentorshipSessionCreate) -> Optional[Dict]:
    """创建导师会话"""
    query = """
        INSERT INTO mentorship_sessions (
            relationship_id, session_number, scheduled_at, duration_minutes,
            agenda, status, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        RETURNING *
    """
    values = (
        session.relationship_id, session.session_number, session.scheduled_at,
        session.duration_minutes, session.agenda, session.status
    )
    return await db.fetch_one(query, *values)


async def update_mentorship_session(db: DatabaseAdapter, session_id: int, update_data: MentorshipSessionUpdate) -> Optional[Dict]:
    """更新导师会话"""
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        return await get_mentorship_session_by_id(db, session_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(data.keys())])
    query = f"""
        UPDATE mentorship_sessions SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, session_id, *data.values())


# 导师评价相关操作

async def get_mentorship_review_by_id(db: DatabaseAdapter, review_id: int) -> Optional[Dict]:
    """根据ID获取导师评价"""
    query = """
        SELECT mr.*, u1.username as reviewer_username, u2.username as reviewee_username
        FROM mentorship_reviews mr
        JOIN users u1 ON mr.reviewer_id = u1.id
        JOIN users u2 ON mr.reviewee_id = u2.id
        WHERE mr.id = $1
    """
    return await db.fetch_one(query, review_id)


async def get_reviews_for_relationship(db: DatabaseAdapter, relationship_id: int) -> List[Dict]:
    """获取关系的所有评价"""
    query = """
        SELECT mr.*, u1.username as reviewer_username, u2.username as reviewee_username
        FROM mentorship_reviews mr
        JOIN users u1 ON mr.reviewer_id = u1.id
        JOIN users u2 ON mr.reviewee_id = u2.id
        WHERE mr.relationship_id = $1
        ORDER BY mr.created_at DESC
    """
    return await db.fetch_all(query, relationship_id)


async def create_mentorship_review(db: DatabaseAdapter, review: MentorshipReviewCreate) -> Optional[Dict]:
    """创建导师评价"""
    query = """
        INSERT INTO mentorship_reviews (
            relationship_id, reviewer_id, reviewee_id, reviewer_role,
            overall_rating, communication_rating, expertise_rating,
            timeliness_rating, value_rating, professionalism_rating,
            comment, pros, areas_for_improvement, would_recommend,
            would_work_again, positive_tags, negative_tags,
            learning_objectives_met, skill_improvement, is_public,
            is_verified, verification_notes, created_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, NOW())
        RETURNING *
    """
    values = (
        review.relationship_id, review.reviewer_id, review.reviewee_id,
        review.reviewer_role, review.overall_rating, review.communication_rating,
        review.expertise_rating, review.timeliness_rating, review.value_rating,
        review.professionalism_rating, review.comment, review.pros,
        review.areas_for_improvement, review.would_recommend,
        review.would_work_again, review.positive_tags, review.negative_tags,
        review.learning_objectives_met, review.skill_improvement,
        review.is_public, review.is_verified, review.verification_notes
    )
    return await db.fetch_one(query, *values)


# 导师交易相关操作

async def get_mentorship_transaction_by_id(db: DatabaseAdapter, transaction_id: int) -> Optional[Dict]:
    """根据ID获取导师交易"""
    query = "SELECT * FROM mentorship_transactions WHERE id = $1"
    return await db.fetch_one(query, transaction_id)


async def get_transactions_for_relationship(db: DatabaseAdapter, relationship_id: int, skip: int = 0, limit: int = 50) -> List[Dict]:
    """获取关系的所有交易"""
    query = """
        SELECT * FROM mentorship_transactions
        WHERE relationship_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    return await db.fetch_all(query, relationship_id, limit, skip)


async def create_mentorship_transaction(db: DatabaseAdapter, transaction: MentorshipTransactionCreate) -> Optional[Dict]:
    """创建导师交易"""
    query = """
        INSERT INTO mentorship_transactions (
            relationship_id, session_id, transaction_type, amount, currency,
            payment_method, payment_status, external_transaction_id,
            payment_gateway, description, reference_number, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
        RETURNING *
    """
    values = (
        transaction.relationship_id, transaction.session_id, transaction.transaction_type,
        transaction.amount, transaction.currency, transaction.payment_method,
        transaction.payment_status, transaction.external_transaction_id,
        transaction.payment_gateway, transaction.description, transaction.reference_number
    )
    return await db.fetch_one(query, *values)


async def update_mentorship_transaction(db: DatabaseAdapter, transaction_id: int, update_data: MentorshipTransactionUpdate) -> Optional[Dict]:
    """更新导师交易"""
    data = update_data.model_dump(exclude_unset=True)
    if not data:
        return await get_mentorship_transaction_by_id(db, transaction_id)

    set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(data.keys())])
    query = f"""
        UPDATE mentorship_transactions SET {set_clause}, updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    return await db.fetch_one(query, transaction_id, *data.values())


# 统计相关操作

async def get_user_mentorship_stats(db: DatabaseAdapter, user_id: int) -> Dict[str, Any]:
    """获取用户的导师统计信息"""
    # 作为导师的统计
    mentor_query = """
        SELECT
            COUNT(*) as total_relationships,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_relationships,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_relationships,
            COALESCE(SUM(total_hours_spent), 0) as total_hours
        FROM mentorship_relationships
        WHERE mentor_id = $1
    """
    mentor_stats = await db.fetch_one(mentor_query, user_id)

    # 作为学员的统计
    mentee_query = """
        SELECT
            COUNT(*) as total_relationships,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_relationships,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_relationships,
            COALESCE(SUM(total_hours_spent), 0) as total_hours
        FROM mentorship_relationships
        WHERE mentee_id = $1
    """
    mentee_stats = await db.fetch_one(mentee_query, user_id)

    return {
        "as_mentor": mentor_stats,
        "as_mentee": mentee_stats
    }
