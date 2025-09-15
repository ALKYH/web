"""
匹配推荐相关的业务逻辑服务
"""
from typing import Optional, Dict, List
from datetime import datetime
from fastapi import HTTPException, status

from apps.schemas.matching import MatchingRequest, MatchingFilter, RecommendationRequest
from apps.api.v1.repositories import matching as matching_repo
from libs.database.adapters import DatabaseAdapter


async def recommend_mentors(db: DatabaseAdapter, user_id: int, request: MatchingRequest) -> Dict:
    """
    基于需求推荐指导者的业务逻辑
    1. 创建匹配请求
    2. 计算匹配分数
    3. 保存匹配结果
    """
    try:
        # 创建匹配请求
        request_id = await matching_repo.create_matching_request(db, user_id, request)
        if not request_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建匹配请求失败"
            )
        
        # 计算匹配分数
        matches = await matching_repo.calculate_match_scores(db, request)
        
        # 保存匹配结果
        await matching_repo.save_matching_result(db, request_id, user_id, matches)
        
        # 构建返回结果
        result = {
            "request_id": request_id,
            "student_id": user_id,
            "total_matches": len(matches),
            "matches": matches[:20],  # 只返回前20个匹配
            "filters_applied": request.model_dump(),
            "created_at": datetime.now()
        }
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推荐匹配失败: {str(e)}"
        )


async def get_filters(db: DatabaseAdapter) -> Dict:
    """
    获取筛选条件的业务逻辑
    """
    try:
        filters = await matching_repo.get_advanced_filters(db)
        return filters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取筛选条件失败: {str(e)}"
        )


async def filter_mentors(db: DatabaseAdapter, filters: MatchingFilter, limit: int = 20, offset: int = 0) -> List[Dict]:
    """
    高级筛选指导者的业务逻辑
    """
    try:
        mentors = await matching_repo.apply_advanced_filters(db, filters, limit, offset)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"筛选指导者失败: {str(e)}"
        )


async def get_matching_history(db: DatabaseAdapter, user_id: int, limit: int = 20) -> List[Dict]:
    """
    获取匹配历史的业务逻辑
    """
    try:
        history = await matching_repo.get_matching_history(db, user_id, limit)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取匹配历史失败: {str(e)}"
        )


async def get_contextual_recommendations(db: DatabaseAdapter, request: RecommendationRequest, user_id: int) -> Dict:
    """
    上下文推荐的业务逻辑
    """
    try:
        recommendations = await matching_repo.get_recommendation_for_context(
            db, request, user_id
        )
        
        result = {
            "recommendations": recommendations,
            "algorithm_version": "v1.0",
            "context": request.context,
            "created_at": datetime.now()
        }
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐失败: {str(e)}"
        )


async def get_popular_mentors(db: DatabaseAdapter, limit: int = 20, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """
    获取热门指导者的业务逻辑
    """
    try:
        mentors = await matching_repo.get_popular_mentors(db, limit, exclude_ids)
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门指导者失败: {str(e)}"
        )


async def get_similar_background_mentors(db: DatabaseAdapter, user_id: int, limit: int = 10, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """
    相似背景推荐的业务逻辑
    """
    try:
        mentors = await matching_repo.get_similar_background_mentors(
            db, user_id, limit, exclude_ids
        )
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相似背景推荐失败: {str(e)}"
        )


async def get_service_related_mentors(db: DatabaseAdapter, service_category: str, limit: int = 10, exclude_ids: Optional[List[int]] = None) -> List[Dict]:
    """
    服务相关推荐的业务逻辑
    """
    try:
        preferences = {"service_category": service_category}
        mentors = await matching_repo.get_service_related_mentors(
            db, preferences, limit, exclude_ids
        )
        return mentors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务相关推荐失败: {str(e)}"
        )