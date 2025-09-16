"""
技能中心 - 服务层
提供技能分类、技能、用户技能和导师技能的业务逻辑
"""
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from apps.schemas.skill import (
    SkillCategory, SkillCategoryCreate, SkillCategoryUpdate,
    Skill, SkillCreate, SkillUpdate,
    UserSkill, UserSkillCreate, UserSkillUpdate,
    MentorSkill, MentorSkillCreate, MentorSkillUpdate
)
from apps.api.v1.repositories import skill as skill_repo
from libs.database.adapters import DatabaseAdapter


# ============ 技能分类服务 ============

async def get_skill_categories(db: DatabaseAdapter, is_active: Optional[bool] = True, skip: int = 0, limit: int = 50) -> List[SkillCategory]:
    """获取技能分类列表"""
    categories = await skill_repo.get_skill_categories(db)
    return [SkillCategory(**category) for category in categories]


async def get_skill_category_by_id(
    db: DatabaseAdapter,
    category_id: UUID
) -> Optional[SkillCategory]:
    """根据ID获取技能分类"""
    category = await skill_repo.get_skill_category_by_id(db, category_id)
    return SkillCategory(**category) if category else None


async def create_skill_category(
    db: DatabaseAdapter,
    category_data: SkillCategoryCreate
) -> SkillCategory:
    """创建技能分类"""
    result = await skill_repo.create_skill_category(db, category_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建技能分类失败"
        )
    return SkillCategory(**result)


async def update_skill_category(
    db: DatabaseAdapter,
    category_id: UUID,
    category_data: SkillCategoryUpdate
) -> Optional[SkillCategory]:
    """更新技能分类"""
    result = await skill_repo.update_skill_category(db, category_id, category_data)
    return SkillCategory(**result) if result else None


# ============ 技能服务 ============

async def get_skills(
    db: DatabaseAdapter,
    category_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100
) -> List[Skill]:
    """获取技能列表"""
    if category_id:
        skills = await skill_repo.get_skills_by_category(db, category_id, is_active, skip, limit)
        return [Skill(**skill) for skill in skills]
    else:
        skills = await skill_repo.get_all_skills(db, is_active, skip, limit)
        return [Skill(**skill) for skill in skills]


async def get_skill_by_id(db: DatabaseAdapter, skill_id: UUID) -> Optional[Skill]:
    """根据ID获取技能"""
    skill = await skill_repo.get_skill_by_id(db, skill_id)
    return Skill(**skill) if skill else None


async def create_skill(db: DatabaseAdapter, skill_data: SkillCreate) -> Skill:
    """创建技能"""
    # 检查分类是否存在
    category = await skill_repo.get_skill_category_by_id(db, skill_data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="技能分类不存在"
        )

    result = await skill_repo.create_skill(db, skill_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建技能失败"
        )
    return Skill(**result)


async def update_skill(
    db: DatabaseAdapter,
    skill_id: UUID,
    skill_data: SkillUpdate
) -> Optional[Skill]:
    """更新技能"""
    result = await skill_repo.update_skill(db, skill_id, skill_data)
    return Skill(**result) if result else None


async def search_skills(db: DatabaseAdapter, query: str, limit: int = 20) -> List[Skill]:
    """搜索技能"""
    skills = await skill_repo.search_skills(db, query, limit)
    return [Skill(**skill) for skill in skills]


# ============ 用户技能服务 ============

async def get_user_skills(
    db: DatabaseAdapter,
    user_id: UUID,
    can_mentor: Optional[bool] = None,
    verified: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50
) -> List[UserSkill]:
    """获取用户的技能列表"""
    # 注意：当前数据库结构不支持 can_mentor 和 verified 字段
    # 这里使用基础查询，将来需要扩展数据库结构
    skills = await skill_repo.get_user_skills_by_user(db, user_id)
    # 应用过滤器（如果将来支持）
    if can_mentor is not None or verified is not None:
        # 临时实现：只返回所有技能，忽略过滤器
        pass
    return [UserSkill(**skill) for skill in skills[skip:skip + limit]] if limit > 0 else [UserSkill(**skill) for skill in skills[skip:]]


async def get_user_skill_by_id(
    db: DatabaseAdapter,
    user_skill_id: UUID,
    user_id: UUID
) -> Optional[UserSkill]:
    """获取用户的特定技能"""
    skill = await skill_repo.get_user_skill_by_id(db, user_skill_id, user_id)
    return UserSkill(**skill) if skill else None


async def create_user_skill(
    db: DatabaseAdapter,
    user_id: UUID,
    skill_data: UserSkillCreate
) -> UserSkill:
    """为用户添加技能"""
    # 检查是否已经拥有该技能
    existing_skill = await skill_repo.get_user_skill_by_skill_id(
        db, user_id, skill_data.skill_id
    )
    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户已经拥有该技能"
        )

    result = await skill_repo.create_user_skill(db, user_id, skill_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加技能失败"
        )
    return UserSkill(**result)


async def update_user_skill(
    db: DatabaseAdapter,
    user_skill_id: UUID,
    user_id: UUID,
    skill_data: UserSkillUpdate
) -> Optional[UserSkill]:
    """更新用户技能"""
    result = await skill_repo.update_user_skill(
        db, user_skill_id, user_id, skill_data
    )
    return UserSkill(**result) if result else None


async def delete_user_skill(
    db: DatabaseAdapter,
    user_skill_id: UUID,
    user_id: UUID
) -> bool:
    """删除用户技能"""
    return await skill_repo.delete_user_skill(db, user_skill_id, user_id)


async def verify_user_skill(
    db: DatabaseAdapter,
    user_skill_id: UUID,
    verified_by: UUID
) -> UserSkill:
    """验证用户技能"""
    result = await skill_repo.verify_user_skill(db, user_skill_id, verified_by)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证技能失败"
        )
    return UserSkill(**result)


# ============ 导师技能服务 ============

async def get_mentor_skills_by_user(
    db: DatabaseAdapter,
    user_id: UUID
) -> List[MentorSkill]:
    """获取用户的导师技能列表"""
    return await skill_repo.get_mentor_skills_by_user(db, user_id)


async def create_mentor_skill(
    db: DatabaseAdapter,
    user_id: UUID,
    mentor_skill_data: MentorSkillCreate
) -> Optional[MentorSkill]:
    """创建导师技能"""
    # 验证用户是否拥有该技能
    user_skill = await skill_repo.get_user_skill_by_id(
        db, mentor_skill_data.user_skill_id, user_id
    )
    if not user_skill:
        return None

    # 检查是否已经是导师技能
    existing_mentor_skill = await skill_repo.get_mentor_skill_by_user_skill_id(
        db, mentor_skill_data.user_skill_id
    )
    if existing_mentor_skill:
        return None

    return await skill_repo.create_mentor_skill(db, user_id, mentor_skill_data)


async def update_mentor_skill(
    db: DatabaseAdapter,
    mentor_skill_id: UUID,
    user_id: UUID,
    mentor_skill_data: MentorSkillUpdate
) -> Optional[MentorSkill]:
    """更新导师技能"""
    return await skill_repo.update_mentor_skill(
        db, mentor_skill_id, user_id, mentor_skill_data
    )


async def delete_mentor_skill(
    db: DatabaseAdapter,
    mentor_skill_id: UUID,
    user_id: UUID
) -> bool:
    """删除导师技能"""
    return await skill_repo.delete_mentor_skill(db, mentor_skill_id, user_id)
