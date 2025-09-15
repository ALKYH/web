"""
用户学习需求服务层
处理用户学习需求相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status

from apps.schemas.user_learning_needs import (
    UserLearningNeedCreate, UserLearningNeedUpdate, UserLearningNeedDetail,
    UserLearningNeedListResponse, LearningNeedFilter
)
from apps.api.v1.repositories import user_learning_needs as needs_repo
from libs.database.adapters import DatabaseAdapter


async def create_learning_need(db: DatabaseAdapter, need: UserLearningNeedCreate) -> UserLearningNeedDetail:
    """
    创建学习需求
    """
    result = await needs_repo.create_learning_need(db, need)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建学习需求失败"
        )

    return UserLearningNeedDetail(**result)


async def get_user_learning_needs(db: DatabaseAdapter, user_id: int, is_active: Optional[bool] = None, skip: int = 0, limit: int = 50) -> UserLearningNeedListResponse:
    """
    获取用户学习需求
    """
    needs = await needs_repo.get_user_learning_needs(db, user_id, is_active, skip, limit)

    need_details = [UserLearningNeedDetail(**need) for need in needs]

    return UserLearningNeedListResponse(
        needs=need_details,
        total=len(need_details),
        has_next=len(need_details) == limit
    )


async def update_learning_need(db: DatabaseAdapter, need_id: int, need: UserLearningNeedUpdate, user_id: int) -> UserLearningNeedDetail:
    """
    更新学习需求
    1. 检查权限
    2. 更新需求
    """
    existing_need = await needs_repo.get_learning_need_by_id(db, need_id)
    if not existing_need:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习需求不存在"
        )

    if existing_need['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此学习需求"
        )

    result = await needs_repo.update_learning_need(db, need_id, need)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新学习需求失败"
        )

    return UserLearningNeedDetail(**result)
