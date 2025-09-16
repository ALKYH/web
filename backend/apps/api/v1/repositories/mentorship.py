"""
导师制 & 服务 - 仓库层
提供服务、导师关系、会话和评价的数据库操作
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.mentorship import (
    Service, ServiceCreate, ServiceUpdate,
    Mentorship, MentorshipCreate, MentorshipUpdate,
    Session, SessionCreate, SessionUpdate,
    Review, ReviewCreate, ReviewUpdate
)
from libs.database.adapters import DatabaseAdapter


# ============ 服务仓库操作 ============

async def get_services(
    db: DatabaseAdapter,
    skill_id: Optional[UUID] = None,
    mentor_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 10
) -> List[Service]:
    """获取服务列表"""
    offset = (page - 1) * page_size
    where_conditions = ["is_active = true"]
    params = []

    if skill_id:
        where_conditions.append("skill_id = $1")
        params.append(skill_id)

    if mentor_id:
        where_conditions.append("mentor_id = $1")
        params.append(mentor_id)

    where_clause = " AND ".join(where_conditions)

    query = f"""
        SELECT id, mentor_id, skill_id, title, description, price, duration_hours, is_active, created_at, updated_at
        FROM services
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    params.extend([page_size, offset])

    rows = await db.fetch_all(query, *params)
    return [Service(**row) for row in rows]


async def get_service_by_id(db: DatabaseAdapter, service_id: UUID) -> Optional[Service]:
    """根据ID获取服务"""
    query = """
        SELECT id, mentor_id, skill_id, title, description, price, duration_hours, is_active, created_at, updated_at
        FROM services
        WHERE id = $1 AND is_active = true
    """
    row = await db.fetch_one(query, service_id)
    return Service(**row) if row else None


async def create_service(
    db: DatabaseAdapter,
    user_id: UUID,
    service_data: ServiceCreate
) -> Optional[Service]:
    """创建服务"""
    query = """
        INSERT INTO services (mentor_id, skill_id, title, description, price, duration_hours, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, mentor_id, skill_id, title, description, price, duration_hours, is_active, created_at, updated_at
    """
    values = (
        user_id,
        service_data.skill_id,
        service_data.title,
        service_data.description,
        service_data.price,
        service_data.duration_hours,
        service_data.is_active
    )
    row = await db.fetch_one(query, *values)
    return Service(**row) if row else None


async def update_service(
    db: DatabaseAdapter,
    service_id: UUID,
    user_id: UUID,
    service_data: ServiceUpdate
) -> Optional[Service]:
    """更新服务"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if service_data.title is not None:
        set_parts.append(f"title = ${param_index}")
        values.append(service_data.title)
        param_index += 1

    if service_data.description is not None:
        set_parts.append(f"description = ${param_index}")
        values.append(service_data.description)
        param_index += 1

    if service_data.price is not None:
        set_parts.append(f"price = ${param_index}")
        values.append(service_data.price)
        param_index += 1

    if service_data.duration_hours is not None:
        set_parts.append(f"duration_hours = ${param_index}")
        values.append(service_data.duration_hours)
        param_index += 1

    if service_data.is_active is not None:
        set_parts.append(f"is_active = ${param_index}")
        values.append(service_data.is_active)
        param_index += 1

    if not set_parts:
        return await get_service_by_id(db, service_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE services
        SET {', '.join(set_parts)}
        WHERE id = ${param_index} AND mentor_id = ${param_index + 1}
        RETURNING id, mentor_id, skill_id, title, description, price, duration_hours, is_active, created_at, updated_at
    """
    values.extend([service_id, user_id])

    row = await db.fetch_one(query, *values)
    return Service(**row) if row else None


async def delete_service(db: DatabaseAdapter, service_id: UUID, user_id: UUID) -> bool:
    """删除服务（软删除）"""
    query = """
        UPDATE services
        SET is_active = false, updated_at = NOW()
        WHERE id = $1 AND mentor_id = $2 AND is_active = true
    """
    result = await db.execute(query, service_id, user_id)
    return result == "UPDATE 1"


async def get_services_by_mentor(db: DatabaseAdapter, mentor_id: UUID) -> List[Service]:
    """获取导师的服务列表"""
    query = """
        SELECT id, mentor_id, skill_id, title, description, price, duration_hours, is_active, created_at, updated_at
        FROM services
        WHERE mentor_id = $1
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, mentor_id)
    return [Service(**row) for row in rows]


# ============ 导师关系仓库操作 ============

async def create_mentorship(
    db: DatabaseAdapter,
    mentorship_data: MentorshipCreate
) -> Optional[Mentorship]:
    """创建导师关系"""
    query = """
        INSERT INTO mentorships (mentor_id, mentee_id, service_id, status)
        VALUES ($1, $2, $3, $4)
        RETURNING id, mentor_id, mentee_id, service_id, status, created_at, updated_at
    """
    values = (
        mentorship_data.mentor_id,
        mentorship_data.mentee_id,
        mentorship_data.service_id,
        mentorship_data.status.value
    )
    row = await db.fetch_one(query, *values)
    return Mentorship(**row) if row else None


async def get_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    user_id: UUID
) -> Optional[Mentorship]:
    """获取导师关系"""
    query = """
        SELECT id, mentor_id, mentee_id, service_id, status, created_at, updated_at
        FROM mentorships
        WHERE id = $1 AND (mentor_id = $2 OR mentee_id = $2)
    """
    row = await db.fetch_one(query, mentorship_id, user_id)
    return Mentorship(**row) if row else None


async def update_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    user_id: UUID,
    mentorship_data: MentorshipUpdate
) -> Optional[Mentorship]:
    """更新导师关系"""
    if mentorship_data.status is None:
        return await get_mentorship(db, mentorship_id, user_id)

    query = """
        UPDATE mentorships
        SET status = $1, updated_at = NOW()
        WHERE id = $2 AND (mentor_id = $3 OR mentee_id = $3)
        RETURNING id, mentor_id, mentee_id, service_id, status, created_at, updated_at
    """
    values = (mentorship_data.status.value, mentorship_id, user_id)
    row = await db.fetch_one(query, *values)
    return Mentorship(**row) if row else None


async def get_mentorships_by_user(
    db: DatabaseAdapter,
    user_id: UUID,
    role: str = "all"
) -> List[Mentorship]:
    """获取用户的导师关系列表"""
    if role == "mentor":
        where_clause = "mentor_id = $1"
    elif role == "mentee":
        where_clause = "mentee_id = $1"
    else:
        where_clause = "(mentor_id = $1 OR mentee_id = $1)"

    query = f"""
        SELECT id, mentor_id, mentee_id, service_id, status, created_at, updated_at
        FROM mentorships
        WHERE {where_clause}
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, user_id)
    return [Mentorship(**row) for row in rows]


# ============ 会话仓库操作 ============

async def create_session(
    db: DatabaseAdapter,
    session_data: SessionCreate,
    user_id: UUID
) -> Optional[Session]:
    """创建会话"""
    # 验证用户是否为导师关系的一部分
    mentorship = await get_mentorship(db, session_data.mentorship_id, user_id)
    if not mentorship:
        return None

    query = """
        INSERT INTO sessions (mentorship_id, scheduled_at, duration_minutes, status, mentor_notes, mentee_notes)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, mentorship_id, scheduled_at, duration_minutes, status, mentor_notes, mentee_notes, created_at, updated_at
    """
    values = (
        session_data.mentorship_id,
        session_data.scheduled_at,
        session_data.duration_minutes,
        session_data.status.value,
        session_data.mentor_notes,
        session_data.mentee_notes
    )
    row = await db.fetch_one(query, *values)
    return Session(**row) if row else None


async def get_session(
    db: DatabaseAdapter,
    session_id: UUID,
    user_id: UUID
) -> Optional[Session]:
    """获取会话"""
    query = """
        SELECT s.id, s.mentorship_id, s.scheduled_at, s.duration_minutes, s.status, s.mentor_notes, s.mentee_notes, s.created_at, s.updated_at
        FROM sessions s
        JOIN mentorships m ON s.mentorship_id = m.id
        WHERE s.id = $1 AND (m.mentor_id = $2 OR m.mentee_id = $2)
    """
    row = await db.fetch_one(query, session_id, user_id)
    return Session(**row) if row else None


async def update_session(
    db: DatabaseAdapter,
    session_id: UUID,
    user_id: UUID,
    session_data: SessionUpdate
) -> Optional[Session]:
    """更新会话"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if session_data.scheduled_at is not None:
        set_parts.append(f"scheduled_at = ${param_index}")
        values.append(session_data.scheduled_at)
        param_index += 1

    if session_data.duration_minutes is not None:
        set_parts.append(f"duration_minutes = ${param_index}")
        values.append(session_data.duration_minutes)
        param_index += 1

    if session_data.status is not None:
        set_parts.append(f"status = ${param_index}")
        values.append(session_data.status.value)
        param_index += 1

    if session_data.mentor_notes is not None:
        set_parts.append(f"mentor_notes = ${param_index}")
        values.append(session_data.mentor_notes)
        param_index += 1

    if session_data.mentee_notes is not None:
        set_parts.append(f"mentee_notes = ${param_index}")
        values.append(session_data.mentee_notes)
        param_index += 1

    if not set_parts:
        return await get_session(db, session_id, user_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE sessions
        SET {', '.join(set_parts)}
        WHERE id = ${param_index}
        AND mentorship_id IN (
            SELECT id FROM mentorships
            WHERE (mentor_id = ${param_index + 1} OR mentee_id = ${param_index + 1})
        )
        RETURNING id, mentorship_id, scheduled_at, duration_minutes, status, mentor_notes, mentee_notes, created_at, updated_at
    """
    values.extend([session_id, user_id])

    row = await db.fetch_one(query, *values)
    return Session(**row) if row else None


async def get_sessions_by_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    user_id: UUID
) -> List[Session]:
    """获取导师关系的会话列表"""
    query = """
        SELECT s.id, s.mentorship_id, s.scheduled_at, s.duration_minutes, s.status, s.mentor_notes, s.mentee_notes, s.created_at, s.updated_at
        FROM sessions s
        JOIN mentorships m ON s.mentorship_id = m.id
        WHERE s.mentorship_id = $1 AND (m.mentor_id = $2 OR m.mentee_id = $2)
        ORDER BY s.scheduled_at DESC
    """
    rows = await db.fetch_all(query, mentorship_id, user_id)
    return [Session(**row) for row in rows]


# ============ 评价仓库操作 ============

async def create_review(
    db: DatabaseAdapter,
    review_data: ReviewCreate,
    reviewer_id: UUID
) -> Optional[Review]:
    """创建评价"""
    # 验证用户是否为导师关系的一部分且关系已完成
    mentorship = await get_mentorship(db, review_data.mentorship_id, reviewer_id)
    if not mentorship or mentorship.status.value != "completed":
        return None

    # 检查是否已经评价过
    existing_review = await get_review_by_mentorship_and_reviewer(
        db, review_data.mentorship_id, reviewer_id
    )
    if existing_review:
        return None

    query = """
        INSERT INTO reviews (mentorship_id, reviewer_id, reviewee_id, rating, comment)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, mentorship_id, reviewer_id, reviewee_id, rating, comment, created_at, updated_at
    """
    # 确定被评价者
    reviewee_id = (
        mentorship.mentor_id if reviewer_id == mentorship.mentee_id
        else mentorship.mentee_id
    )

    values = (
        review_data.mentorship_id,
        reviewer_id,
        reviewee_id,
        review_data.rating,
        review_data.comment
    )
    row = await db.fetch_one(query, *values)
    return Review(**row) if row else None


async def get_review_by_id(db: DatabaseAdapter, review_id: UUID) -> Optional[Review]:
    """根据ID获取评价"""
    query = """
        SELECT id, mentorship_id, reviewer_id, reviewee_id, rating, comment, created_at, updated_at
        FROM reviews
        WHERE id = $1
    """
    row = await db.fetch_one(query, review_id)
    return Review(**row) if row else None


async def update_review(
    db: DatabaseAdapter,
    review_id: UUID,
    reviewer_id: UUID,
    review_data: ReviewUpdate
) -> Optional[Review]:
    """更新评价"""
    # 构建动态更新语句
    set_parts = []
    values = []
    param_index = 1

    if review_data.rating is not None:
        set_parts.append(f"rating = ${param_index}")
        values.append(review_data.rating)
        param_index += 1

    if review_data.comment is not None:
        set_parts.append(f"comment = ${param_index}")
        values.append(review_data.comment)
        param_index += 1

    if not set_parts:
        return await get_review_by_id(db, review_id)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE reviews
        SET {', '.join(set_parts)}
        WHERE id = ${param_index} AND reviewer_id = ${param_index + 1}
        RETURNING id, mentorship_id, reviewer_id, reviewee_id, rating, comment, created_at, updated_at
    """
    values.extend([review_id, reviewer_id])

    row = await db.fetch_one(query, *values)
    return Review(**row) if row else None


async def get_reviews_by_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID
) -> List[Review]:
    """获取导师关系的所有评价"""
    query = """
        SELECT id, mentorship_id, reviewer_id, reviewee_id, rating, comment, created_at, updated_at
        FROM reviews
        WHERE mentorship_id = $1
        ORDER BY created_at DESC
    """
    rows = await db.fetch_all(query, mentorship_id)
    return [Review(**row) for row in rows]


async def get_review_by_mentorship_and_reviewer(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    reviewer_id: UUID
) -> Optional[Review]:
    """获取特定用户对导师关系的评价"""
    query = """
        SELECT id, mentorship_id, reviewer_id, reviewee_id, rating, comment, created_at, updated_at
        FROM reviews
        WHERE mentorship_id = $1 AND reviewer_id = $2
    """
    row = await db.fetch_one(query, mentorship_id, reviewer_id)
    return Review(**row) if row else None