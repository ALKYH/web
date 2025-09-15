"""
用户资料相关的服务层
"""
from typing import Dict, Optional
from fastapi import HTTPException, status

from apps.schemas.user import ProfileUpdate
from apps.api.v1.repositories import user as user_repo
from libs.database.adapters import DatabaseAdapter


async def get_user_profile(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取用户完整资料"""
    profile = await user_repo.get_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="用户资料未找到"
        )
    return profile


async def get_user_basic_info(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取用户基本信息"""
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    return user


async def update_user_profile(db: DatabaseAdapter, user_id: int, profile_in: ProfileUpdate) -> Dict:
    """更新用户资料"""
    # 先检查用户是否存在
    existing_user = await user_repo.get_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    # 更新资料
    profile = await user_repo.update_profile(db, user_id, profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到或更新失败"
        )
    
    return profile


async def get_public_profile(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取用户公开资料（隐藏敏感信息）"""
    profile = await user_repo.get_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户资料未找到"
        )
    
    # 隐藏敏感信息
    public_profile = profile.copy()
    public_profile["email"] = None
    public_profile["phone"] = None
    public_profile["birth_date"] = None
    
    return public_profile
