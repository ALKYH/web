"""
技能服务层
处理技能和技能分类的业务逻辑
"""
from typing import List, Optional
from fastapi import HTTPException, status

from apps.schemas.skills import (
    SkillCategoryCreate, SkillCategoryUpdate, SkillCreate, SkillUpdate,
    SkillCategoryDetail, SkillDetail, SkillListResponse, SkillCategoryListResponse
)
from apps.api.v1.repositories import skills as skills_repo
from libs.database.adapters import DatabaseAdapter


async def create_skill_category(db: DatabaseAdapter, category: SkillCategoryCreate) -> SkillCategoryDetail:
    """
    创建技能分类
    """
    result = await skills_repo.create_skill_category(db, category)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建技能分类失败"
        )

    # 获取完整详情（包含技能列表）
    return await get_skill_category_detail(db, result['id'])


async def get_skill_category_detail(db: DatabaseAdapter, category_id: int) -> SkillCategoryDetail:
    """
    获取技能分类详情
    """
    category = await skills_repo.get_skill_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能分类不存在"
        )

    # 获取分类下的技能
    skills = await skills_repo.get_skills_by_category(db, category_id)

    return SkillCategoryDetail(
        **category,
        skills=[SkillDetail(**skill) for skill in skills],
        skill_count=len(skills)
    )


async def create_skill(db: DatabaseAdapter, skill: SkillCreate) -> SkillDetail:
    """
    创建技能
    """
    # 检查分类是否存在
    category = await skills_repo.get_skill_category_by_id(db, skill.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能分类不存在"
        )

    result = await skills_repo.create_skill(db, skill)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建技能失败"
        )

    return SkillDetail(**result)


async def get_skill_detail(db: DatabaseAdapter, skill_id: int) -> SkillDetail:
    """
    获取技能详情
    """
    skill = await skills_repo.get_skill_by_id(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能不存在"
        )

    return SkillDetail(**skill)


async def get_all_skills(db: DatabaseAdapter, is_active: Optional[bool] = True, skip: int = 0, limit: int = 100) -> SkillListResponse:
    """
    获取所有技能
    """
    skills = await skills_repo.get_all_skills(db, is_active, skip, limit)

    skill_details = [SkillDetail(**skill) for skill in skills]

    return SkillListResponse(
        skills=skill_details,
        total=len(skill_details),
        has_next=len(skill_details) == limit
    )


async def search_skills(db: DatabaseAdapter, query: str, limit: int = 20) -> SkillListResponse:
    """
    搜索技能
    """
    skills = await skills_repo.search_skills(db, query, limit)

    skill_details = [SkillDetail(**skill) for skill in skills]

    return SkillListResponse(
        skills=skill_details,
        total=len(skill_details),
        has_next=False
    )
