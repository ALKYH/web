"""
指导者相关的服务层
包括指导者资料管理、搜索等业务逻辑
"""
from typing import List, Dict, Optional
from fastapi import HTTPException, status

from apps.schemas.mentor import MentorProfileCreate, MentorProfileUpdate
from apps.api.v1.repositories import mentor as mentor_repo
from libs.database.adapters import DatabaseAdapter


async def create_mentor_profile(db: DatabaseAdapter, user_id: int, mentor_data: MentorProfileCreate) -> Dict:
    """
    创建指导者资料的业务逻辑
    1. 检查用户是否已经是指导者
    2. 创建指导者资料
    """
    # 1. 检查是否已经是指导者
    existing_mentor = await mentor_repo.get_mentor_profile(db, user_id)
    if existing_mentor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经是指导者了"
        )
    
    # 2. 创建指导者资料
    mentor = await mentor_repo.create_mentor_profile(db, user_id, mentor_data)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建指导者资料失败"
        )
    
    return mentor


async def get_mentor_profile(db: DatabaseAdapter, user_id: int) -> Dict:
    """获取指导者资料"""
    mentor = await mentor_repo.get_mentor_profile(db, user_id)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指导者资料不存在"
        )
    return mentor


async def update_mentor_profile(db: DatabaseAdapter, user_id: int, mentor_data: MentorProfileUpdate) -> Dict:
    """更新指导者资料"""
    mentor = await mentor_repo.update_mentor_profile(db, user_id, mentor_data)
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指导者资料不存在或更新失败"
        )
    return mentor


async def search_mentors(db: DatabaseAdapter, search_query: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict]:
    """搜索指导者"""
    try:
        mentors = await mentor_repo.search_mentors(db, search_query, limit, offset)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索指导者失败: {str(e)}"
        )


async def delete_mentor_profile(db: DatabaseAdapter, user_id: int) -> bool:
    """删除指导者资料"""
    success = await mentor_repo.delete_mentor_profile(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指导者资料不存在或删除失败"
        )
    return success