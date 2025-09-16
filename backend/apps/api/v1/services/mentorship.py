"""
导师制 & 服务 - 服务层
提供服务、导师关系、会话和评价的业务逻辑
"""
from typing import List, Optional
from uuid import UUID

from apps.schemas.mentorship import (
    Service, ServiceCreate, ServiceUpdate,
    Mentorship, MentorshipCreate, MentorshipUpdate,
    Session, SessionCreate, SessionUpdate,
    Review, ReviewCreate, ReviewUpdate
)
from apps.api.v1.repositories import mentorship as mentorship_repo
from libs.database.adapters import DatabaseAdapter


# ============ 服务管理 ============

async def get_services(
    db: DatabaseAdapter,
    skill_id: Optional[UUID] = None,
    mentor_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 10
) -> List[Service]:
    """获取服务列表"""
    return await mentorship_repo.get_services(
        db=db,
        skill_id=skill_id,
        mentor_id=mentor_id,
        page=page,
        page_size=page_size
    )


async def get_service_by_id(db: DatabaseAdapter, service_id: UUID) -> Optional[Service]:
    """根据ID获取服务"""
    return await mentorship_repo.get_service_by_id(db, service_id)


async def create_service(
    db: DatabaseAdapter,
    user_id: UUID,
    service_data: ServiceCreate
) -> Optional[Service]:
    """创建服务"""
    return await mentorship_repo.create_service(
        db=db,
        user_id=user_id,
        service_data=service_data
    )


async def update_service(
    db: DatabaseAdapter,
    service_id: UUID,
    user_id: UUID,
    service_data: ServiceUpdate
) -> Optional[Service]:
    """更新服务"""
    return await mentorship_repo.update_service(
        db=db,
        service_id=service_id,
        user_id=user_id,
        service_data=service_data
    )


async def delete_service(db: DatabaseAdapter, service_id: UUID, user_id: UUID) -> bool:
    """删除服务"""
    return await mentorship_repo.delete_service(db, service_id, user_id)


async def get_services_by_mentor(db: DatabaseAdapter, mentor_id: UUID) -> List[Service]:
    """获取导师的服务列表"""
    return await mentorship_repo.get_services_by_mentor(db, mentor_id)


# ============ 导师关系管理 ============

async def create_mentorship(
    db: DatabaseAdapter,
    mentorship_data: MentorshipCreate
) -> Optional[Mentorship]:
    """创建导师关系"""
    return await mentorship_repo.create_mentorship(db, mentorship_data)


async def get_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    user_id: UUID
) -> Optional[Mentorship]:
    """获取导师关系"""
    return await mentorship_repo.get_mentorship(db, mentorship_id, user_id)


async def update_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    user_id: UUID,
    mentorship_data: MentorshipUpdate
) -> Optional[Mentorship]:
    """更新导师关系"""
    return await mentorship_repo.update_mentorship(
        db=db,
        mentorship_id=mentorship_id,
        user_id=user_id,
        mentorship_data=mentorship_data
    )


async def get_mentorships_by_user(
    db: DatabaseAdapter,
    user_id: UUID,
    role: str = "all"  # "mentor", "mentee", "all"
) -> List[Mentorship]:
    """获取用户的导师关系列表"""
    return await mentorship_repo.get_mentorships_by_user(db, user_id, role)


# ============ 会话管理 ============

async def create_session(
    db: DatabaseAdapter,
    session_data: SessionCreate,
    user_id: UUID
) -> Optional[Session]:
    """创建会话"""
    return await mentorship_repo.create_session(
        db=db,
        session_data=session_data,
        user_id=user_id
    )


async def get_session(
    db: DatabaseAdapter,
    session_id: UUID,
    user_id: UUID
) -> Optional[Session]:
    """获取会话"""
    return await mentorship_repo.get_session(db, session_id, user_id)


async def update_session(
    db: DatabaseAdapter,
    session_id: UUID,
    user_id: UUID,
    session_data: SessionUpdate
) -> Optional[Session]:
    """更新会话"""
    return await mentorship_repo.update_session(
        db=db,
        session_id=session_id,
        user_id=user_id,
        session_data=session_data
    )


async def get_sessions_by_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID,
    user_id: UUID
) -> List[Session]:
    """获取导师关系的会话列表"""
    return await mentorship_repo.get_sessions_by_mentorship(
        db, mentorship_id, user_id
    )


# ============ 评价管理 ============

async def create_review(
    db: DatabaseAdapter,
    review_data: ReviewCreate,
    reviewer_id: UUID
) -> Optional[Review]:
    """创建评价"""
    return await mentorship_repo.create_review(
        db=db,
        review_data=review_data,
        reviewer_id=reviewer_id
    )


async def get_review_by_id(db: DatabaseAdapter, review_id: UUID) -> Optional[Review]:
    """根据ID获取评价"""
    return await mentorship_repo.get_review_by_id(db, review_id)


async def update_review(
    db: DatabaseAdapter,
    review_id: UUID,
    reviewer_id: UUID,
    review_data: ReviewUpdate
) -> Optional[Review]:
    """更新评价"""
    return await mentorship_repo.update_review(
        db=db,
        review_id=review_id,
        reviewer_id=reviewer_id,
        review_data=review_data
    )


async def get_reviews_by_mentorship(
    db: DatabaseAdapter,
    mentorship_id: UUID
) -> List[Review]:
    """获取导师关系的所有评价"""
    return await mentorship_repo.get_reviews_by_mentorship(db, mentorship_id)