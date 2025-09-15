"""
导师系统服务层
处理导师匹配、关系、会话、评价和交易的业务逻辑
"""
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status

from apps.schemas.mentorship import (
    MentorMatchCreate, MentorshipRelationshipCreate, MentorshipSessionCreate,
    MentorshipReviewCreate, MentorshipTransactionCreate, MentorshipDashboard,
    MentorshipStats
)
from apps.api.v1.repositories import mentorship as mentorship_repo
from apps.api.v1.repositories import user_reputation_stats as reputation_repo
from libs.database.adapters import DatabaseAdapter


async def create_mentor_match(db: DatabaseAdapter, match: MentorMatchCreate, creator_id: int) -> Dict:
    """
    创建导师匹配
    """
    # 检查权限（这里可以添加更复杂的权限检查）
    if creator_id not in [match.mentor_id, match.mentee_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权创建此匹配"
        )

    result = await mentorship_repo.create_mentor_match(db, match)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建导师匹配失败"
        )

    return result


async def create_mentorship_relationship(db: DatabaseAdapter, relationship: MentorshipRelationshipCreate, creator_id: int) -> Dict:
    """
    创建导师关系
    1. 验证权限
    2. 创建关系
    3. 更新统计信息
    """
    if creator_id not in [relationship.mentor_id, relationship.mentee_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权创建此关系"
        )

    result = await mentorship_repo.create_mentorship_relationship(db, relationship)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建导师关系失败"
        )

    # 更新声誉统计
    await reputation_repo.update_mentor_stats(db, relationship.mentor_id, relationship_completed=True)
    await reputation_repo.update_mentee_stats(db, relationship.mentee_id, relationship_completed=True)

    return result


async def create_mentorship_session(db: DatabaseAdapter, session: MentorshipSessionCreate, creator_id: int) -> Dict:
    """
    创建导师会话
    """
    # 检查关系是否存在且用户有权限
    relationship = await mentorship_repo.get_mentorship_relationship_by_id(db, session.relationship_id)
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师关系不存在"
        )

    if creator_id not in [relationship['mentor_id'], relationship['mentee_id']]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此关系创建会话"
        )

    result = await mentorship_repo.create_mentorship_session(db, session)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建导师会话失败"
        )

    return result


async def create_mentorship_review(db: DatabaseAdapter, review: MentorshipReviewCreate, reviewer_id: int) -> Dict:
    """
    创建导师评价
    """
    # 验证评价者权限
    relationship = await mentorship_repo.get_mentorship_relationship_by_id(db, review.relationship_id)
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导师关系不存在"
        )

    if reviewer_id not in [relationship['mentor_id'], relationship['mentee_id']]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权为此关系创建评价"
        )

    result = await mentorship_repo.create_mentorship_review(db, review)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建评价失败"
        )

    # 更新声誉统计
    if review.reviewer_role == 'mentor':
        await reputation_repo.update_mentor_stats(db, reviewer_id)
    else:
        await reputation_repo.update_mentee_stats(db, reviewer_id)

    return result


async def process_mentorship_transaction(db: DatabaseAdapter, transaction: MentorshipTransactionCreate, creator_id: int) -> Dict:
    """
    处理导师交易
    """
    # 这里可以添加支付处理逻辑
    result = await mentorship_repo.create_mentorship_transaction(db, transaction)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建交易记录失败"
        )

    return result


async def get_user_mentorship_dashboard(db: DatabaseAdapter, user_id: int) -> MentorshipDashboard:
    """
    获取用户的导师仪表板
    """
    stats = await mentorship_repo.get_user_mentorship_stats(db, user_id)

    return MentorshipDashboard(
        active_relationships=stats['as_mentor']['active_relationships'] + stats['as_mentee']['active_relationships'],
        completed_relationships=stats['as_mentor']['completed_relationships'] + stats['as_mentee']['completed_relationships'],
        total_sessions=stats['as_mentor']['total_sessions'] + stats['as_mentee']['total_sessions'],
        completed_sessions=stats['as_mentor']['completed_sessions'] + stats['as_mentee']['total_sessions'],  # 简化
        total_earnings=0,  # 这里需要从交易记录计算
        average_rating=0,  # 这里需要从评价计算
        next_session=None  # 这里需要从会话记录计算
    )


async def get_mentorship_stats(db: DatabaseAdapter, user_id: int) -> MentorshipStats:
    """
    获取用户的导师统计
    """
    stats = await mentorship_repo.get_user_mentorship_stats(db, user_id)

    return MentorshipStats(
        total_relationships=stats['as_mentor']['total_relationships'] + stats['as_mentee']['total_relationships'],
        active_relationships=stats['as_mentor']['active_relationships'] + stats['as_mentee']['active_relationships'],
        completed_relationships=stats['as_mentor']['completed_relationships'] + stats['as_mentee']['completed_relationships'],
        total_sessions=stats['as_mentor']['total_sessions'] + stats['as_mentee']['total_sessions'],
        completed_sessions=stats['as_mentor']['completed_sessions'],  # 简化
        total_hours=stats['as_mentor']['total_hours'] + stats['as_mentee']['total_hours'],
        average_rating=0,  # 需要计算
        total_earnings=0,  # 需要计算
        success_rate=0  # 需要计算
    )
