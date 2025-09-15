"""
用户技能服务层
处理用户技能相关的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status

from apps.schemas.user_skills import (
    UserSkillCreate, UserSkillUpdate, UserSkillDetail, UserSkillListResponse,
    SkillEndorsement
)
from apps.api.v1.repositories import user_skills as user_skills_repo
from libs.database.adapters import DatabaseAdapter


async def add_user_skill(db: DatabaseAdapter, skill: UserSkillCreate) -> UserSkillDetail:
    """
    添加用户技能
    """
    result = await user_skills_repo.create_user_skill(db, skill)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加技能失败"
        )

    return UserSkillDetail(**result)


async def get_user_skills(db: DatabaseAdapter, user_id: int, can_mentor: Optional[bool] = None, verified: Optional[bool] = None, skip: int = 0, limit: int = 50) -> UserSkillListResponse:
    """
    获取用户技能
    """
    skills = await user_skills_repo.get_user_skills(db, user_id, can_mentor, None, verified, skip, limit)

    skill_details = [UserSkillDetail(**skill) for skill in skills]

    return UserSkillListResponse(
        skills=skill_details,
        total=len(skill_details),
        has_next=len(skill_details) == limit
    )


async def verify_user_skill(db: DatabaseAdapter, user_skill_id: int, verified_by: int) -> UserSkillDetail:
    """
    验证用户技能
    """
    result = await user_skills_repo.verify_user_skill(db, user_skill_id, verified_by)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证技能失败"
        )

    return UserSkillDetail(**result)
