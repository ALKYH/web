"""
用户相关的 API 路由
包括用户资料管理等功能
"""
from fastapi import APIRouter, Depends

from apps.schemas.user import UserRead, ProfileUpdate, ProfileRead
from apps.api.v1.deps import AuthenticatedUser
from apps.api.v1.deps import get_current_user, get_database
from apps.api.v1.services import user as user_service
from libs.database.adapters import DatabaseAdapter

router = APIRouter()


@router.get(
    "/me",
    response_model=ProfileRead,
    summary="获取当前用户资料",
    description="获取当前登录用户的完整资料信息"
)
async def read_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取当前用户的完整资料
    
    包括基本信息和扩展资料
    """
    profile = await user_service.get_user_profile(db=db, user_id=int(current_user.id))
    
    return ProfileRead(
        id=profile["id"],
        username=profile["username"],
        email=profile.get("email"),
        role=profile.get("role", "user"),
        is_active=profile.get("is_active", True),
        created_at=profile["created_at"],
        full_name=profile.get("full_name"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
        phone=profile.get("phone"),
        location=profile.get("location"),
        website=profile.get("website"),
        birth_date=profile.get("birth_date")
    )


@router.put(
    "/me",
    response_model=ProfileRead,
    summary="更新当前用户资料",
    description="更新当前登录用户的资料信息"
)
async def update_current_user_profile(
    profile_in: ProfileUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    更新当前用户的资料
    
    可以更新以下信息：
    - full_name: 真实姓名
    - avatar_url: 头像链接
    - bio: 个人简介
    - phone: 联系电话
    - location: 所在地区
    - website: 个人网站
    - birth_date: 生日
    """
    profile = await user_service.update_user_profile(db=db, user_id=int(current_user.id), profile_in=profile_in)
    
    return ProfileRead(
        id=profile["id"],
        username=profile["username"],
        email=profile.get("email"),
        role=profile.get("role", "user"),
        is_active=profile.get("is_active", True),
        created_at=profile["created_at"],
        full_name=profile.get("full_name"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
        phone=profile.get("phone"),
        location=profile.get("location"),
        website=profile.get("website"),
        birth_date=profile.get("birth_date")
    )


@router.get(
    "/me/basic",
    response_model=UserRead,
    summary="获取当前用户基本信息",
    description="获取当前登录用户的基本账户信息"
)
async def read_current_user_basic(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取当前用户的基本信息
    
    仅包括基本的账户信息，不包括扩展资料
    """
    user = await user_service.get_user_basic_info(db=db, user_id=int(current_user.id))
    
    return UserRead(
        id=user["id"],
        username=user["username"],
        email=user.get("email"),
        role=user.get("role", "user"),
        is_active=user.get("is_active", True),
        created_at=user["created_at"]
    )


@router.get(
    "/{user_id}/profile",
    response_model=ProfileRead,
    summary="获取指定用户的公开资料",
    description="获取指定用户的公开资料信息"
)
async def read_user_profile(
    user_id: int,
    db: DatabaseAdapter = Depends(get_database)
):
    """
    获取指定用户的公开资料
    
    - **user_id**: 用户ID
    
    返回该用户的公开资料信息
    """
    profile = await user_service.get_public_profile(db=db, user_id=user_id)
    
    # 返回公开信息（敏感信息已在服务层隐藏）
    return ProfileRead(
        id=profile["id"],
        username=profile["username"],
        email=profile.get("email"),  # 已在服务层设为None
        role=profile.get("role", "user"),
        is_active=profile.get("is_active", True),
        created_at=profile["created_at"],
        full_name=profile.get("full_name"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
        phone=profile.get("phone"),  # 已在服务层设为None
        location=profile.get("location"),
        website=profile.get("website"),
        birth_date=profile.get("birth_date")  # 已在服务层设为None
    )