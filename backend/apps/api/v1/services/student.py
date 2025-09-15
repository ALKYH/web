"""
学生档案相关的业务逻辑服务
"""
from typing import Optional, List, Dict
from fastapi import HTTPException, status

from apps.schemas.student import StudentCreate, StudentUpdate
from apps.api.v1.repositories import student as student_repo
from libs.database.adapters import DatabaseAdapter


async def create_student_profile(db: DatabaseAdapter, user_id: int, profile_in: StudentCreate) -> Dict:
    """
    创建学生档案的核心业务逻辑
    1. 检查用户是否已有档案
    2. 如没有，则创建新档案
    """
    # 1. 检查用户是否已有档案
    existing_profile = await student_repo.get_profile_by_user_id(db, user_id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists for this user.",
        )
    
    # 2. 创建新档案
    profile = await student_repo.create_profile(db, user_id=user_id, profile_in=profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student profile in the database."
        )
        
    return profile


async def get_student_profile_by_user_id(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取指定用户的学生档案"""
    profile = await student_repo.get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile


async def get_student_profile_by_id(db: DatabaseAdapter, profile_id: int) -> Dict:
    """根据档案ID获取学生档案"""
    profile = await student_repo.get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile


async def update_student_profile(db: DatabaseAdapter, user_id: int, profile_in: StudentUpdate) -> Dict:
    """更新指定用户的学生档案"""
    # 确保档案存在才能更新
    existing_profile = await student_repo.get_profile_by_user_id(db, user_id)
    if not existing_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found, cannot update.")

    updated_profile = await student_repo.update_profile(db, user_id=user_id, profile_in=profile_in)
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update student profile in the database."
        )
    return updated_profile


async def get_student_profile_by_id(db: DatabaseAdapter, profile_id: int) -> Dict:
    """根据档案ID获取学生档案"""
    profile = await student_repo.get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return profile


async def search_student_profiles(db: DatabaseAdapter, search_query: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict]:
    """
    搜索学生档案的业务逻辑
    """
    profiles = await student_repo.search_profiles(db, search_query, limit, offset)
    return profiles