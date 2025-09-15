"""
用户声誉统计服务层
处理用户声誉统计相关的业务逻辑
"""
from typing import Optional, List
from fastapi import HTTPException, status

from apps.schemas.user_reputation_stats import UserReputationStatsDetail, ReputationLeaderboard
from apps.api.v1.repositories import user_reputation_stats as reputation_repo
from libs.database.adapters import DatabaseAdapter


async def get_user_reputation(db: DatabaseAdapter, user_id: int) -> UserReputationStatsDetail:
    """
    获取用户声誉统计
    """
    stats = await reputation_repo.get_reputation_stats_by_user_id(db, user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户声誉统计不存在"
        )

    return UserReputationStatsDetail(**stats)


async def get_reputation_leaderboard(db: DatabaseAdapter, trust_level: Optional[str] = None, limit: int = 50) -> List[ReputationLeaderboard]:
    """
    获取声誉排行榜
    """
    leaderboard = await reputation_repo.get_reputation_leaderboard(db, trust_level, limit)

    return [ReputationLeaderboard(**item) for item in leaderboard]


async def update_trust_level(db: DatabaseAdapter, user_id: int) -> Optional[UserReputationStatsDetail]:
    """
    更新用户信任等级
    """
    result = await reputation_repo.update_trust_level(db, user_id)
    if result:
        return UserReputationStatsDetail(**result)
    return None
