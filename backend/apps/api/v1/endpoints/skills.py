"""
技能中心 - API 路由
包括技能分类、技能管理和用户技能的API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from apps.api.v1.deps import (
    get_current_user,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.skill import (
    SkillCategory, SkillCategoryCreate, SkillCategoryUpdate,
    Skill, SkillCreate, SkillUpdate,
    UserSkill, UserSkillCreate, UserSkillUpdate,
    MentorSkill, MentorSkillCreate, MentorSkillUpdate
)
from apps.schemas.common import GeneralResponse, PaginatedResponse
from apps.api.v1.services import skill as skill_service

router = APIRouter()


# ============ 技能分类管理 ============

@router.get(
    "/categories",
    response_model=GeneralResponse[List[SkillCategory]],
    summary="获取技能分类列表",
    description="获取所有技能分类"
)
async def list_skill_categories(
    db: DatabaseAdapter = Depends(get_database)
):
    """获取技能分类列表"""
    categories = await skill_service.get_skill_categories(db)
    return GeneralResponse(data=categories)


@router.post(
    "/categories",
    response_model=GeneralResponse[SkillCategory],
    status_code=status.HTTP_201_CREATED,
    summary="创建技能分类",
    description="创建新的技能分类"
)
async def create_skill_category(
    category_data: SkillCategoryCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建技能分类

    - **name**: 分类名称
    - **description**: 分类描述（可选）
    """
    category = await skill_service.create_skill_category(db, category_data)
    return GeneralResponse(data=category)


@router.get(
    "/categories/{category_id}",
    response_model=GeneralResponse[SkillCategory],
    summary="获取技能分类详情",
    description="获取指定技能分类的详细信息"
)
async def get_skill_category(
    category_id: UUID,
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取技能分类详情

    - **category_id**: 分类ID
    """
    category = await skill_service.get_skill_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="技能分类不存在")
    return GeneralResponse(data=category)


@router.put(
    "/categories/{category_id}",
    response_model=GeneralResponse[SkillCategory],
    summary="更新技能分类",
    description="更新指定技能分类的信息"
)
async def update_skill_category(
    category_id: UUID,
    category_data: SkillCategoryUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新技能分类

    - **category_id**: 分类ID
    - **name**: 新名称（可选）
    - **description**: 新描述（可选）
    """
    category = await skill_service.update_skill_category(db, category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="技能分类不存在")
    return GeneralResponse(data=category)


@router.delete(
    "/categories/{category_id}",
    response_model=GeneralResponse[dict],
    summary="删除技能分类",
    description="删除指定的技能分类"
)
async def delete_skill_category(
    category_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除技能分类

    - **category_id**: 分类ID
    """
    success = await skill_service.delete_skill_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="技能分类不存在")
    return GeneralResponse(data={"message": "技能分类删除成功"})


# ============ 技能管理 ============

@router.get(
    "",
    response_model=GeneralResponse[List[Skill]],
    summary="获取技能列表",
    description="获取技能列表，支持按分类筛选"
)
async def list_skills(
    category_id: Optional[UUID] = Query(None, description="分类ID筛选"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取技能列表

    - **category_id**: 按分类筛选（可选）
    - **limit**: 返回数量（1-200）
    - **offset**: 偏移量
    """
    skills = await skill_service.get_skills(db, category_id, limit, offset)
    return GeneralResponse(data=skills)


@router.post(
    "",
    response_model=GeneralResponse[Skill],
    status_code=status.HTTP_201_CREATED,
    summary="创建技能",
    description="创建新的技能"
)
async def create_skill(
    skill_data: SkillCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    创建技能

    - **name**: 技能名称
    - **category_id**: 所属分类ID
    """
    skill = await skill_service.create_skill(db, skill_data)
    return GeneralResponse(data=skill)


@router.get(
    "/{skill_id}",
    response_model=GeneralResponse[Skill],
    summary="获取技能详情",
    description="获取指定技能的详细信息"
)
async def get_skill(
    skill_id: UUID,
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取技能详情

    - **skill_id**: 技能ID
    """
    skill = await skill_service.get_skill(db, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    return GeneralResponse(data=skill)


@router.put(
    "/{skill_id}",
    response_model=GeneralResponse[Skill],
    summary="更新技能",
    description="更新指定技能的信息"
)
async def update_skill(
    skill_id: UUID,
    skill_data: SkillUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新技能

    - **skill_id**: 技能ID
    - **name**: 新名称（可选）
    - **category_id**: 新分类ID（可选）
    """
    skill = await skill_service.update_skill(db, skill_id, skill_data)
    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")
    return GeneralResponse(data=skill)


@router.delete(
    "/{skill_id}",
    response_model=GeneralResponse[dict],
    summary="删除技能",
    description="删除指定的技能"
)
async def delete_skill(
    skill_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除技能

    - **skill_id**: 技能ID
    """
    success = await skill_service.delete_skill(db, skill_id)
    if not success:
        raise HTTPException(status_code=404, detail="技能不存在")
    return GeneralResponse(data={"message": "技能删除成功"})


# ============ 用户技能管理 ============

@router.get(
    "/users/{user_id}/skills",
    response_model=GeneralResponse[List[UserSkill]],
    summary="获取用户技能列表",
    description="获取指定用户的所有技能"
)
async def list_user_skills(
    user_id: UUID,
    can_mentor: Optional[bool] = Query(None, description="是否可指导筛选"),
    verified: Optional[bool] = Query(None, description="是否已验证筛选"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取用户技能列表

    - **user_id**: 用户ID
    - **can_mentor**: 是否可指导筛选（可选）
    - **verified**: 是否已验证筛选（可选）
    - **limit**: 返回数量（1-200）
    """
    skills = await skill_service.get_user_skills(db, user_id, can_mentor, verified, limit)
    return GeneralResponse(data=skills)


@router.post(
    "/users/skills",
    response_model=GeneralResponse[UserSkill],
    status_code=status.HTTP_201_CREATED,
    summary="添加用户技能",
    description="为当前用户添加新技能"
)
async def create_user_skill(
    skill_data: UserSkillCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    添加用户技能

    - **skill_id**: 技能ID
    - **proficiency_level**: 熟练度（1-5）
    - **years_experience**: 经验年限
    """
    user_skill = await skill_service.create_user_skill(db, skill_data, current_user.id)
    return GeneralResponse(data=user_skill)


@router.put(
    "/users/skills/{user_skill_id}",
    response_model=GeneralResponse[UserSkill],
    summary="更新用户技能",
    description="更新指定的用户技能信息"
)
async def update_user_skill(
    user_skill_id: UUID,
    skill_data: UserSkillUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新用户技能

    - **user_skill_id**: 用户技能ID
    - **proficiency_level**: 新熟练度（可选）
    - **years_experience**: 新经验年限（可选）
    """
    user_skill = await skill_service.update_user_skill(db, user_skill_id, skill_data, current_user.id)
    if not user_skill:
        raise HTTPException(status_code=404, detail="用户技能不存在")
    return GeneralResponse(data=user_skill)


@router.delete(
    "/users/skills/{user_skill_id}",
    response_model=GeneralResponse[dict],
    summary="删除用户技能",
    description="删除指定的用户技能"
)
async def delete_user_skill(
    user_skill_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除用户技能

    - **user_skill_id**: 用户技能ID
    """
    success = await skill_service.delete_user_skill(db, user_skill_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="用户技能不存在")
    return GeneralResponse(data={"message": "用户技能删除成功"})


# ============ 导师技能管理 ============

@router.get(
    "/mentors/{user_id}/skills",
    response_model=GeneralResponse[List[MentorSkill]],
    summary="获取导师技能列表",
    description="获取指定导师的所有指导技能"
)
async def list_mentor_skills(
    user_id: UUID,
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取导师技能列表

    - **user_id**: 导师用户ID
    - **is_active**: 是否激活筛选（可选）
    """
    skills = await skill_service.get_mentor_skills_by_user(db, user_id, is_active)
    return GeneralResponse(data=skills)


@router.post(
    "/mentors/skills",
    response_model=GeneralResponse[MentorSkill],
    status_code=status.HTTP_201_CREATED,
    summary="添加导师技能",
    description="为当前导师添加指导技能"
)
async def create_mentor_skill(
    skill_data: MentorSkillCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    添加导师技能

    - **user_skill_id**: 关联的用户技能ID
    - **can_mentor**: 是否可提供指导
    - **hourly_rate**: 时薪（可选）
    - **description**: 服务描述（可选）
    """
    mentor_skill = await skill_service.create_mentor_skill(db, skill_data, current_user.id)
    return GeneralResponse(data=mentor_skill)


@router.put(
    "/mentors/skills/{mentor_skill_id}",
    response_model=GeneralResponse[MentorSkill],
    summary="更新导师技能",
    description="更新指定的导师技能信息"
)
async def update_mentor_skill(
    mentor_skill_id: UUID,
    skill_data: MentorSkillUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    更新导师技能

    - **mentor_skill_id**: 导师技能ID
    - **can_mentor**: 是否可提供指导（可选）
    - **hourly_rate**: 新时薪（可选）
    - **description**: 新服务描述（可选）
    - **is_active**: 是否激活（可选）
    """
    mentor_skill = await skill_service.update_mentor_skill(db, mentor_skill_id, skill_data, current_user.id)
    if not mentor_skill:
        raise HTTPException(status_code=404, detail="导师技能不存在")
    return GeneralResponse(data=mentor_skill)


@router.delete(
    "/mentors/skills/{mentor_skill_id}",
    response_model=GeneralResponse[dict],
    summary="删除导师技能",
    description="删除指定的导师技能"
)
async def delete_mentor_skill(
    mentor_skill_id: UUID,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    删除导师技能

    - **mentor_skill_id**: 导师技能ID
    """
    success = await skill_service.delete_mentor_skill(db, mentor_skill_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="导师技能不存在")
    return GeneralResponse(data={"message": "导师技能删除成功"})


# ============ 技能搜索 ============

@router.get(
    "/search",
    response_model=GeneralResponse[List[dict]],
    summary="搜索技能",
    description="根据条件搜索技能和导师"
)
async def search_skills(
    skill_name: Optional[str] = Query(None, description="技能名称关键词"),
    category_id: Optional[UUID] = Query(None, description="分类ID"),
    min_proficiency: Optional[int] = Query(None, ge=1, le=5, description="最低熟练度"),
    can_mentor: Optional[bool] = Query(None, description="是否可指导"),
    verified_only: Optional[bool] = Query(None, description="仅显示已验证"),
    location: Optional[str] = Query(None, description="位置筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    搜索技能和导师

    - **skill_name**: 技能名称关键词
    - **category_id**: 分类ID筛选
    - **min_proficiency**: 最低熟练度（1-5）
    - **can_mentor**: 是否可提供指导
    - **verified_only**: 仅显示已验证技能
    - **location**: 位置筛选
    - **limit**: 返回数量（1-100）
    """
    results = await skill_service.search_user_skills(
        db, skill_name, category_id, min_proficiency, can_mentor,
        verified_only, location, limit
    )
    return GeneralResponse(data=results)
