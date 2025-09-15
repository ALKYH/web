"""
用户不可用时间段服务层
处理用户不可用时间段相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import date

from apps.schemas.user_unavailable_periods import (
    UserUnavailablePeriodCreate, UserUnavailablePeriodDetail,
    UserUnavailablePeriodListResponse
)
from apps.api.v1.repositories import user_unavailable_periods as periods_repo
from libs.database.adapters import DatabaseAdapter


async def add_unavailable_period(db: DatabaseAdapter, period: UserUnavailablePeriodCreate) -> UserUnavailablePeriodDetail:
    """
    添加不可用时间段
    """
    result = await periods_repo.create_unavailable_period(db, period)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加不可用时间段失败"
        )

    return UserUnavailablePeriodDetail(**result)


async def get_user_unavailable_periods(db: DatabaseAdapter, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, skip: int = 0, limit: int = 50) -> UserUnavailablePeriodListResponse:
    """
    获取用户不可用时间段
    """
    periods = await periods_repo.get_user_unavailable_periods(db, user_id, start_date, end_date, skip, limit)

    period_details = [UserUnavailablePeriodDetail(**period) for period in periods]

    return UserUnavailablePeriodListResponse(
        periods=period_details,
        total=len(period_details),
        has_next=len(period_details) == limit
    )


async def check_conflicting_periods(db: DatabaseAdapter, user_id: int, start_date: date, end_date: date, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[UserUnavailablePeriodDetail]:
    """
    检查冲突的不可用时间段
    """
    conflicts = await periods_repo.get_conflicting_periods(db, user_id, start_date, end_date, start_time, end_time)

    return [UserUnavailablePeriodDetail(**conflict) for conflict in conflicts]
