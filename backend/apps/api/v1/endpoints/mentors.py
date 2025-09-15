"""
指导者相关的 API 路由
包括指导者资料管理、搜索等功能
"""
from fastapi import APIRouter, Depends, status
from typing import List, Optional

from apps.api.v1.deps import (
    get_current_user,
    require_mentor_role,
    AuthenticatedUser,
    get_database
)
from libs.database.adapters import DatabaseAdapter
from apps.schemas.mentor import (
    MentorCreate, MentorUpdate, MentorProfile, MentorPublic
)
from apps.api.v1.services import mentor as mentor_service

router = APIRouter()


@router.post(
    "/profile",
    response_model=MentorProfile,
    summary="注册成为指导者",
    description="用户注册成为指导者"
)
async def create_mentor_profile(
    mentor_data: MentorCreate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """注册成为指导者"""
    return await mentor_service.create_mentor_profile(db, int(current_user.id), mentor_data)


@router.get(
    "/profile",
    response_model=MentorProfile,
    summary="获取指导者资料",
    description="获取当前用户的指导者资料"
)
async def get_mentor_profile(
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """获取指导者资料"""
    return await mentor_service.get_mentor_profile(db, int(current_user.id))


@router.put(
    "/profile",
    response_model=MentorProfile,
    summary="更新指导者资料",
    description="更新当前用户的指导者资料"
)
async def update_mentor_profile(
    mentor_data: MentorUpdate,
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """更新指导者资料"""
    return await mentor_service.update_mentor_profile(db, int(current_user.id), mentor_data)


@router.get(
    "/search",
    response_model=List[MentorPublic],
    summary="搜索指导者",
    description="搜索指导者列表"
)
async def search_mentors(
    search_query: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: DatabaseAdapter = Depends(get_database)
):
    """搜索指导者"""
    mentors = await mentor_service.search_mentors(db, search_query, limit, offset)
    return [MentorPublic(**mentor) for mentor in mentors]


@router.delete(
    "/profile",
    summary="删除指导者资料",
    description="删除当前用户的指导者资料"
)
async def delete_mentor_profile(
    db: DatabaseAdapter = Depends(get_database),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """删除指导者资料"""
    await mentor_service.delete_mentor_profile(db, int(current_user.id))
    return {"message": "指导者资料已删除"}