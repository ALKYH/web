"""
用户可用性服务层
处理用户可用性相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import date

from apps.schemas.user_availability import (
    UserAvailabilityCreate, UserAvailabilityUpdate, UserAvailabilityDetail,
    UserAvailabilityListResponse, WeeklyAvailability
)
from apps.api.v1.repositories import user_availability as availability_repo
from libs.database.adapters import DatabaseAdapter


async def set_user_availability(db: DatabaseAdapter, availability: UserAvailabilityCreate) -> UserAvailabilityDetail:
    """
    设置用户可用性
    """
    result = await availability_repo.create_availability(db, availability)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="设置可用性失败"
        )

    return UserAvailabilityDetail(**result)


async def get_user_availability(db: DatabaseAdapter, user_id: int, day_of_week: Optional[int] = None) -> UserAvailabilityListResponse:
    """
    获取用户可用性
    """
    availabilities = await availability_repo.get_user_availability(db, user_id, day_of_week)

    availability_details = [UserAvailabilityDetail(**avail) for avail in availabilities]

    return UserAvailabilityListResponse(
        availabilities=availability_details,
        total=len(availability_details)
    )


async def check_availability(db: DatabaseAdapter, user_id: int, check_date: date, start_time: Optional[str] = None, end_time: Optional[str] = None) -> bool:
    """
    检查用户在指定时间是否可用
    """
    return await availability_repo.check_availability(db, user_id, check_date, start_time, end_time)


async def get_available_users(db: DatabaseAdapter, day_of_week: int, start_time: str, end_time: str) -> List[UserAvailabilityDetail]:
    """
    获取指定时间段内可用的用户
    """
    users = await availability_repo.get_available_users(db, day_of_week, start_time, end_time)

    return [UserAvailabilityDetail(**user) for user in users]
