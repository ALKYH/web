"""
用户中心 - API 路由
包括用户资料管理和认证相关功能
"""
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Optional
from uuid import UUID

from apps.schemas.user import (
    User, UserCreate, UserUpdate, UserLogin,
    Profile, ProfileUpdate
)
from apps.schemas.common import GeneralResponse
from apps.api.v1.deps import (
    AuthenticatedUser, get_current_user, get_database
)
from apps.api.v1.services import user as user_service
from libs.database.adapters import DatabaseAdapter

router = APIRouter()


@router.get(
    "/me",
    response_model=GeneralResponse[User],
    summary="获取当前用户信息",
    description="获取当前登录用户的完整信息"
)
async def read_current_user(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[User]:
    """
    获取当前用户的完整信息
    """
    user = await user_service.get_user_by_id(db=db, user_id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return GeneralResponse(data=user)


@router.put(
    "/me",
    response_model=GeneralResponse[User],
    summary="更新当前用户信息",
    description="更新当前登录用户的基本信息"
)
async def update_current_user(
    user_data: UserUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[User]:
    """
    更新当前用户的基本信息
    """
    updated_user = await user_service.update_user(
        db=db,
        user_id=current_user.id,
        user_data=user_data
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return GeneralResponse(data=updated_user)


@router.get(
    "/profile",
    response_model=GeneralResponse[Profile],
    summary="获取当前用户画像",
    description="获取当前登录用户的完整画像信息"
)
async def read_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Profile]:
    """
    获取当前用户的完整画像信息
    """
    profile = await user_service.get_user_profile(db=db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")

    return GeneralResponse(data=profile)


@router.put(
    "/profile",
    response_model=GeneralResponse[Profile],
    summary="更新当前用户画像",
    description="更新当前登录用户的画像信息"
)
async def update_current_user_profile(
    profile_data: ProfileUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
) -> GeneralResponse[Profile]:
    """
    更新当前用户的画像信息
    """
    updated_profile = await user_service.update_user_profile(
        db=db,
        user_id=current_user.id,
        profile_data=profile_data
    )
    if not updated_profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")

    return GeneralResponse(data=updated_profile)
